from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, EmailChangeRequest

class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ['username', 'email', 'univ_email', 'is_staff', 'is_active']
    fieldsets = UserAdmin.fieldsets + (
        ('Academic Info', {'fields': ('stud_id', 'univ_email', 'personal_email', 'backup_email')}),
        ('Profile', {'fields': ('profile_picture', 'tagline', 'bio')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Academic Info', {'fields': ('stud_id', 'univ_email', 'personal_email', 'backup_email')}),
    )

@admin.register(EmailChangeRequest)
class EmailChangeRequestAdmin(admin.ModelAdmin):
    list_display = ['user', 'new_email', 'status', 'created_at', 'reviewed_by']
    list_filter = ['status', 'created_at']
    search_fields = ['user__username', 'new_email']
    readonly_fields = ['created_at', 'reviewed_at']
    actions = ['approve_requests', 'reject_requests']

    def approve_requests(self, request, queryset):
        for req in queryset:
            if req.status == 'pending':
                req.approve(request.user)
        self.message_user(request, f"{queryset.count()} requests approved.")
    approve_requests.short_description = "Approve selected requests"

    def reject_requests(self, request, queryset):
        for req in queryset:
            if req.status == 'pending':
                req.reject(request.user)
        self.message_user(request, f"{queryset.count()} requests rejected.")
    reject_requests.short_description = "Reject selected requests"

admin.site.register(User, CustomUserAdmin)
