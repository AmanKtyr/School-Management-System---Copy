from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils import timezone
from datetime import datetime, timedelta

def landing_page(request):
    """
    View for the landing page of SipherEdu
    """
    # If user is already authenticated, redirect to dashboard
    if request.user.is_authenticated:
        return redirect('home')

    return render(request, 'website/landing_page.html')

def about(request):
    """
    View for the about page
    """
    return render(request, 'website/about.html')

def features(request):
    """
    View for the features page
    """
    return render(request, 'website/features.html')

def contact(request):
    """
    View for the contact page
    """
    return render(request, 'website/contact.html')

def pricing(request):
    """
    View for the pricing page
    """
    return render(request, 'website/pricing.html')

def blog(request):
    """
    View for the blog listing page
    """
    return render(request, 'website/blog.html')

def blog_detail(request, blog_id):
    """
    View for the blog detail page
    """
    # In a real application, you would fetch the blog post from the database
    # For now, we'll just render the template
    return render(request, 'website/blog_detail.html')

def demo(request):
    """
    View for the demo request page
    """
    # Calculate tomorrow's date for the demo request form
    tomorrow_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    context = {
        'tomorrow_date': tomorrow_date
    }
    return render(request, 'website/demo.html', context)

def testimonials(request):
    """
    View for the testimonials page
    """
    return render(request, 'website/testimonials.html')

def faq(request):
    """
    View for the FAQ page
    """
    return render(request, 'website/faq.html')

def careers(request):
    """
    View for the careers page
    """
    return render(request, 'website/careers.html')

def sitemap(request):
    """
    View for the sitemap page
    """
    return render(request, 'website/sitemap.html')

def sitemap_xml(request):
    """
    View for the XML sitemap
    """
    site_url = request.build_absolute_uri('/').rstrip('/')
    last_modified = timezone.now().strftime('%Y-%m-%d')

    context = {
        'site_url': site_url,
        'last_modified': last_modified,
    }

    content = render_to_string('sitemap.xml', context, request)
    return HttpResponse(content, content_type='application/xml')
