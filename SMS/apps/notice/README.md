# Notice System for School Management System

A comprehensive notice/announcement system that allows principals and teachers to broadcast notices to students, teachers, and staff members.

## Features

### Core Features
- **Multi-recipient Support**: Send notices to all users, specific groups (students, teachers, staff), specific classes, or individual users
- **Priority Levels**: Low, Medium, High, and Urgent priority levels with visual indicators
- **Notice Categories**: Organize notices with customizable categories (Academic, Events, Holidays, etc.)
- **Status Management**: Draft, Published, and Archived status for notices
- **Rich Content**: Support for detailed notice content with file attachments
- **Validity Period**: Set notice validity with start and end dates
- **Read Tracking**: Track which recipients have read the notices
- **Important Notices**: Mark notices as important with special highlighting

### User Roles & Permissions
- **Admin/Principal**: Full access - create, edit, delete all notices, manage categories
- **Teachers**: Can create and manage their own notices
- **Students**: View notices sent to them, mark as read

### Notification Options
- **Email Notifications**: Optional email alerts for recipients
- **SMS Notifications**: Optional SMS alerts for recipients (framework ready)
- **Dashboard Widgets**: Real-time notice updates on user dashboards

## Installation & Setup

### 1. Database Migration
The notice system has been set up and migrated. The following models are created:
- `Notice`: Main notice model
- `NoticeRecipient`: Tracks recipients and read status
- `NoticeCategory`: Notice categories for organization

### 2. URL Configuration
Notice URLs are integrated at `/notices/`:
- `/notices/` - Notice list
- `/notices/create/` - Create new notice
- `/notices/<id>/` - Notice detail view
- `/notices/<id>/edit/` - Edit notice
- `/notices/quick-create/` - Quick notice creation
- `/notices/my-notices/` - User's personal notices

### 3. Sample Data
Run the following command to create sample notices and categories:
```bash
python manage.py create_sample_notices
```

## Usage Guide

### For Principals/Admins

#### Creating a Notice
1. Navigate to `/notices/create/` or click "Create Notice" button
2. Fill in the notice details:
   - **Title**: Clear, descriptive title
   - **Content**: Detailed notice content
   - **Category**: Select appropriate category (optional)
   - **Priority**: Choose priority level
   - **Recipients**: Select who should receive the notice
   - **Validity**: Set notice validity period (optional)
   - **Options**: Mark as important, enable email/SMS notifications
   - **Attachment**: Upload files if needed

#### Quick Notice
For urgent announcements, use the "Quick Notice" feature:
1. Click "Quick Notice" button
2. Fill in basic details (title, content, recipients, priority)
3. Notice is published immediately

#### Managing Categories
1. Go to `/notices/categories/`
2. Create new categories with custom colors
3. Organize notices by category for better management

### For Teachers

Teachers can:
- Create notices for their classes or all students
- Edit their own notices
- View all notices relevant to them
- Use quick notice for urgent announcements

### For Students

Students can:
- View notices sent to them
- Mark notices as read
- Filter notices by category, priority, etc.
- Access notice attachments

## Technical Details

### Models

#### Notice Model
- Title, content, priority, status
- Recipient configuration (type, target class, individuals)
- Validity period, importance flag
- Email/SMS notification settings
- File attachment support
- Category association

#### NoticeRecipient Model
- Links notices to users
- Tracks read status and timestamps
- Email/SMS delivery status
- Unique constraint on notice-user combination

#### NoticeCategory Model
- Category name, description, color
- Active/inactive status
- Used for organizing notices

### Views
- **ListView**: Paginated notice listing with filtering
- **DetailView**: Full notice display with read tracking
- **CreateView**: Notice creation with recipient management
- **UpdateView**: Notice editing with permission checks
- **DeleteView**: Notice deletion with confirmations
- **Dashboard Views**: Widget-friendly notice summaries

### Templates
- Responsive design with Bootstrap
- Priority-based color coding
- Read/unread status indicators
- Mobile-friendly interface
- Dashboard widgets for integration

### Permissions
- Role-based access control
- Admin: Full access to all notices
- Teachers: Create/edit own notices
- Students: Read-only access to relevant notices

## Integration with Existing Dashboards

### Adding Notice Widget
Include the notice widget in any dashboard template:

```html
{% include 'notice/widgets/notice_widget.html' %}
```

### Context Processor (Optional)
Add to settings.py for global notice context:

```python
TEMPLATES = [
    {
        'OPTIONS': {
            'context_processors': [
                # ... other processors
                'apps.notice.context_processors.notice_context',
            ],
        },
    },
]
```

## Customization

### Styling
- Modify `apps/notice/templates/notice/base.html` for custom CSS
- Priority colors can be customized in the CSS
- Category colors are configurable per category

### Recipient Logic
- Extend `create_recipients()` method in views for custom recipient logic
- Modify user role detection in `get_user_role()` function

### Notifications
- Email/SMS notification framework is ready
- Implement actual sending logic in the views
- Extend NoticeRecipient model for delivery tracking

## API Endpoints

### AJAX Endpoints
- `POST /notices/<id>/mark-read/` - Mark notice as read
- Returns JSON response for frontend integration

## Future Enhancements

1. **Real-time Notifications**: WebSocket integration for live updates
2. **Mobile App API**: REST API for mobile applications
3. **Advanced Filtering**: More sophisticated filtering options
4. **Bulk Operations**: Bulk notice management
5. **Analytics**: Notice engagement analytics
6. **Templates**: Pre-defined notice templates
7. **Approval Workflow**: Multi-level approval for notices
8. **Scheduled Publishing**: Schedule notices for future publication

## Troubleshooting

### Common Issues

1. **Migration Errors**: Ensure all dependencies are migrated first
2. **Permission Denied**: Check user roles and permissions
3. **File Upload Issues**: Verify MEDIA_ROOT and MEDIA_URL settings
4. **Email/SMS Not Working**: Implement actual notification sending logic

### Debug Mode
Enable Django debug mode to see detailed error messages during development.

## Support

For issues or feature requests, refer to the main project documentation or contact the development team.

---

**Note**: This notice system is designed to be flexible and extensible. Customize it according to your school's specific requirements.
