from django.contrib import admin

from projects.models import Project, ProjectMilestone

admin.site.register(Project)
admin.site.register(ProjectMilestone)
