from django.conf import settings
from django.db import models

from core.models import Category


class ScheduleEntry(models.Model):
    class Weekday(models.IntegerChoices):
        SATURDAY = 0, "Saturday"
        SUNDAY = 1, "Sunday"
        MONDAY = 2, "Monday"
        TUESDAY = 3, "Tuesday"
        WEDNESDAY = 4, "Wednesday"
        THURSDAY = 5, "Thursday"
        FRIDAY = 6, "Friday"

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="schedule_entries"
    )
    title = models.CharField(max_length=255)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="schedule_entries"
    )
    weekday = models.PositiveSmallIntegerField(choices=Weekday.choices)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_recurring = models.BooleanField(default=True)

    class Meta:
        ordering = ["weekday", "start_time"]

    def __str__(self):
        return f"{self.title} ({self.get_weekday_display()})"


class ScheduleException(models.Model):
    """A one-off override for a specific date — e.g. you skip Sunday's gym
    slot this week, or move it to a different time."""

    entry = models.ForeignKey(ScheduleEntry, on_delete=models.CASCADE, related_name="exceptions")
    date = models.DateField()
    is_cancelled = models.BooleanField(default=False)
    new_start_time = models.TimeField(null=True, blank=True)
    new_end_time = models.TimeField(null=True, blank=True)

    class Meta:
        unique_together = ("entry", "date")
