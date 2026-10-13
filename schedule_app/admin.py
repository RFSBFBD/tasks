from django.contrib import admin

from schedule_app.models import ScheduleEntry, ScheduleException

admin.site.register(ScheduleEntry)
admin.site.register(ScheduleException)
