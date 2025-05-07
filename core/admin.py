# admin.py
from django.contrib import admin
from .models import Blog


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'date_posted', 'slug')
    prepopulated_fields = {'slug': ('title',)}

