from django.contrib import admin
from .models import (
    AcademicSession, AcademicTerm, SiteConfig, StudentClass, Subject,
    CollegeProfile, FeeSettings, FeeStructure, Section, ClassTeacher,
    ClassSubject, Backup, AutomatedBackupSettings
)

# Register your models here.
admin.site.register(AcademicSession)
admin.site.register(AcademicTerm)
admin.site.register(SiteConfig)
admin.site.register(StudentClass)
admin.site.register(Subject)
admin.site.register(CollegeProfile)
admin.site.register(FeeSettings)
admin.site.register(FeeStructure)
admin.site.register(Section)
admin.site.register(ClassTeacher)
admin.site.register(ClassSubject)

# Register Backup models
@admin.register(Backup)
class BackupAdmin(admin.ModelAdmin):
    list_display = ('name', 'backup_type', 'format', 'size', 'created_at', 'created_by', 'is_encrypted')
    list_filter = ('backup_type', 'format', 'is_encrypted', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('size', 'size_bytes', 'created_at')
    date_hierarchy = 'created_at'

@admin.register(AutomatedBackupSettings)
class AutomatedBackupSettingsAdmin(admin.ModelAdmin):
    list_display = ('enabled', 'frequency', 'backup_time', 'day_of_week', 'backup_type', 'last_backup', 'next_backup')
    list_filter = ('enabled', 'frequency', 'backup_type')
    readonly_fields = ('last_backup', 'next_backup')
