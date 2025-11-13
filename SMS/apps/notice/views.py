from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden, Http404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Q, Count
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.paginator import Paginator
from django.db import transaction

from .models import Notice, NoticeRecipient, NoticeCategory
from .forms import NoticeForm, NoticeCategoryForm, NoticeFilterForm, QuickNoticeForm
from apps.students.models import Student
from apps.staffs.models import Staff
from apps.corecode.models import StudentClass


def get_user_role(user):
    """Determine user role based on user attributes and related models"""
    if user.is_superuser:
        return 'admin'

    # Check if user is a staff member
    try:
        staff = Staff.objects.get(user=user)
        return 'teacher'
    except Staff.DoesNotExist:
        pass

    # Check if user is a student
    try:
        # Assuming students have user accounts (you may need to adjust this)
        student = Student.objects.filter(fullname__icontains=user.get_full_name()).first()
        if student:
            return 'student'
    except:
        pass

    return 'other'


class NoticeListView(LoginRequiredMixin, ListView):
    """List view for notices with filtering"""
    model = Notice
    template_name = 'notice/notice_list.html'
    context_object_name = 'notices'
    paginate_by = 10

    def get_queryset(self):
        queryset = Notice.objects.select_related('created_by', 'category', 'target_class')

        # Filter based on user role
        user_role = get_user_role(self.request.user)

        if user_role != 'admin':
            # Non-admin users can only see published notices
            queryset = queryset.filter(status='published')

            # Filter notices relevant to the user
            user_notices = NoticeRecipient.objects.filter(
                user=self.request.user
            ).values_list('notice_id', flat=True)

            queryset = queryset.filter(
                Q(id__in=user_notices) |
                Q(recipient_type='all')
            )

        # Apply filters from form
        form = NoticeFilterForm(self.request.GET)
        if form.is_valid():
            if form.cleaned_data['search']:
                search_term = form.cleaned_data['search']
                queryset = queryset.filter(
                    Q(title__icontains=search_term) |
                    Q(content__icontains=search_term)
                )

            if form.cleaned_data['category']:
                queryset = queryset.filter(category=form.cleaned_data['category'])

            if form.cleaned_data['priority']:
                queryset = queryset.filter(priority=form.cleaned_data['priority'])

            if form.cleaned_data['status']:
                queryset = queryset.filter(status=form.cleaned_data['status'])

            if form.cleaned_data['recipient_type']:
                queryset = queryset.filter(recipient_type=form.cleaned_data['recipient_type'])

            if form.cleaned_data['created_by']:
                queryset = queryset.filter(created_by=form.cleaned_data['created_by'])

            if form.cleaned_data['is_important']:
                queryset = queryset.filter(is_important=True)

        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = NoticeFilterForm(self.request.GET)
        context['user_role'] = get_user_role(self.request.user)

        # Get unread notice count for current user
        context['unread_count'] = NoticeRecipient.objects.filter(
            user=self.request.user,
            is_read=False
        ).count()

        return context


class NoticeDetailView(LoginRequiredMixin, DetailView):
    """Detail view for individual notice"""
    model = Notice
    template_name = 'notice/notice_detail.html'
    context_object_name = 'notice'

    def get_object(self, queryset=None):
        notice = super().get_object(queryset)

        # Check if user has permission to view this notice
        user_role = get_user_role(self.request.user)

        if user_role != 'admin':
            # Check if notice is published and user is a recipient
            if notice.status != 'published':
                raise Http404("Notice not found")

            # Check if user is a recipient
            is_recipient = NoticeRecipient.objects.filter(
                notice=notice,
                user=self.request.user
            ).exists()

            if not is_recipient and notice.recipient_type != 'all':
                raise Http404("Notice not found")

        # Mark as read if user is a recipient
        try:
            recipient = NoticeRecipient.objects.get(notice=notice, user=self.request.user)
            recipient.mark_as_read()
        except NoticeRecipient.DoesNotExist:
            pass

        return notice

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_role'] = get_user_role(self.request.user)

        # Get recipient info for current user
        try:
            context['recipient_info'] = NoticeRecipient.objects.get(
                notice=self.object,
                user=self.request.user
            )
        except NoticeRecipient.DoesNotExist:
            context['recipient_info'] = None

        return context


class NoticeCreateView(LoginRequiredMixin, CreateView):
    """Create view for notices - only for admin and teachers"""
    model = Notice
    form_class = NoticeForm
    template_name = 'notice/notice_form.html'
    success_url = reverse_lazy('notice:list')

    def dispatch(self, request, *args, **kwargs):
        user_role = get_user_role(request.user)
        if user_role not in ['admin', 'teacher']:
            messages.error(request, "You don't have permission to create notices.")
            return redirect('notice:list')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.created_by = self.request.user

        with transaction.atomic():
            response = super().form_valid(form)

            # Create recipients based on recipient type
            self.create_recipients(self.object, form.cleaned_data)

            messages.success(self.request, f"Notice '{self.object.title}' created successfully!")
            return response

    def create_recipients(self, notice, cleaned_data):
        """Create NoticeRecipient objects based on recipient type"""
        recipients = []

        if notice.recipient_type == 'all':
            # All active users
            users = User.objects.filter(is_active=True)
            recipients = [NoticeRecipient(notice=notice, user=user) for user in users]

        elif notice.recipient_type == 'students':
            # All students (assuming students have user accounts)
            student_users = User.objects.filter(
                is_active=True,
                is_staff=False,
                is_superuser=False
            )
            recipients = [NoticeRecipient(notice=notice, user=user) for user in student_users]

        elif notice.recipient_type == 'teachers':
            # All teachers/staff
            staff_users = Staff.objects.filter(
                current_status='active',
                user__isnull=False
            ).values_list('user', flat=True)
            users = User.objects.filter(id__in=staff_users)
            recipients = [NoticeRecipient(notice=notice, user=user) for user in users]

        elif notice.recipient_type == 'staff':
            # All staff members
            staff_users = Staff.objects.filter(
                current_status='active',
                user__isnull=False
            ).values_list('user', flat=True)
            users = User.objects.filter(id__in=staff_users)
            recipients = [NoticeRecipient(notice=notice, user=user) for user in users]

        elif notice.recipient_type == 'class' and notice.target_class:
            # Students in specific class
            students = Student.objects.filter(
                current_class=notice.target_class,
                current_status='active'
            )
            # You may need to adjust this based on how students are linked to users
            student_users = []
            for student in students:
                # Try to find user by name or create logic to link students to users
                user = User.objects.filter(
                    Q(first_name__icontains=student.fullname.split()[0]) |
                    Q(username__icontains=student.registration_number)
                ).first()
                if user:
                    student_users.append(user)

            recipients = [NoticeRecipient(notice=notice, user=user) for user in student_users]

        elif notice.recipient_type == 'individual':
            # Individual users selected in form
            individual_users = cleaned_data.get('individual_recipients', [])
            recipients = [NoticeRecipient(notice=notice, user=user) for user in individual_users]

        # Bulk create recipients
        if recipients:
            NoticeRecipient.objects.bulk_create(recipients)


class NoticeUpdateView(LoginRequiredMixin, UpdateView):
    """Update view for notices - only for admin and notice creator"""
    model = Notice
    form_class = NoticeForm
    template_name = 'notice/notice_form.html'
    success_url = reverse_lazy('notice:list')

    def dispatch(self, request, *args, **kwargs):
        notice = self.get_object()
        user_role = get_user_role(request.user)

        # Only admin or notice creator can edit
        if user_role != 'admin' and notice.created_by != request.user:
            messages.error(request, "You don't have permission to edit this notice.")
            return redirect('notice:detail', pk=notice.pk)

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        with transaction.atomic():
            # Delete existing recipients if recipient type changed
            if 'recipient_type' in form.changed_data or 'target_class' in form.changed_data:
                self.object.recipients.all().delete()

                # Create new recipients
                self.create_recipients(self.object, form.cleaned_data)

            response = super().form_valid(form)
            messages.success(self.request, f"Notice '{self.object.title}' updated successfully!")
            return response

    def create_recipients(self, notice, cleaned_data):
        """Same logic as in CreateView"""
        # Reuse the same method from NoticeCreateView
        create_view = NoticeCreateView()
        create_view.create_recipients(notice, cleaned_data)


class NoticeDeleteView(LoginRequiredMixin, DeleteView):
    """Delete view for notices - only for admin and notice creator"""
    model = Notice
    template_name = 'notice/notice_confirm_delete.html'
    success_url = reverse_lazy('notice:list')

    def dispatch(self, request, *args, **kwargs):
        notice = self.get_object()
        user_role = get_user_role(request.user)

        # Only admin or notice creator can delete
        if user_role != 'admin' and notice.created_by != request.user:
            messages.error(request, "You don't have permission to delete this notice.")
            return redirect('notice:detail', pk=notice.pk)

        return super().dispatch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        notice = self.get_object()
        messages.success(request, f"Notice '{notice.title}' deleted successfully!")
        return super().delete(request, *args, **kwargs)


@login_required
def dashboard_notices(request):
    """Dashboard view showing recent notices for current user"""
    user_role = get_user_role(request.user)

    # Get recent notices for the user
    if user_role == 'admin':
        recent_notices = Notice.objects.select_related('created_by', 'category').order_by('-created_at')[:5]
    else:
        # Get notices where user is recipient
        user_notice_ids = NoticeRecipient.objects.filter(
            user=request.user
        ).values_list('notice_id', flat=True)

        recent_notices = Notice.objects.filter(
            Q(id__in=user_notice_ids) | Q(recipient_type='all'),
            status='published'
        ).select_related('created_by', 'category').order_by('-created_at')[:5]

    # Get unread count
    unread_count = NoticeRecipient.objects.filter(
        user=request.user,
        is_read=False
    ).count()

    context = {
        'recent_notices': recent_notices,
        'unread_count': unread_count,
        'user_role': user_role
    }

    return render(request, 'notice/dashboard_notices.html', context)


@login_required
def mark_notice_read(request, notice_id):
    """AJAX view to mark a notice as read"""
    if request.method == 'POST':
        try:
            recipient = NoticeRecipient.objects.get(
                notice_id=notice_id,
                user=request.user
            )
            recipient.mark_as_read()
            return JsonResponse({'status': 'success', 'message': 'Notice marked as read'})
        except NoticeRecipient.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Notice not found'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})


@login_required
def quick_notice_create(request):
    """Quick notice creation for admin/teachers"""
    user_role = get_user_role(request.user)
    if user_role not in ['admin', 'teacher']:
        return HttpResponseForbidden("You don't have permission to create notices.")

    if request.method == 'POST':
        form = QuickNoticeForm(request.POST)
        if form.is_valid():
            # Create notice
            notice = Notice.objects.create(
                title=form.cleaned_data['title'],
                content=form.cleaned_data['content'],
                recipient_type=form.cleaned_data['recipient_type'],
                priority=form.cleaned_data['priority'],
                is_important=form.cleaned_data['is_important'],
                created_by=request.user,
                status='published'
            )

            # Create recipients
            create_view = NoticeCreateView()
            create_view.create_recipients(notice, form.cleaned_data)

            messages.success(request, f"Quick notice '{notice.title}' created successfully!")
            return redirect('notice:list')
    else:
        form = QuickNoticeForm()

    return render(request, 'notice/quick_notice_form.html', {'form': form})


@login_required
def my_notices(request):
    """View showing notices specifically for the current user"""
    # Get notices where user is recipient
    user_notice_ids = NoticeRecipient.objects.filter(
        user=request.user
    ).values_list('notice_id', flat=True)

    notices = Notice.objects.filter(
        Q(id__in=user_notice_ids) | Q(recipient_type='all'),
        status='published'
    ).select_related('created_by', 'category').order_by('-created_at')

    # Paginate
    paginator = Paginator(notices, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Get read status for each notice and attach to notice objects
    user_recipients = NoticeRecipient.objects.filter(
        user=request.user,
        notice__in=page_obj
    ).select_related('notice')

    read_status = {recipient.notice_id: recipient.is_read for recipient in user_recipients}

    # Attach read status to each notice object
    unread_count = 0
    for notice in page_obj:
        notice.is_read_by_user = read_status.get(notice.id, False)
        if not notice.is_read_by_user:
            unread_count += 1

    context = {
        'page_obj': page_obj,
        'unread_count': unread_count,
        'user_role': get_user_role(request.user)
    }

    return render(request, 'notice/my_notices.html', context)


# Category management views
class NoticeCategoryListView(LoginRequiredMixin, ListView):
    """List view for notice categories - admin only"""
    model = NoticeCategory
    template_name = 'notice/category_list.html'
    context_object_name = 'categories'

    def dispatch(self, request, *args, **kwargs):
        if get_user_role(request.user) != 'admin':
            messages.error(request, "You don't have permission to manage categories.")
            return redirect('notice:list')
        return super().dispatch(request, *args, **kwargs)


class NoticeCategoryCreateView(LoginRequiredMixin, CreateView):
    """Create view for notice categories - admin only"""
    model = NoticeCategory
    form_class = NoticeCategoryForm
    template_name = 'notice/category_form.html'
    success_url = reverse_lazy('notice:category_list')

    def dispatch(self, request, *args, **kwargs):
        if get_user_role(request.user) != 'admin':
            messages.error(request, "You don't have permission to create categories.")
            return redirect('notice:list')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, f"Category '{form.instance.name}' created successfully!")
        return super().form_valid(form)
