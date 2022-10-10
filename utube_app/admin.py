from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

class CustomUserAdmin(UserAdmin):
    list_display = (
        'username', 'email', 'first_name', 'last_name', 'is_staff',
        'phone'
        )

    fieldsets = (
        (None, {
            'fields': ('username', 'password')
        }),
        ('Personal info', {
            'fields': ('first_name', 'last_name', 'email', 'phone')
        }),
        ('Permissions', {
            'fields': (
                'is_active', 'is_staff', 'is_superuser',
                'groups', 'user_permissions'
                )
        }),
        ('Important dates', {
            'fields': ('last_login', 'date_joined')
        })
    )

    add_fieldsets = (
        (None, {
            'fields': ('username', 'password1', 'password2')
        }),
        ('Personal info', {
            'fields': ('first_name', 'last_name', 'email', 'phone')
        }),
        ('Permissions', {
            'fields': (
                'is_active', 'is_staff', 'is_superuser',
                'groups', 'user_permissions'
                )
        }),
        ('Important dates', {
            'fields': ('last_login', 'date_joined')
        })
    )

class AuthorAdmin(admin.ModelAdmin):
    list_display = ['id', 'identity', 'is_banned']

class VideoAdmin(admin.ModelAdmin):
    list_display = ['id', 'author', 'time_creation', 'title', 'description', 'hashtags', 'file']
    list_filter = ['author', 'time_creation', 'title', 'description', 'hashtags']
    search_fields = ('title',  'hashtags')

class CommentAdmin(admin.ModelAdmin):
    model = Comment

class LikeAdmin(admin.ModelAdmin):
    model = Like


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Author, AuthorAdmin)
admin.site.register(Video, VideoAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Like, LikeAdmin)
admin.site.register(Subscription)