from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Count, Q, Avg
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta

from ..models import *
from ..forms import ContactForm, ProjectRatingForm

# ========== Helper Functions ==========

def is_superuser(user):
    """التحقق من أن المستخدم هو superuser"""
    return user.is_authenticated and user.is_superuser

def get_dashboard_stats():
    """جلب إحصائيات الـ Dashboard"""
    return {
        'total_portfolios': Portfolio.objects.filter(is_active=True).count(),
        'total_portfolios_all': Portfolio.objects.count(),
        'total_services': Service.objects.filter(is_active=True).count(),
        'total_blog_posts': BlogPost.objects.filter(is_published=True).count(),
        'total_ratings': ProjectRating.objects.count(),
        'pending_ratings': ProjectRating.objects.filter(is_approved=False).count(),
        'total_messages': ContactMessage.objects.count(),
        'unread_messages': ContactMessage.objects.filter(status='unread').count(),
        'total_testimonials': Testimonial.objects.filter(is_active=True).count(),
        'total_skills': Skill.objects.filter(is_active=True).count(),
        'total_experiences': WorkExperience.objects.filter(is_active=True).count(),
        'avg_rating': ProjectRating.objects.filter(is_approved=True).aggregate(Avg('rating'))['rating__avg'] or 0,
    }

# ========== Authentication Views ==========

def dashboard_login(request):
    """صفحة تسجيل الدخول إلى لوحة التحكم"""
    if request.user.is_authenticated and request.user.is_superuser:
        return redirect('dashboard:index')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None and user.is_superuser:
            login(request, user)
            messages.success(request, 'Welcome back to the Dashboard!')
            return redirect('dashboard:index')
        else:
            messages.error(request, 'Invalid credentials or insufficient permissions.')
    
    return render(request, 'dashboard/login.html')

def dashboard_logout(request):
    """تسجيل الخروج من لوحة التحكم"""
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('dashboard:login')

# ========== Main Dashboard ==========

@login_required
@user_passes_test(is_superuser)
def dashboard_index(request):
    """الصفحة الرئيسية للوحة التحكم"""
    stats = get_dashboard_stats()
    
    # Recent activities
    recent_ratings = ProjectRating.objects.order_by('-created_at')[:5]
    recent_messages = ContactMessage.objects.order_by('-created_at')[:5]
    recent_portfolios = Portfolio.objects.order_by('-project_date')[:5]
    
    # Ratings over time (last 30 days)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    ratings_over_time = ProjectRating.objects.filter(
        created_at__gte=thirty_days_ago
    ).extra({'date': "date(created_at)"}).values('date').annotate(count=Count('id')).order_by('date')
    
    context = {
        'stats': stats,
        'recent_ratings': recent_ratings,
        'recent_messages': recent_messages,
        'recent_portfolios': recent_portfolios,
        'ratings_over_time': list(ratings_over_time),
    }
    return render(request, 'dashboard/index.html', context)

# ========== Portfolio Management ==========

@login_required
@user_passes_test(is_superuser)
def portfolio_list(request):
    """عرض قائمة المشاريع"""
    portfolios = Portfolio.objects.all().select_related('category', 'language').order_by('-project_date')
    paginator = Paginator(portfolios, 15)
    page = request.GET.get('page', 1)
    portfolios_page = paginator.get_page(page)
    
    return render(request, 'dashboard/portfolios.html', {'portfolios': portfolios_page})

@login_required
@user_passes_test(is_superuser)
def portfolio_edit(request, slug=None):
    """إضافة أو تعديل مشروع"""
    portfolio = None
    if slug:
        portfolio = get_object_or_404(Portfolio, slug=slug)
    
    if request.method == 'POST':
        # Handle form submission
        data = request.POST
        files = request.FILES
        
        if not portfolio:
            portfolio = Portfolio()
        
        portfolio.title = data.get('title')
        portfolio.slug = data.get('slug')
        portfolio.client_name = data.get('client_name')
        portfolio.project_date = data.get('project_date')
        portfolio.project_url = data.get('project_url')
        portfolio.short_description = data.get('short_description')
        portfolio.overview = data.get('overview')
        portfolio.challenge = data.get('challenge')
        portfolio.solution = data.get('solution')
        portfolio.result = data.get('result')
        portfolio.project_duration = data.get('project_duration')
        portfolio.team_size = data.get('team_size') or 1
        portfolio.order = data.get('order') or 0
        portfolio.is_featured = data.get('is_featured') == 'on'
        portfolio.is_active = data.get('is_active') == 'on'
        
        # Get category
        category_id = data.get('category')
        if category_id:
            portfolio.category = PortfolioCategory.objects.filter(id=category_id).first()
        
        # Get language
        language_id = data.get('language')
        if language_id:
            portfolio.language = Language.objects.filter(id=language_id).first()
        
        # Handle cover image
        if files.get('cover_image'):
            portfolio.cover_image = files['cover_image']
        
        # Handle technologies
        technologies = data.getlist('technologies')
        if technologies:
            portfolio.technologies = technologies
        
        portfolio.save()
        
        messages.success(request, f'Portfolio "{portfolio.title}" saved successfully!')
        return redirect('dashboard:portfolios')
    
    languages = Language.objects.filter(is_active=True)
    categories = PortfolioCategory.objects.all()
    
    context = {
        'portfolio': portfolio,
        'languages': languages,
        'categories': categories,
        'is_edit': slug is not None,
    }
    return render(request, 'dashboard/portfolio_edit.html', context)

@login_required
@user_passes_test(is_superuser)
def portfolio_delete(request, slug):
    """حذف مشروع"""
    portfolio = get_object_or_404(Portfolio, slug=slug)
    title = portfolio.title
    portfolio.delete()
    messages.success(request, f'Portfolio "{title}" deleted successfully!')
    return redirect('dashboard:portfolios')

# ========== Services Management ==========

@login_required
@user_passes_test(is_superuser)
def service_list(request):
    """عرض قائمة الخدمات"""
    services = Service.objects.all().select_related('language').order_by('order')
    paginator = Paginator(services, 15)
    page = request.GET.get('page', 1)
    services_page = paginator.get_page(page)
    
    return render(request, 'dashboard/services.html', {'services': services_page})

@login_required
@user_passes_test(is_superuser)
def service_edit(request, slug=None):
    """إضافة أو تعديل خدمة"""
    service = None
    if slug:
        service = get_object_or_404(Service, slug=slug)
    
    if request.method == 'POST':
        data = request.POST
        files = request.FILES
        
        if not service:
            service = Service()
        
        service.title = data.get('title')
        service.slug = data.get('slug')
        service.short_description = data.get('short_description')
        service.full_description = data.get('full_description')
        service.icon = data.get('icon')
        service.order = data.get('order') or 0
        service.is_featured = data.get('is_featured') == 'on'
        service.is_active = data.get('is_active') == 'on'
        
        # Get language
        language_id = data.get('language')
        if language_id:
            service.language = Language.objects.filter(id=language_id).first()
        
        # Handle image
        if files.get('image'):
            service.image = files['image']
        
        # Handle features
        features = data.getlist('features')
        if features:
            service.features = features
        
        service.save()
        
        messages.success(request, f'Service "{service.title}" saved successfully!')
        return redirect('dashboard:services')
    
    languages = Language.objects.filter(is_active=True)
    
    context = {
        'service': service,
        'languages': languages,
        'is_edit': slug is not None,
    }
    return render(request, 'dashboard/service_edit.html', context)

@login_required
@user_passes_test(is_superuser)
def service_delete(request, slug):
    """حذف خدمة"""
    service = get_object_or_404(Service, slug=slug)
    title = service.title
    service.delete()
    messages.success(request, f'Service "{title}" deleted successfully!')
    return redirect('dashboard:services')

# ========== Blog Management ==========

@login_required
@user_passes_test(is_superuser)
def blog_list(request):
    """عرض قائمة المقالات"""
    posts = BlogPost.objects.all().select_related('category', 'language').order_by('-published_date')
    paginator = Paginator(posts, 15)
    page = request.GET.get('page', 1)
    posts_page = paginator.get_page(page)
    
    return render(request, 'dashboard/blog_posts.html', {'posts': posts_page})

@login_required
@user_passes_test(is_superuser)
def blog_edit(request, slug=None):
    """إضافة أو تعديل مقال"""
    post = None
    if slug:
        post = get_object_or_404(BlogPost, slug=slug)
    
    if request.method == 'POST':
        data = request.POST
        files = request.FILES
        
        if not post:
            post = BlogPost()
        
        post.title = data.get('title')
        post.slug = data.get('slug')
        post.excerpt = data.get('excerpt')
        post.content = data.get('content')
        post.tags = data.get('tags')
        post.author_name = data.get('author_name') or 'Admin'
        post.is_published = data.get('is_published') == 'on'
        
        # Get category
        category_id = data.get('category')
        if category_id:
            post.category = BlogCategory.objects.filter(id=category_id).first()
        
        # Get language
        language_id = data.get('language')
        if language_id:
            post.language = Language.objects.filter(id=language_id).first()
        
        # Handle featured image
        if files.get('featured_image'):
            post.featured_image = files['featured_image']
        
        post.save()
        
        messages.success(request, f'Blog post "{post.title}" saved successfully!')
        return redirect('dashboard:blog')
    
    languages = Language.objects.filter(is_active=True)
    categories = BlogCategory.objects.all()
    
    context = {
        'post': post,
        'languages': languages,
        'categories': categories,
        'is_edit': slug is not None,
    }
    return render(request, 'dashboard/blog_edit.html', context)

@login_required
@user_passes_test(is_superuser)
def blog_delete(request, slug):
    """حذف مقال"""
    post = get_object_or_404(BlogPost, slug=slug)
    title = post.title
    post.delete()
    messages.success(request, f'Blog post "{title}" deleted successfully!')
    return redirect('dashboard:blog')

# ========== Ratings Management ==========

@login_required
@user_passes_test(is_superuser)
def ratings_list(request):
    """عرض قائمة التقييمات"""
    ratings = ProjectRating.objects.all().select_related('portfolio').order_by('-created_at')
    paginator = Paginator(ratings, 20)
    page = request.GET.get('page', 1)
    ratings_page = paginator.get_page(page)
    
    return render(request, 'dashboard/ratings.html', {'ratings': ratings_page})

@login_required
@user_passes_test(is_superuser)
def rating_approve(request, id):
    """الموافقة على تقييم"""
    rating = get_object_or_404(ProjectRating, id=id)
    rating.is_approved = not rating.is_approved
    rating.save()
    status = "approved" if rating.is_approved else "unapproved"
    messages.success(request, f'Rating from {rating.name} has been {status}.')
    return redirect('dashboard:ratings')

@login_required
@user_passes_test(is_superuser)
def rating_delete(request, id):
    """حذف تقييم"""
    rating = get_object_or_404(ProjectRating, id=id)
    name = rating.name
    rating.delete()
    messages.success(request, f'Rating from {name} deleted successfully!')
    return redirect('dashboard:ratings')

# ========== Contact Messages ==========

@login_required
@user_passes_test(is_superuser)
def messages_list(request):
    """عرض قائمة رسائل الاتصال"""
    messages_list = ContactMessage.objects.all().order_by('-created_at')
    paginator = Paginator(messages_list, 20)
    page = request.GET.get('page', 1)
    messages_page = paginator.get_page(page)
    
    return render(request, 'dashboard/messages.html', {'messages': messages_page})

@login_required
@user_passes_test(is_superuser)
def message_mark_read(request, id):
    """تحديد رسالة كمقروءة"""
    message = get_object_or_404(ContactMessage, id=id)
    message.status = 'read'
    message.save()
    messages.success(request, f'Message from {message.name} marked as read.')
    return redirect('dashboard:messages')

@login_required
@user_passes_test(is_superuser)
def message_delete(request, id):
    """حذف رسالة"""
    message = get_object_or_404(ContactMessage, id=id)
    name = message.name
    message.delete()
    messages.success(request, f'Message from {name} deleted successfully!')
    return redirect('dashboard:messages')

# ========== Testimonials Management ==========

@login_required
@user_passes_test(is_superuser)
def testimonial_list(request):
    """عرض قائمة الشهادات"""
    testimonials = Testimonial.objects.all().select_related('language').order_by('order')
    paginator = Paginator(testimonials, 15)
    page = request.GET.get('page', 1)
    testimonials_page = paginator.get_page(page)
    
    return render(request, 'dashboard/testimonials.html', {'testimonials': testimonials_page})

@login_required
@user_passes_test(is_superuser)
def testimonial_edit(request, id=None):
    """إضافة أو تعديل شهادة"""
    testimonial = None
    if id:
        testimonial = get_object_or_404(Testimonial, id=id)
    
    if request.method == 'POST':
        data = request.POST
        files = request.FILES
        
        if not testimonial:
            testimonial = Testimonial()
        
        testimonial.client_name = data.get('client_name')
        testimonial.client_position = data.get('client_position')
        testimonial.client_company = data.get('client_company')
        testimonial.content = data.get('content')
        testimonial.rating = data.get('rating') or 5
        testimonial.order = data.get('order') or 0
        testimonial.is_active = data.get('is_active') == 'on'
        
        # Get language
        language_id = data.get('language')
        if language_id:
            testimonial.language = Language.objects.filter(id=language_id).first()
        
        # Handle image
        if files.get('client_image'):
            testimonial.client_image = files['client_image']
        
        testimonial.save()
        
        messages.success(request, f'Testimonial from "{testimonial.client_name}" saved successfully!')
        return redirect('dashboard:testimonials')
    
    languages = Language.objects.filter(is_active=True)
    
    context = {
        'testimonial': testimonial,
        'languages': languages,
        'is_edit': id is not None,
    }
    return render(request, 'dashboard/testimonial_edit.html', context)

@login_required
@user_passes_test(is_superuser)
def testimonial_delete(request, id):
    """حذف شهادة"""
    testimonial = get_object_or_404(Testimonial, id=id)
    name = testimonial.client_name
    testimonial.delete()
    messages.success(request, f'Testimonial from "{name}" deleted successfully!')
    return redirect('dashboard:testimonials')

# ========== Skills Management ==========

@login_required
@user_passes_test(is_superuser)
def skill_list(request):
    """عرض قائمة المهارات"""
    skills = Skill.objects.all().select_related('category', 'language').order_by('-proficiency')
    paginator = Paginator(skills, 20)
    page = request.GET.get('page', 1)
    skills_page = paginator.get_page(page)
    
    return render(request, 'dashboard/skills.html', {'skills': skills_page})

@login_required
@user_passes_test(is_superuser)
def skill_edit(request, id=None):
    """إضافة أو تعديل مهارة"""
    skill = None
    if id:
        skill = get_object_or_404(Skill, id=id)
    
    if request.method == 'POST':
        data = request.POST
        
        if not skill:
            skill = Skill()
        
        skill.name = data.get('name')
        skill.proficiency = data.get('proficiency') or 80
        skill.years_of_experience = data.get('years_of_experience') or 0
        skill.description = data.get('description')
        skill.order = data.get('order') or 0
        skill.is_active = data.get('is_active') == 'on'
        
        # Get category
        category_id = data.get('category')
        if category_id:
            skill.category = SkillCategory.objects.filter(id=category_id).first()
        
        # Get language
        language_id = data.get('language')
        if language_id:
            skill.language = Language.objects.filter(id=language_id).first()
        
        skill.save()
        
        messages.success(request, f'Skill "{skill.name}" saved successfully!')
        return redirect('dashboard:skills')
    
    languages = Language.objects.filter(is_active=True)
    categories = SkillCategory.objects.all()
    
    context = {
        'skill': skill,
        'languages': languages,
        'categories': categories,
        'is_edit': id is not None,
    }
    return render(request, 'dashboard/skill_edit.html', context)

@login_required
@user_passes_test(is_superuser)
def skill_delete(request, id):
    """حذف مهارة"""
    skill = get_object_or_404(Skill, id=id)
    name = skill.name
    skill.delete()
    messages.success(request, f'Skill "{name}" deleted successfully!')
    return redirect('dashboard:skills')

# ========== Work Experiences Management ==========

@login_required
@user_passes_test(is_superuser)
def experience_list(request):
    """عرض قائمة الخبرات"""
    experiences = WorkExperience.objects.all().select_related('language').order_by('-start_date')
    paginator = Paginator(experiences, 15)
    page = request.GET.get('page', 1)
    experiences_page = paginator.get_page(page)
    
    return render(request, 'dashboard/experiences.html', {'experiences': experiences_page})

@login_required
@user_passes_test(is_superuser)
def experience_edit(request, id=None):
    """إضافة أو تعديل خبرة"""
    experience = None
    if id:
        experience = get_object_or_404(WorkExperience, id=id)
    
    if request.method == 'POST':
        data = request.POST
        
        if not experience:
            experience = WorkExperience()
        
        experience.job_title = data.get('job_title')
        experience.company_name = data.get('company_name')
        experience.company_website = data.get('company_website')
        experience.description = data.get('description')
        experience.technologies = data.get('technologies')
        experience.order = data.get('order') or 0
        experience.is_current = data.get('is_current') == 'on'
        experience.is_active = data.get('is_active') == 'on'
        
        # Handle dates
        start_date = data.get('start_date')
        if start_date:
            experience.start_date = start_date
        
        end_date = data.get('end_date')
        if end_date and not experience.is_current:
            experience.end_date = end_date
        
        # Get language
        language_id = data.get('language')
        if language_id:
            experience.language = Language.objects.filter(id=language_id).first()
        
        # Handle achievements
        achievements = data.getlist('achievements')
        if achievements:
            experience.achievements = achievements
        
        experience.save()
        
        messages.success(request, f'Experience "{experience.job_title}" saved successfully!')
        return redirect('dashboard:experiences')
    
    languages = Language.objects.filter(is_active=True)
    
    context = {
        'experience': experience,
        'languages': languages,
        'is_edit': id is not None,
    }
    return render(request, 'dashboard/experience_edit.html', context)

@login_required
@user_passes_test(is_superuser)
def experience_delete(request, id):
    """حذف خبرة"""
    experience = get_object_or_404(WorkExperience, id=id)
    title = experience.job_title
    experience.delete()
    messages.success(request, f'Experience "{title}" deleted successfully!')
    return redirect('dashboard:experiences')

# ========== Education Management ==========

@login_required
@user_passes_test(is_superuser)
def education_list(request):
    """عرض قائمة التعليم"""
    educations = Education.objects.all().select_related('language').order_by('-end_year')
    paginator = Paginator(educations, 15)
    page = request.GET.get('page', 1)
    educations_page = paginator.get_page(page)
    
    return render(request, 'dashboard/education.html', {'educations': educations_page})

@login_required
@user_passes_test(is_superuser)
def education_edit(request, id=None):
    """إضافة أو تعديل تعليم"""
    education = None
    if id:
        education = get_object_or_404(Education, id=id)
    
    if request.method == 'POST':
        data = request.POST
        
        if not education:
            education = Education()
        
        education.degree = data.get('degree')
        education.field_of_study = data.get('field_of_study')
        education.institution = data.get('institution')
        education.start_year = data.get('start_year') or 2000
        education.description = data.get('description')
        education.grade = data.get('grade')
        education.order = data.get('order') or 0
        education.is_current = data.get('is_current') == 'on'
        education.is_active = data.get('is_active') == 'on'
        
        end_year = data.get('end_year')
        if end_year and not education.is_current:
            education.end_year = end_year
        
        # Get language
        language_id = data.get('language')
        if language_id:
            education.language = Language.objects.filter(id=language_id).first()
        
        education.save()
        
        messages.success(request, f'Education "{education.degree}" saved successfully!')
        return redirect('dashboard:education')
    
    languages = Language.objects.filter(is_active=True)
    
    context = {
        'education': education,
        'languages': languages,
        'is_edit': id is not None,
    }
    return render(request, 'dashboard/education_edit.html', context)

@login_required
@user_passes_test(is_superuser)
def education_delete(request, id):
    """حذف تعليم"""
    education = get_object_or_404(Education, id=id)
    degree = education.degree
    education.delete()
    messages.success(request, f'Education "{degree}" deleted successfully!')
    return redirect('dashboard:education')

# ========== Personal Info ==========

@login_required
@user_passes_test(is_superuser)
def personal_info_edit(request):
    """تعديل المعلومات الشخصية"""
    personal_info = PersonalInfo.objects.first()
    
    if request.method == 'POST':
        data = request.POST
        files = request.FILES
        
        if not personal_info:
            personal_info = PersonalInfo()
        
        personal_info.name = data.get('name')
        personal_info.title = data.get('title')
        personal_info.bio = data.get('bio')
        personal_info.short_bio = data.get('short_bio')
        personal_info.years_experience = data.get('years_experience') or 0
        personal_info.projects_completed = data.get('projects_completed') or 0
        personal_info.client_satisfaction = data.get('client_satisfaction') or 0
        personal_info.happy_clients = data.get('happy_clients') or 0
        personal_info.keywords = data.get('keywords')
        
        # Get language
        language_id = data.get('language')
        if language_id:
            personal_info.language = Language.objects.filter(id=language_id).first()
        
        # Handle images
        if files.get('profile_image'):
            personal_info.profile_image = files['profile_image']
        if files.get('resume_file'):
            personal_info.resume_file = files['resume_file']
        
        personal_info.save()
        
        messages.success(request, 'Personal information saved successfully!')
        return redirect('dashboard:personal_info')
    
    languages = Language.objects.filter(is_active=True)
    
    context = {
        'personal_info': personal_info,
        'languages': languages,
    }
    return render(request, 'dashboard/personal_info.html', context)

# ========== Site Settings ==========

@login_required
@user_passes_test(is_superuser)
def site_settings_edit(request):
    """تعديل إعدادات الموقع"""
    settings = SiteSetting.objects.first()
    
    if request.method == 'POST':
        data = request.POST
        files = request.FILES
        
        if not settings:
            settings = SiteSetting()
        
        settings.site_name_ar = data.get('site_name_ar')
        settings.site_name_en = data.get('site_name_en')
        settings.footer_text_ar = data.get('footer_text_ar')
        settings.footer_text_en = data.get('footer_text_en')
        settings.contact_email = data.get('contact_email')
        settings.contact_phone = data.get('contact_phone')
        settings.contact_address_ar = data.get('contact_address_ar')
        settings.contact_address_en = data.get('contact_address_en')
        settings.facebook_url = data.get('facebook_url')
        settings.twitter_url = data.get('twitter_url')
        settings.linkedin_url = data.get('linkedin_url')
        settings.github_url = data.get('github_url')
        settings.instagram_url = data.get('instagram_url')
        settings.enable_rtl = data.get('enable_rtl') == 'on'
        settings.maintenance_mode = data.get('maintenance_mode') == 'on'
        
        # Handle images
        if files.get('site_logo'):
            settings.site_logo = files['site_logo']
        if files.get('favicon'):
            settings.favicon = files['favicon']
        
        settings.save()
        
        messages.success(request, 'Site settings saved successfully!')
        return redirect('dashboard:settings')
    
    context = {'settings': settings}
    return render(request, 'dashboard/settings.html', context)

# ========== Users Management ==========

@login_required
@user_passes_test(is_superuser)
def users_list(request):
    """عرض قائمة المستخدمين (Superusers only)"""
    from django.contrib.auth.models import User
    
    users = User.objects.all().order_by('-is_superuser', '-date_joined')
    paginator = Paginator(users, 20)
    page = request.GET.get('page', 1)
    users_page = paginator.get_page(page)
    
    return render(request, 'dashboard/users.html', {'users': users_page})