# admin.py
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.db.models import Count
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import *

# ============================================================
# إعدادات عامة للـ Admin
# ============================================================

admin.site.site_header = _("SnapFolio Administration")
admin.site.site_title = _("SnapFolio Admin Portal")
admin.site.index_title = _("Welcome to SnapFolio Dashboard")

# ============================================================
# نماذج الترجمة واللغات
# ============================================================

@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'native_name', 'direction', 'is_default', 'is_active', 'flag_preview']
    list_filter = ['is_default', 'is_active', 'direction']
    search_fields = ['code', 'name', 'native_name']
    list_editable = ['is_default', 'is_active']
    list_per_page = 20
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('code', 'name', 'native_name')
        }),
        (_('Settings'), {
            'fields': ('direction', 'flag_icon', 'is_default', 'is_active'),
            'classes': ('wide',)
        }),
    )
    
    def flag_preview(self, obj):
        if obj.flag_icon:
            return format_html('<i class="bi bi-{}"></i>', obj.flag_icon)
        return "-"
    flag_preview.short_description = _("Flag")
    
    def save_model(self, request, obj, form, change):
        if obj.is_default:
            Language.objects.filter(is_default=True).update(is_default=False)
        super().save_model(request, obj, form, change)


# ============================================================
# إعدادات الموقع
# ============================================================

@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    list_display = ['site_logo_preview', 'get_site_name', 'contact_email', 'maintenance_mode']
    fieldsets = (
        (_('Site Basic Info'), {
            'fields': ('site_logo', 'favicon', 'site_name_ar', 'site_name_en', 'footer_text_ar', 'footer_text_en')
        }),
        (_('Contact Information'), {
            'fields': ('contact_email', 'contact_phone', 'contact_address_ar', 'contact_address_en')
        }),
        (_('Social Media Links'), {
            'fields': ('facebook_url', 'twitter_url', 'linkedin_url', 'github_url', 'instagram_url'),
            'classes': ('collapse',)
        }),
        (_('General Settings'), {
            'fields': ('default_language', 'enable_rtl', 'maintenance_mode')
        }),
    )
    
    def site_logo_preview(self, obj):
        if obj.site_logo:
            return format_html('<img src="{}" style="width: 50px; height: 50px; border-radius: 50%; object-fit: cover;" />', obj.site_logo.url)
        return "-"
    site_logo_preview.short_description = _("Logo")
    
    def get_site_name(self, obj):
        return format_html(
            '<span style="font-weight: bold;">AR: {}</span><br><span style="color: #666;">EN: {}</span>',
            obj.site_name_ar, obj.site_name_en
        )
    get_site_name.short_description = _("Site Name")


# ============================================================
# الأقسام الديناميكية
# ============================================================

class SectionContentInline(admin.TabularInline):
    model = SectionContent
    extra = 1
    fields = ['language', 'title', 'subtitle', 'description', 'button_text', 'button_link']
    show_change_link = True


@admin.register(DynamicSection)
class DynamicSectionAdmin(admin.ModelAdmin):
    list_display = ['section_key', 'section_type', 'order', 'is_active']
    list_filter = ['section_type', 'is_active']
    search_fields = ['section_key']
    list_editable = ['order', 'is_active']
    inlines = [SectionContentInline]
    
    fieldsets = (
        (_('Section Info'), {
            'fields': ('section_key', 'section_type', 'order', 'is_active')
        }),
        (_('Design Settings'), {
            'fields': ('background_image', 'background_color', 'custom_class'),
            'classes': ('collapse',)
        }),
    )


@admin.register(SectionContent)
class SectionContentAdmin(admin.ModelAdmin):
    list_display = ['section', 'language', 'title', 'has_description']
    list_filter = ['language', 'section']
    search_fields = ['title', 'description']
    list_per_page = 30
    
    def has_description(self, obj):
        return bool(obj.description)
    has_description.boolean = True
    has_description.short_description = _("Has Description")


# ============================================================
# المعلومات الشخصية
# ============================================================

@admin.register(PersonalInfo)
class PersonalInfoAdmin(admin.ModelAdmin):
    list_display = ['name', 'language', 'title', 'years_experience', 'profile_image_preview']
    list_filter = ['language']
    search_fields = ['name', 'title', 'bio']
    list_per_page = 20
    
    fieldsets = (
        (_('Personal Information'), {
            'fields': ('language', 'name', 'title', 'bio', 'short_bio', 'profile_image', 'resume_file')
        }),
        (_('Statistics'), {
            'fields': ('years_experience', 'projects_completed', 'client_satisfaction', 'happy_clients'),
            'classes': ('wide',)
        }),
        (_('SEO'), {
            'fields': ('keywords',),
            'classes': ('collapse',)
        }),
    )
    
    def profile_image_preview(self, obj):
        if obj.profile_image:
            return format_html('<img src="{}" style="width: 50px; height: 50px; border-radius: 50%; object-fit: cover;" />', obj.profile_image.url)
        return "-"
    profile_image_preview.short_description = _("Profile Image")


# ============================================================
# التعليم والخبرات
# ============================================================

@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ['degree', 'field_of_study', 'institution', 'language', 'start_year', 'end_year', 'is_current', 'order']
    list_filter = ['language', 'is_current', 'is_active']
    search_fields = ['degree', 'field_of_study', 'institution']
    list_editable = ['order', 'is_current']
    list_per_page = 30
    
    fieldsets = (
        (_('Education Info'), {
            'fields': ('language', 'degree', 'field_of_study', 'institution')
        }),
        (_('Dates'), {
            'fields': ('start_year', 'end_year', 'is_current')
        }),
        (_('Additional Info'), {
            'fields': ('description', 'grade', 'order', 'is_active')
        }),
    )


@admin.register(WorkExperience)
class WorkExperienceAdmin(admin.ModelAdmin):
    list_display = ['job_title', 'company_name', 'language', 'start_date', 'end_date', 'is_current', 'order']
    list_filter = ['language', 'is_current', 'is_active']
    search_fields = ['job_title', 'company_name', 'description']
    list_editable = ['order', 'is_current']
    list_per_page = 30
    
    fieldsets = (
        (_('Job Info'), {
            'fields': ('language', 'job_title', 'company_name', 'company_website')
        }),
        (_('Dates'), {
            'fields': ('start_date', 'end_date', 'is_current')
        }),
        (_('Details'), {
            'fields': ('description', 'achievements', 'technologies', 'order', 'is_active')
        }),
    )


# ============================================================
# المهارات
# ============================================================

@admin.register(SkillCategory)
class SkillCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'language', 'icon', 'order', 'is_active', 'skills_count']
    list_filter = ['language', 'is_active']
    search_fields = ['name']
    list_editable = ['order', 'is_active']
    list_per_page = 30
    
    def skills_count(self, obj):
        count = obj.skills.filter(is_active=True).count()
        url = reverse('admin:core_skill_changelist') + f'?category__id__exact={obj.id}'
        return format_html('<a href="{}">{} {}</a>', url, count, _('skills'))
    skills_count.short_description = _("Skills Count")


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'language', 'proficiency', 'years_of_experience', 'order', 'is_active']
    list_filter = ['category', 'language', 'is_active']
    search_fields = ['name', 'description']
    list_editable = ['proficiency', 'order', 'is_active']
    list_per_page = 50
    
    fieldsets = (
        (_('Skill Info'), {
            'fields': ('language', 'category', 'name', 'icon')
        }),
        (_('Proficiency'), {
            'fields': ('proficiency', 'years_of_experience', 'description')
        }),
        (_('Settings'), {
            'fields': ('order', 'is_active')
        }),
    )


# ============================================================
# الخدمات
# ============================================================

class ServiceDetailInline(admin.TabularInline):
    model = ServiceDetail
    extra = 1
    fields = ['language', 'content_title', 'content_body', 'image', 'order']
    show_change_link = True


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['title', 'language', 'icon_preview', 'short_description', 'is_featured', 'order', 'is_active']
    list_filter = ['language', 'is_featured', 'is_active']
    search_fields = ['title', 'short_description', 'full_description']
    list_editable = ['is_featured', 'order', 'is_active']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ServiceDetailInline]
    list_per_page = 30
    
    fieldsets = (
        (_('Service Info'), {
            'fields': ('language', 'title', 'slug', 'icon', 'image')
        }),
        (_('Description'), {
            'fields': ('short_description', 'full_description', 'features')
        }),
        (_('SEO'), {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
        (_('Settings'), {
            'fields': ('order', 'is_featured', 'is_active')
        }),
    )
    
    def icon_preview(self, obj):
        if obj.icon:
            return format_html('<i class="bi bi-{}"></i>', obj.icon)
        return "-"
    icon_preview.short_description = _("Icon")


@admin.register(ServiceDetail)
class ServiceDetailAdmin(admin.ModelAdmin):
    list_display = ['service', 'language', 'content_title', 'order']
    list_filter = ['language', 'service']
    search_fields = ['content_title', 'content_body']
    list_editable = ['order']


# ============================================================
# المشاريع (Portfolio)
# ============================================================

class PortfolioFeatureInline(admin.TabularInline):
    model = PortfolioFeature
    extra = 1
    fields = ['language', 'feature_title', 'feature_description', 'feature_icon', 'order']
    show_change_link = True


@admin.register(PortfolioCategory)
class PortfolioCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'language', 'slug', 'order', 'portfolios_count']
    list_filter = ['language']
    search_fields = ['name']
    list_editable = ['order']
    prepopulated_fields = {'slug': ('name',)}
    list_per_page = 30
    
    def portfolios_count(self, obj):
        count = obj.portfolios.filter(is_active=True).count()
        url = reverse('admin:core_portfolio_changelist') + f'?category__id__exact={obj.id}'
        return format_html('<a href="{}">{} {}</a>', url, count, _('projects'))
    portfolios_count.short_description = _("Projects Count")


@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'language', 'client_name', 'project_date', 'cover_image_preview', 'is_featured', 'is_active']
    list_filter = ['category', 'language', 'is_featured', 'is_active']
    search_fields = ['title', 'client_name', 'short_description', 'overview']
    list_editable = ['is_featured', 'is_active']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [PortfolioFeatureInline]
    list_per_page = 30
    date_hierarchy = 'project_date'
    
    fieldsets = (
        (_('Basic Info'), {
            'fields': ('language', 'category', 'title', 'slug', 'client_name', 'project_date', 'project_url')
        }),
        (_('Content'), {
            'fields': ('short_description', 'overview', 'challenge', 'solution', 'result')
        }),
        (_('Media'), {
            'fields': ('cover_image', 'gallery_images', 'video_url')
        }),
        (_('Technical Info'), {
            'fields': ('technologies', 'project_duration', 'team_size')
        }),
        (_('SEO'), {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
        (_('Settings'), {
            'fields': ('order', 'is_featured', 'is_active')
        }),
    )
    
    def cover_image_preview(self, obj):
        if obj.cover_image:
            return format_html('<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 8px;" />', obj.cover_image.url)
        return format_html('<span style="color: red;">⚠️ No Image</span>')
    cover_image_preview.short_description = _("Cover Image")


@admin.register(PortfolioFeature)
class PortfolioFeatureAdmin(admin.ModelAdmin):
    list_display = ['feature_title', 'portfolio', 'language', 'order']
    list_filter = ['language', 'portfolio']
    search_fields = ['feature_title', 'feature_description']
    list_editable = ['order']


# ============================================================
# آراء العملاء
# ============================================================

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ['client_name', 'client_position', 'language', 'rating', 'content_preview', 'order', 'is_active']
    list_filter = ['language', 'rating', 'is_active']
    search_fields = ['client_name', 'client_position', 'content']
    list_editable = ['order', 'is_active']
    list_per_page = 30
    
    fieldsets = (
        (_('Client Info'), {
            'fields': ('language', 'client_name', 'client_position', 'client_company', 'client_image')
        }),
        (_('Content'), {
            'fields': ('content', 'rating')
        }),
        (_('Settings'), {
            'fields': ('order', 'is_active')
        }),
    )
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = _("Content")
    
    def rating_stars(self, obj):
        stars = '★' * obj.rating + '☆' * (5 - obj.rating)
        return format_html('<span style="color: #ffc107;">{}</span>', stars)
    rating_stars.short_description = _("Rating")


# ============================================================
# المدونة
# ============================================================

@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'language', 'slug', 'posts_count']
    list_filter = ['language']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_per_page = 30
    
    def posts_count(self, obj):
        count = obj.posts.filter(is_published=True).count()
        url = reverse('admin:core_blogpost_changelist') + f'?category__id__exact={obj.id}'
        return format_html('<a href="{}">{} {}</a>', url, count, _('posts'))
    posts_count.short_description = _("Posts Count")


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'language', 'author_name', 'published_date', 'views_count', 'featured_image_preview', 'is_published']
    list_filter = ['category', 'language', 'is_published', 'published_date']
    search_fields = ['title', 'excerpt', 'content', 'author_name', 'tags']
    list_editable = ['is_published']
    prepopulated_fields = {'slug': ('title',)}
    list_per_page = 30
    date_hierarchy = 'published_date'
    readonly_fields = ['views_count', 'updated_date', 'published_date']  # أضف published_date هنا
    
    fieldsets = (
        (_('Post Info'), {
            'fields': ('language', 'category', 'title', 'slug', 'author_name', 'author_image')
        }),
        (_('Content'), {
            'fields': ('excerpt', 'content', 'featured_image')
        }),
        (_('Metadata'), {
            'fields': ('tags', 'views_count')
        }),
        (_('SEO'), {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
        (_('Settings'), {
            'fields': ('is_published', 'published_date', 'updated_date')  # published_date كـ readonly
        }),
    )
    
    def featured_image_preview(self, obj):
        if obj.featured_image:
            return format_html('<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 8px;" />', obj.featured_image.url)
        return "-"
    featured_image_preview.short_description = _("Featured Image")



# ============================================================
# رسائل الاتصال
# ============================================================

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'status', 'created_at', 'message_preview']
    list_filter = ['status', 'created_at']
    search_fields = ['name', 'email', 'subject', 'message']
    list_editable = ['status']
    list_per_page = 30
    date_hierarchy = 'created_at'
    readonly_fields = ['name', 'email', 'phone', 'subject', 'message', 'ip_address', 'user_agent', 'created_at']
    
    fieldsets = (
        (_('Sender Info'), {
            'fields': ('name', 'email', 'phone', 'ip_address', 'user_agent')
        }),
        (_('Message'), {
            'fields': ('subject', 'message', 'created_at')
        }),
        (_('Status'), {
            'fields': ('status', 'replied_at', 'reply_message')
        }),
    )
    
    def message_preview(self, obj):
        return obj.message[:100] + '...' if len(obj.message) > 100 else obj.message
    message_preview.short_description = _("Message Preview")
    
    def has_add_permission(self, request):
        return False
    
    actions = ['mark_as_read', 'mark_as_replied', 'mark_as_spam']
    
    @admin.action(description=_("Mark selected messages as read"))
    def mark_as_read(self, request, queryset):
        updated = queryset.update(status='read')
        self.message_user(request, _(f"{updated} messages marked as read."))
    
    @admin.action(description=_("Mark selected messages as replied"))
    def mark_as_replied(self, request, queryset):
        updated = queryset.update(status='replied')
        self.message_user(request, _(f"{updated} messages marked as replied."))
    
    @admin.action(description=_("Mark selected messages as spam"))
    def mark_as_spam(self, request, queryset):
        updated = queryset.update(status='spam')
        self.message_user(request, _(f"{updated} messages marked as spam."))


# ============================================================
# الصفحات الثابتة
# ============================================================

@admin.register(StaticPage)
class StaticPageAdmin(admin.ModelAdmin):
    list_display = ['title', 'language', 'slug', 'show_in_menu', 'is_published']
    list_filter = ['language', 'show_in_menu', 'is_published']
    search_fields = ['title', 'content']
    list_editable = ['show_in_menu', 'is_published']
    prepopulated_fields = {'slug': ('title',)}
    list_per_page = 30
    
    fieldsets = (
        (_('Page Info'), {
            'fields': ('language', 'title', 'slug', 'content', 'featured_image')
        }),
        (_('SEO'), {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
        (_('Settings'), {
            'fields': ('show_in_menu', 'menu_order', 'is_published')
        }),
    )


# ============================================================
# القوائم
# ============================================================

class MenuItemInline(admin.TabularInline):
    model = MenuItem
    extra = 3
    fields = ['title', 'url', 'url_type', 'parent', 'icon', 'order', 'open_in_new_tab', 'is_active']
    show_change_link = True


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ['name', 'location', 'language', 'is_active', 'items_count']
    list_filter = ['location', 'language', 'is_active']
    search_fields = ['name', 'location']
    list_editable = ['is_active']
    inlines = [MenuItemInline]
    
    def items_count(self, obj):
        return obj.items.filter(is_active=True).count()
    items_count.short_description = _("Items Count")


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ['title', 'menu', 'parent', 'url', 'order', 'is_active']
    list_filter = ['menu', 'url_type', 'is_active']
    search_fields = ['title', 'url']
    list_editable = ['order', 'is_active']
    list_per_page = 50


# ============================================================
# الإعدادات العامة والبلوكات القابلة لإعادة الاستخدام
# ============================================================

@admin.register(GlobalSetting)
class GlobalSettingAdmin(admin.ModelAdmin):
    list_display = ['setting_key', 'setting_type', 'setting_value_preview', 'language']
    list_filter = ['setting_type', 'language']
    search_fields = ['setting_key', 'description', 'setting_value']
    list_per_page = 30
    
    def setting_value_preview(self, obj):
        if obj.setting_type == 'boolean':
            return '✓' if obj.setting_value.lower() == 'true' else '✗'
        return obj.setting_value[:50] + '...' if len(obj.setting_value) > 50 else obj.setting_value
    setting_value_preview.short_description = _("Value")


@admin.register(ReusableBlock)
class ReusableBlockAdmin(admin.ModelAdmin):
    list_display = ['block_key', 'language', 'title', 'is_active']
    list_filter = ['language', 'is_active']
    search_fields = ['block_key', 'title', 'content']
    list_editable = ['is_active']
    list_per_page = 30
    
    fieldsets = (
        (_('Block Info'), {
            'fields': ('language', 'block_key', 'title', 'content')
        }),
        (_('Button'), {
            'fields': ('button_text', 'button_link')
        }),
        (_('Design'), {
            'fields': ('background_image', 'extra_data')
        }),
        (_('Settings'), {
            'fields': ('is_active',)
        }),
    )
    
    
# ============================================================
# نظام التقييمات
# ============================================================

@admin.register(ProjectRating)
class ProjectRatingAdmin(admin.ModelAdmin):
    list_display = ['name', 'portfolio', 'rating', 'is_approved', 'created_at']
    list_filter = ['rating', 'is_approved', 'created_at']
    search_fields = ['name', 'email', 'comment', 'portfolio__title']
    list_editable = ['is_approved']
    list_per_page = 30
    readonly_fields = ['name', 'email', 'rating', 'comment', 'created_at']
    
    fieldsets = (
        (_('Rater Info'), {
            'fields': ('name', 'email')
        }),
        (_('Rating'), {
            'fields': ('portfolio', 'rating', 'comment')
        }),
        (_('Status'), {
            'fields': ('is_approved', 'created_at')
        }),
    )
    
    actions = ['approve_ratings', 'disapprove_ratings']
    
    @admin.action(description=_("Approve selected ratings"))
    def approve_ratings(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, _(f"{updated} ratings approved and will appear on site."))
    
    @admin.action(description=_("Disapprove selected ratings"))
    def disapprove_ratings(self, request, queryset):
        updated = queryset.update(is_approved=False)
        self.message_user(request, _(f"{updated} ratings disapproved."))
    
    def has_add_permission(self, request):
        return False  # المستخدمون يضيفون تقييمات من الواجهة الأمامية فقط
