from django.conf import settings
from django.db import models


class UserProfile(models.Model):
    """Maps a Clerk user (clerk_user_id, the JWT 'sub' claim) to a local
    Django auth.User row, so every other model can keep using a normal
    ForeignKey(User) and normal row-level ownership checks."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    clerk_user_id = models.CharField(max_length=255, unique=True, db_index=True)
    display_name = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.display_name or self.clerk_user_id


class Category(models.Model):
    """Shared category/tag used by tasks and goals (e.g. University, Gym,
    Quran, Freelance, AI Educational Assistant)."""

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="categories"
    )
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=20, default="#6366F1")

    class Meta:
        unique_together = ("owner", "name")

    def __str__(self):
        return self.name
