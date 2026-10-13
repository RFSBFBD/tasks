"""
Clerk <-> Django bridge.

Clerk owns sign-up / sign-in / sessions on the frontend. Every request that
hits this backend carries a Clerk session JWT in the Authorization header
(e.g. "Authorization: Bearer <token>"). This class verifies that token
against Clerk's public JWKS (no secret key needed for verification — the
secret key is only used server-side for other Clerk Backend API calls, if
you ever add them) and maps the Clerk user to a local Django auth.User via
core.models.UserProfile.

No password or Clerk secret is ever stored here.
"""
import time

import jwt
import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from core.models import UserProfile

User = get_user_model()

_jwks_cache = {"keys": None, "fetched_at": 0}
_JWKS_CACHE_SECONDS = 60 * 60  # re-fetch at most once an hour


def _get_jwks():
    now = time.time()
    if _jwks_cache["keys"] is None or (now - _jwks_cache["fetched_at"]) > _JWKS_CACHE_SECONDS:
        if not settings.CLERK_JWKS_URL:
            raise AuthenticationFailed("CLERK_JWKS_URL is not configured.")
        resp = requests.get(settings.CLERK_JWKS_URL, timeout=5)
        resp.raise_for_status()
        _jwks_cache["keys"] = resp.json()["keys"]
        _jwks_cache["fetched_at"] = now
    return _jwks_cache["keys"]


def _get_signing_key(token):
    header = jwt.get_unverified_header(token)
    kid = header.get("kid")
    for key in _get_jwks():
        if key.get("kid") == kid:
            return jwt.algorithms.RSAAlgorithm.from_jwk(key)
    # JWKS may have rotated — force a refresh once and retry.
    _jwks_cache["keys"] = None
    for key in _get_jwks():
        if key.get("kid") == kid:
            return jwt.algorithms.RSAAlgorithm.from_jwk(key)
    raise AuthenticationFailed("No matching Clerk signing key found for this token.")


class ClerkAuthentication(BaseAuthentication):
    """DRF authentication backend that trusts a verified Clerk session token."""

    keyword = "Bearer"

    def authenticate(self, request):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith(f"{self.keyword} "):
            return None  # let DRF fall through to "not authenticated"

        token = auth_header.split(" ", 1)[1].strip()
        if not token:
            return None

        try:
            signing_key = _get_signing_key(token)
            payload = jwt.decode(
                token,
                signing_key,
                algorithms=["RS256"],
                issuer=settings.CLERK_ISSUER or None,
                options={"verify_aud": False},
            )
        except jwt.ExpiredSignatureError as exc:
            raise AuthenticationFailed("Clerk session token has expired.") from exc
        except jwt.PyJWTError as exc:
            raise AuthenticationFailed(f"Invalid Clerk session token: {exc}") from exc

        clerk_user_id = payload.get("sub")
        if not clerk_user_id:
            raise AuthenticationFailed("Clerk token missing 'sub' claim.")

        profile, _ = UserProfile.objects.get_or_create(
            clerk_user_id=clerk_user_id,
            defaults={
                "user": User.objects.create_user(
                    username=clerk_user_id, password=None
                )
            },
        )
        return (profile.user, token)
