import os
import json
import shutil
import zipfile
import tempfile
import subprocess
from datetime import datetime
from django.conf import settings
from django.core.management import call_command
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Backup, AutomatedBackupSettings

User = get_user_model()

def get_backup_dir():
    """Get or create the backup directory"""
    backup_dir = os.path.join(settings.BASE_DIR, 'backups')
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    return backup_dir

def get_media_dir():
    """Get the media directory"""
    return settings.MEDIA_ROOT

def get_database_path():
    """Get the database path for SQLite"""
    if 'sqlite3' in settings.DATABASES['default']['ENGINE']:
        return settings.DATABASES['default']['NAME']
    return None

def format_size(size_bytes):
    """Format file size in bytes to human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"

def create_database_backup(output_file=None):
    """Create a backup of the database"""
    if output_file is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = os.path.join(get_backup_dir(), f'db_backup_{timestamp}.json')
    
    # Use Django's dumpdata command to create a JSON dump of the database
    with open(output_file, 'w') as f:
        call_command('dumpdata', exclude=['contenttypes', 'auth.permission'], indent=2, stdout=f)
    
    return output_file

def create_sql_backup(output_file=None):
    """Create a SQL dump of the database (for SQLite)"""
    db_path = get_database_path()
    if not db_path or not os.path.exists(db_path):
        raise ValueError("Database file not found")
    
    if output_file is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = os.path.join(get_backup_dir(), f'db_backup_{timestamp}.sql')
    
    # For SQLite, we can just copy the database file
    shutil.copy2(db_path, output_file)
    
    return output_file

def create_media_backup(output_file=None):
    """Create a backup of media files"""
    media_dir = get_media_dir()
    if not os.path.exists(media_dir):
        raise ValueError("Media directory not found")
    
    if output_file is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = os.path.join(get_backup_dir(), f'media_backup_{timestamp}.zip')
    
    # Create a ZIP archive of the media directory
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(media_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, os.path.dirname(media_dir))
                zipf.write(file_path, arcname)
    
    return output_file

def create_settings_backup(output_file=None):
    """Create a backup of settings (SiteConfig, CollegeProfile, etc.)"""
    if output_file is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = os.path.join(get_backup_dir(), f'settings_backup_{timestamp}.json')
    
    # Use Django's dumpdata command to create a JSON dump of settings-related models
    with open(output_file, 'w') as f:
        call_command(
            'dumpdata', 
            'corecode.SiteConfig', 
            'corecode.CollegeProfile',
            'corecode.AcademicSession',
            'corecode.AcademicTerm',
            indent=2, 
            stdout=f
        )
    
    return output_file

def create_custom_backup(components, output_file=None, user=None, backup_name=None, encrypt=False, password=None):
    """Create a custom backup with selected components"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_name = backup_name or f'custom_backup_{timestamp}'
    
    if output_file is None:
        output_file = os.path.join(get_backup_dir(), f'{backup_name}.zip')
    
    # Create a temporary directory for the backup components
    with tempfile.TemporaryDirectory() as temp_dir:
        backup_files = {}
        
        # Backup database if selected
        if 'database' in components:
            db_file = os.path.join(temp_dir, 'database.json')
            create_database_backup(db_file)
            backup_files['database'] = db_file
        
        # Backup media if selected
        if 'media' in components:
            media_file = os.path.join(temp_dir, 'media.zip')
            create_media_backup(media_file)
            backup_files['media'] = media_file
        
        # Backup settings if selected
        if 'settings' in components:
            settings_file = os.path.join(temp_dir, 'settings.json')
            create_settings_backup(settings_file)
            backup_files['settings'] = settings_file
        
        # Backup specific apps if selected
        app_components = {
            'students': ['students'],
            'staff': ['staffs', 'NonTeachingStaffs'],
            'classes': ['corecode.StudentClass', 'corecode.Section', 'corecode.ClassTeacher', 'corecode.Subject', 'corecode.ClassSubject'],
            'results': ['exams'],
            'attendance': ['attendance'],
            'fees': ['fees'],
        }
        
        for component, apps in app_components.items():
            if component in components:
                component_file = os.path.join(temp_dir, f'{component}.json')
                with open(component_file, 'w') as f:
                    call_command('dumpdata', *apps, indent=2, stdout=f)
                backup_files[component] = component_file
        
        # Create a manifest file with backup information
        manifest = {
            'name': backup_name,
            'timestamp': timestamp,
            'components': components,
            'created_by': user.username if user else 'system',
            'encrypted': encrypt,
        }
        
        manifest_file = os.path.join(temp_dir, 'manifest.json')
        with open(manifest_file, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        # Create the ZIP archive
        with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add the manifest
            zipf.write(manifest_file, 'manifest.json')
            
            # Add all backup components
            for component, file_path in backup_files.items():
                zipf.write(file_path, f'{component}{os.path.splitext(file_path)[1]}')
    
    # Encrypt the ZIP file if requested
    if encrypt and password:
        # This is a placeholder for encryption - in a real implementation,
        # you would use a proper encryption library
        encrypted_file = f"{output_file}.encrypted"
        # For now, we'll just rename the file to simulate encryption
        os.rename(output_file, encrypted_file)
        output_file = encrypted_file
    
    # Get the file size
    file_size_bytes = os.path.getsize(output_file)
    file_size = format_size(file_size_bytes)
    
    # Create a backup record in the database
    backup = Backup.objects.create(
        name=backup_name,
        file_path=output_file,
        backup_type='custom' if len(components) > 1 else components[0],
        format='zip',
        size=file_size,
        size_bytes=file_size_bytes,
        created_by=user,
        is_encrypted=encrypt,
        description=f"Custom backup with components: {', '.join(components)}",
        includes_students='students' in components,
        includes_staff='staff' in components,
        includes_classes='classes' in components,
        includes_results='results' in components,
        includes_attendance='attendance' in components,
        includes_fees='fees' in components,
        includes_settings='settings' in components,
    )
    
    return backup

def create_full_backup(output_file=None, user=None, backup_name=None, encrypt=False, password=None):
    """Create a full backup of the system"""
    components = ['database', 'media', 'settings', 'students', 'staff', 'classes', 'results', 'attendance', 'fees']
    backup_name = backup_name or f'full_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
    
    return create_custom_backup(
        components=components,
        output_file=output_file,
        user=user,
        backup_name=backup_name,
        encrypt=encrypt,
        password=password
    )

def restore_database(backup_file):
    """Restore database from a backup file"""
    # Check if the file exists
    if not os.path.exists(backup_file):
        raise ValueError(f"Backup file not found: {backup_file}")
    
    # Check the file extension
    ext = os.path.splitext(backup_file)[1].lower()
    
    if ext == '.json':
        # JSON format - use loaddata
        call_command('loaddata', backup_file)
    elif ext == '.sql':
        # SQL format - for SQLite, we can replace the database file
        db_path = get_database_path()
        if not db_path:
            raise ValueError("Database path not found")
        
        # Create a backup of the current database
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = f"{db_path}.{timestamp}.bak"
        shutil.copy2(db_path, backup_path)
        
        # Replace the database file
        shutil.copy2(backup_file, db_path)
    else:
        raise ValueError(f"Unsupported backup format: {ext}")
    
    return True

def restore_media(backup_file):
    """Restore media files from a backup file"""
    # Check if the file exists
    if not os.path.exists(backup_file):
        raise ValueError(f"Backup file not found: {backup_file}")
    
    # Check if it's a ZIP file
    if not zipfile.is_zipfile(backup_file):
        raise ValueError(f"Not a valid ZIP file: {backup_file}")
    
    media_dir = get_media_dir()
    
    # Create a backup of the current media directory
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = f"{media_dir}.{timestamp}.bak"
    if os.path.exists(media_dir):
        shutil.copytree(media_dir, backup_dir)
    
    # Extract the ZIP file to the media directory
    with zipfile.ZipFile(backup_file, 'r') as zipf:
        zipf.extractall(os.path.dirname(media_dir))
    
    return True

def restore_from_backup(backup_id, components=None, user=None, backup_before_restore=True):
    """Restore the system from a backup"""
    try:
        backup = Backup.objects.get(id=backup_id)
    except Backup.DoesNotExist:
        raise ValueError(f"Backup with ID {backup_id} not found")
    
    # Check if the backup file exists
    if not os.path.exists(backup.file_path):
        raise ValueError(f"Backup file not found: {backup.file_path}")
    
    # Create a safety backup if requested
    if backup_before_restore:
        safety_backup = create_full_backup(
            backup_name=f"pre_restore_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            user=user
        )
    
    # For full backups or if no specific components are selected
    if backup.backup_type == 'full' or not components:
        # Extract the backup to a temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            with zipfile.ZipFile(backup.file_path, 'r') as zipf:
                zipf.extractall(temp_dir)
            
            # Check for manifest
            manifest_path = os.path.join(temp_dir, 'manifest.json')
            if os.path.exists(manifest_path):
                with open(manifest_path, 'r') as f:
                    manifest = json.load(f)
                
                # Restore database if it exists
                db_file = os.path.join(temp_dir, 'database.json')
                if os.path.exists(db_file):
                    restore_database(db_file)
                
                # Restore media if it exists
                media_file = os.path.join(temp_dir, 'media.zip')
                if os.path.exists(media_file):
                    restore_media(media_file)
                
                # Restore settings if they exist
                settings_file = os.path.join(temp_dir, 'settings.json')
                if os.path.exists(settings_file):
                    call_command('loaddata', settings_file)
                
                # Restore other components if they exist
                for component in ['students', 'staff', 'classes', 'results', 'attendance', 'fees']:
                    component_file = os.path.join(temp_dir, f'{component}.json')
                    if os.path.exists(component_file):
                        call_command('loaddata', component_file)
            else:
                # No manifest, assume it's a simple database backup
                if backup.format == 'json':
                    restore_database(backup.file_path)
                elif backup.format == 'zip':
                    # Assume it's a media backup
                    restore_media(backup.file_path)
    else:
        # Selective restore
        with tempfile.TemporaryDirectory() as temp_dir:
            with zipfile.ZipFile(backup.file_path, 'r') as zipf:
                zipf.extractall(temp_dir)
            
            # Check for manifest
            manifest_path = os.path.join(temp_dir, 'manifest.json')
            if os.path.exists(manifest_path):
                with open(manifest_path, 'r') as f:
                    manifest = json.load(f)
                
                # Restore selected components
                component_map = {
                    'database': 'database.json',
                    'media': 'media.zip',
                    'settings': 'settings.json',
                    'students': 'students.json',
                    'staff': 'staff.json',
                    'classes': 'classes.json',
                    'results': 'results.json',
                    'attendance': 'attendance.json',
                    'fees': 'fees.json',
                }
                
                for component in components:
                    if component in component_map:
                        component_file = os.path.join(temp_dir, component_map[component])
                        if os.path.exists(component_file):
                            if component == 'database':
                                restore_database(component_file)
                            elif component == 'media':
                                restore_media(component_file)
                            else:
                                call_command('loaddata', component_file)
    
    return True

def run_automated_backup():
    """Run automated backup based on settings"""
    try:
        settings = AutomatedBackupSettings.objects.first()
        if not settings or not settings.enabled:
            return False
        
        # Check if it's time to run the backup
        now = timezone.now()
        if not settings.next_backup or now >= settings.next_backup:
            # Create the backup
            if settings.backup_type == 'full':
                backup = create_full_backup(
                    backup_name=f"automated_full_backup_{now.strftime('%Y%m%d_%H%M%S')}"
                )
            elif settings.backup_type == 'database':
                backup = create_custom_backup(
                    components=['database'],
                    backup_name=f"automated_db_backup_{now.strftime('%Y%m%d_%H%M%S')}"
                )
            elif settings.backup_type == 'incremental':
                # For incremental backups, we need to find the last full backup
                # and only backup changes since then
                # This is a simplified version - a real implementation would be more complex
                backup = create_full_backup(
                    backup_name=f"automated_incremental_backup_{now.strftime('%Y%m%d_%H%M%S')}"
                )
            
            # Update the last backup time
            settings.last_backup = now
            
            # Calculate the next backup time
            settings.calculate_next_backup()
            settings.save()
            
            # Apply retention policy
            if settings.retention_policy != 'all':
                max_backups = int(settings.retention_policy)
                old_backups = Backup.objects.filter(
                    name__startswith='automated_'
                ).order_by('-created_at')[max_backups:]
                
                for old_backup in old_backups:
                    old_backup.delete()  # This will also delete the file
            
            # Send notification if enabled
            if settings.notify_on_backup:
                # This is a placeholder for email notification
                # In a real implementation, you would send an email here
                pass
            
            return backup
        
        return False
    except Exception as e:
        # Log the error
        print(f"Error in automated backup: {e}")
        return False
