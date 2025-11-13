from django.db.models import Q
from .models import Notice, NoticeRecipient


def notice_context(request):
    """
    Context processor to add notice-related data to all templates
    """
    context = {}
    
    if request.user.is_authenticated:
        # Get recent notices for the user
        if request.user.is_superuser:
            # Admin can see all notices
            recent_notices = Notice.objects.select_related('created_by', 'category').order_by('-created_at')[:3]
            user_role = 'admin'
        else:
            # Get notices where user is recipient
            user_notice_ids = NoticeRecipient.objects.filter(
                user=request.user
            ).values_list('notice_id', flat=True)
            
            recent_notices = Notice.objects.filter(
                Q(id__in=user_notice_ids) | Q(recipient_type='all'),
                status='published'
            ).select_related('created_by', 'category').order_by('-created_at')[:3]
            
            # Determine user role
            if hasattr(request.user, 'staff') or request.user.is_staff:
                user_role = 'teacher'
            else:
                user_role = 'student'
        
        # Get unread count
        unread_count = NoticeRecipient.objects.filter(
            user=request.user,
            is_read=False
        ).count()
        
        context.update({
            'recent_notices': recent_notices,
            'unread_count': unread_count,
            'user_role': user_role,
        })
    
    return context
