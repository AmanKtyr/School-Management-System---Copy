from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_page, name='landing_page'),
    path('about/', views.about, name='about'),
    path('features/', views.features, name='features'),
    path('contact/', views.contact, name='contact'),
    path('pricing/', views.pricing, name='pricing'),
    path('blog/', views.blog, name='blog'),
    path('blog/<int:blog_id>/', views.blog_detail, name='blog_detail'),
    path('demo/', views.demo, name='demo'),
    path('testimonials/', views.testimonials, name='testimonials'),
    path('faq/', views.faq, name='faq'),
    path('careers/', views.careers, name='careers'),
    path('sitemap/', views.sitemap, name='sitemap'),
    path('sitemap.xml', views.sitemap_xml, name='sitemap_xml'),
]
