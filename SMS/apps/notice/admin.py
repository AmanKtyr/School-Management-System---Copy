from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import Notice, NoticeRecipient, NoticeCategory


class NoticeRecipientInline(admin.TabularInline):
    """Inline admin for notice recipients"""
    model = NoticeRecipient
    extra = 0
    readonly_fields = ('user', 'is_read', 'read_at', 'email_sent', 'sms_sent', 'created_at')
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(NoticeCategory)
class NoticeCategoryAdmin(admin.ModelAdmin):
    """Admin interface for Notice Categories"""
    list_display = ('name', 'description', 'color_display', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    list_editable = ('is_active',)

    def color_display(self, obj):
        return format_html(
            '<span style="background-color: {}; padding: 5px 10px; color: white; border-radius: 3px;">{}</span>',
            obj.color,
            obj.color
        )
    color_display.short_description = 'Color'


@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    """Admin interface for Notices"""
    list_display = (
        'title', 'created_by', 'priority_display', 'status_display',
        'recipient_type', 'total_recipients', 'read_count', 'created_at', 'is_active_display'
    )
    list_filter = (
        'status', 'priority', 'recipient_type', 'is_important',
        'send_email', 'send_sms', 'created_at', 'category'
    )
    search_fields = ('title', 'content', 'created_by__username', 'created_by__first_name', 'created_by__last_name')
    readonly_fields = ('created_at', 'updated_at', 'total_recipients', 'read_count', 'unread_count')

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'content', 'category', 'attachment')
        }),
        ('Notice Settings', {
            'fields': ('priority', 'status', 'is_important')
        }),
        ('Recipients', {
            'fields': ('recipient_type', 'target_class')
        }),
        ('Validity Period', {
            'fields': ('valid_from', 'valid_until')
        }),
        ('Notifications', {
            'fields': ('send_email', 'send_sms')
        }),
        ('Statistics', {
            'fields': ('total_recipients', 'read_count', 'unread_count'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    inlines = [NoticeRecipientInline]

    def save_model(self, request, obj, form, change):
        """Set created_by to current user if creating new notice"""
        if not change:  # Creating new notice
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def priority_display(self, obj):
        colors = {
            'low': '#28a745',
            'medium': '#ffc107',
            'high': '#fd7e14',
            'urgent': '#dc3545'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            colors.get(obj.priority, '#6c757d'),
            obj.get_priority_display()
        )
    priority_display.short_description = 'Priority'

    def status_display(self, obj):
        colors = {
            'draft': '#6c757d',
            'published': '#28a745',
            'archived': '#dc3545'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            colors.get(obj.status, '#6c757d'),
            obj.get_status_display()
        )
    status_display.short_description = 'Status'

    def is_active_display(self, obj):
        if obj.is_active:
            return format_html('<span style="color: green;">✓ Active</span>')
        else:
            return format_html('<span style="color: red;">✗ Inactive</span>')
    is_active_display.short_description = 'Active'

    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        return super().get_queryset(request).select_related('created_by', 'category', 'target_class')


@admin.register(NoticeRecipient)
class NoticeRecipientAdmin(admin.ModelAdmin):
    """Admin interface for Notice Recipients"""
    list_display = (
        'notice_title', 'user_name', 'is_read_display', 'read_at',
        'email_sent_display', 'sms_sent_display', 'created_at'
    )
    list_filter = (
        'is_read', 'email_sent', 'sms_sent', 'created_at',
        'notice__priority', 'notice__status'
    )
    search_fields = (
        'notice__title', 'user__username', 'user__first_name',
        'user__last_name', 'user__email'
    )
    readonly_fields = ('notice', 'user', 'created_at')

    def notice_title(self, obj):
        return obj.notice.title
    notice_title.short_description = 'Notice'

    def user_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    user_name.short_description = 'User'

    def is_read_display(self, obj):
        if obj.is_read:
            return format_html('<span style="color: green;">✓ Read</span>')
        else:
            return format_html('<span style="color: red;">✗ Unread</span>')
    is_read_display.short_description = 'Read Status'

    def email_sent_display(self, obj):
        if obj.email_sent:
            return format_html('<span style="color: green;">✓ Sent</span>')
        else:
            return format_html('<span style="color: gray;">✗ Not Sent</span>')
    email_sent_display.short_description = 'Email'

    def sms_sent_display(self, obj):
        if obj.sms_sent:
            return format_html('<span style="color: green;">✓ Sent</span>')
        else:
            return format_html('<span style="color: gray;">✗ Not Sent</span>')
    sms_sent_display.short_description = 'SMS'

    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        return super().get_queryset(request).select_related('notice', 'user')

    def has_add_permission(self, request):
        """Prevent manual addition of recipients"""
        return False
