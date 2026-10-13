from django.conf import settings
from django.db import models

from core.models import Category


class Goal(models.Model):
    class Timeframe(models.TextChoices):
        WEEKLY = "weekly", "Weekly"
        MONTHLY = "monthly", "Monthly"
        QUARTERLY = "quarterly", "Quarterly"
        YEARLY = "yearly", "Yearly"

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="goals"
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="goals"
    )
    timeframe = models.CharField(max_length=20, choices=Timeframe.choices, default=Timeframe.WEEKLY)
    target_value = models.PositiveIntegerField(default=1)
    current_value = models.PositiveIntegerField(default=0)
    due_date = models.DateField(null=True, blank=True)
    is_achieved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
