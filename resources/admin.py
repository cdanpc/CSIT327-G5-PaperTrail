from django.contrib import admin
from .models import Resource, Tag, Bookmark, Rating, Comment, Like


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']
    ordering = ['name']


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ['title', 'resource_type', 'uploader', 'verification_status', 'created_at']
    list_filter = ['resource_type', 'verification_status', 'created_at']
    search_fields = ['title', 'description', 'uploader__username']
    filter_horizontal = ['tags']
    readonly_fields = ['created_at', 'updated_at', 'verified_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'resource_type', 'uploader')
        }),
        ('Files & Links', {
            'fields': ('file', 'external_url')
        }),
        ('Categorization', {
            'fields': ('tags',)
        }),
        ('Verification', {
            'fields': ('verification_status', 'verification_by', 'verified_at', 'rejection_reason')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ['user', 'resource', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'resource__title']


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ['user', 'resource', 'stars', 'created_at']
    list_filter = ['stars', 'created_at']
    search_fields = ['user__username', 'resource__title']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'resource', 'text_preview', 'parent_comment', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'resource__title', 'text']
    raw_id_fields = ['parent_comment']
    
    def text_preview(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    text_preview.short_description = 'Comment Preview'


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'resource', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'resource__title']
