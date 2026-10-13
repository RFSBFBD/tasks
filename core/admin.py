from django.contrib import admin

from core.models import Category, UserProfile

admin.site.register(UserProfile)
admin.site.register(Category)
