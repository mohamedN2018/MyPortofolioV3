from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'dashboard'

urlpatterns = [
    # Authentication
    path('login/', views.dashboard_login, name='login'),
    path('logout/', views.dashboard_logout, name='logout'),
    
    # Main Dashboard
    path('', views.dashboard_index, name='index'),
    
    # Portfolio Management
    path('portfolios/', views.portfolio_list, name='portfolios'),
    path('portfolios/add/', views.portfolio_edit, name='portfolio_add'),
    path('portfolios/edit/<slug:slug>/', views.portfolio_edit, name='portfolio_edit'),
    path('portfolios/delete/<slug:slug>/', views.portfolio_delete, name='portfolio_delete'),
    
    # Services Management
    path('services/', views.service_list, name='services'),
    path('services/add/', views.service_edit, name='service_add'),
    path('services/edit/<slug:slug>/', views.service_edit, name='service_edit'),
    path('services/delete/<slug:slug>/', views.service_delete, name='service_delete'),
    
    # Blog Management
    path('blog/', views.blog_list, name='blog'),
    path('blog/add/', views.blog_edit, name='blog_add'),
    path('blog/edit/<slug:slug>/', views.blog_edit, name='blog_edit'),
    path('blog/delete/<slug:slug>/', views.blog_delete, name='blog_delete'),
    
    # Ratings Management
    path('ratings/', views.ratings_list, name='ratings'),
    path('ratings/approve/<int:id>/', views.rating_approve, name='rating_approve'),
    path('ratings/delete/<int:id>/', views.rating_delete, name='rating_delete'),
    
    # Contact Messages
    path('messages/', views.messages_list, name='messages'),
    path('messages/mark-read/<int:id>/', views.message_mark_read, name='message_mark_read'),
    path('messages/delete/<int:id>/', views.message_delete, name='message_delete'),
    
    # Testimonials
    path('testimonials/', views.testimonial_list, name='testimonials'),
    path('testimonials/add/', views.testimonial_edit, name='testimonial_add'),
    path('testimonials/edit/<int:id>/', views.testimonial_edit, name='testimonial_edit'),
    path('testimonials/delete/<int:id>/', views.testimonial_delete, name='testimonial_delete'),
    
    # Skills
    path('skills/', views.skill_list, name='skills'),
    path('skills/add/', views.skill_edit, name='skill_add'),
    path('skills/edit/<int:id>/', views.skill_edit, name='skill_edit'),
    path('skills/delete/<int:id>/', views.skill_delete, name='skill_delete'),
    
    # Work Experiences
    path('experiences/', views.experience_list, name='experiences'),
    path('experiences/add/', views.experience_edit, name='experience_add'),
    path('experiences/edit/<int:id>/', views.experience_edit, name='experience_edit'),
    path('experiences/delete/<int:id>/', views.experience_delete, name='experience_delete'),
    
    # Education
    path('education/', views.education_list, name='education'),
    path('education/add/', views.education_edit, name='education_add'),
    path('education/edit/<int:id>/', views.education_edit, name='education_edit'),
    path('education/delete/<int:id>/', views.education_delete, name='education_delete'),
    
    # Personal Info
    path('personal-info/', views.personal_info_edit, name='personal_info'),
    
    # Site Settings
    path('settings/', views.site_settings_edit, name='settings'),
    
    # Users (Superuser only)
    path('users/', views.users_list, name='users'),
]