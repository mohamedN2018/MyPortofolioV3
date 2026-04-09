from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from .models import *

# ======================
# تسجيل النماذج مع تخصيص واجهة الإدارة
# ======================

@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'direction', 'is_default', 'is_active']
    list_editable = ['is_default', 'is_active']
    list_filter = ['is_active', 'direction']
    search_fields = ['name', 'code']

@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    list_display = ['site_name', 'contact_email', 'maintenance_mode']
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('site_name', 'site_logo', 'favicon', 'footer_text')
        }),
        (_('Contact Information'), {
            'fields': ('contact_email', 'contact_phone', 'contact_address')
        }),
        (_('Social Media'), {
            'fields': ('facebook_url', 'twitter_url', 'linkedin_url', 'github_url', 'instagram_url')
        }),
        (_('Advanced Settings'), {
            'fields': ('default_language', 'enable_rtl', 'maintenance_mode'),
            'classes': ('collapse',)
        }),
    )

class SectionContentInline(admin.TabularInline):
    model = SectionContent
    extra = 1
    fields = ['language', 'title', 'subtitle', 'description', 'button_text', 'button_link']

@admin.register(DynamicSection)
class DynamicSectionAdmin(admin.ModelAdmin):
    list_display = ['section_key', 'section_type', 'order', 'is_active']
    list_editable = ['order', 'is_active']
    list_filter = ['section_type', 'is_active']
    search_fields = ['section_key']
    inlines = [SectionContentInline]

@admin.register(PersonalInfo)
class PersonalInfoAdmin(admin.ModelAdmin):
    list_display = ['name', 'language', 'title', 'years_experience', 'projects_completed']
    list_filter = ['language']
    search_fields = ['name', 'title', 'bio']
    fieldsets = (
        (_('Personal Details'), {
            'fields': ('language', 'name', 'title', 'bio', 'short_bio', 'profile_image', 'resume_file')
        }),
        (_('Statistics'), {
            'fields': ('years_experience', 'projects_completed', 'client_satisfaction', 'happy_clients')
        }),
        (_('SEO'), {
            'fields': ('keywords',),
            'classes': ('collapse',)
        }),
    )

@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ['degree', 'institution', 'start_year', 'end_year', 'is_current', 'order']
    list_editable = ['order', 'is_current']
    list_filter = ['language', 'is_current']
    search_fields = ['degree', 'institution', 'field_of_study']

@admin.register(WorkExperience)
class WorkExperienceAdmin(admin.ModelAdmin):
    list_display = ['job_title', 'company_name', 'start_date', 'end_date', 'is_current', 'order']
    list_editable = ['order', 'is_current']
    list_filter = ['language', 'is_current']
    search_fields = ['job_title', 'company_name', 'description']
    fieldsets = (
        (_('Job Details'), {
            'fields': ('language', 'job_title', 'company_name', 'company_website')
        }),
        (_('Date Information'), {
            'fields': ('start_date', 'end_date', 'is_current')
        }),
        (_('Content'), {
            'fields': ('description', 'achievements', 'technologies')
        }),
        (_('Display Settings'), {
            'fields': ('order', 'is_active')
        }),
    )

@admin.register(SkillCategory)
class SkillCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'language', 'order', 'is_active']
    list_editable = ['order', 'is_active']
    list_filter = ['language']

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'proficiency', 'years_of_experience', 'order']
    list_editable = ['proficiency', 'order']
    list_filter = ['language', 'category']
    search_fields = ['name', 'description']

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['title', 'language', 'order', 'is_featured', 'is_active']
    list_editable = ['order', 'is_featured', 'is_active']
    list_filter = ['language', 'is_featured', 'is_active']
    search_fields = ['title', 'short_description', 'full_description']
    prepopulated_fields = {'slug': ('title',)}
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('language', 'title', 'slug', 'icon', 'image')
        }),
        (_('Description'), {
            'fields': ('short_description', 'full_description', 'features')
        }),
        (_('SEO'), {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
        (_('Display Settings'), {
            'fields': ('order', 'is_featured', 'is_active')
        }),
    )

@admin.register(PortfolioCategory)
class PortfolioCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'language', 'order']
    list_filter = ['language']
    prepopulated_fields = {'slug': ('name',)}

class PortfolioFeatureInline(admin.TabularInline):
    model = PortfolioFeature
    extra = 1
    fields = ['language', 'feature_title', 'feature_description', 'feature_icon', 'order']

@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'client_name', 'project_date', 'is_featured', 'is_active']
    list_filter = ['language', 'category', 'is_featured', 'is_active']
    search_fields = ['title', 'client_name', 'short_description', 'overview']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [PortfolioFeatureInline]
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('language', 'category', 'title', 'slug', 'client_name', 'project_date', 'project_url')
        }),
        (_('Content'), {
            'fields': ('short_description', 'overview', 'challenge', 'solution', 'result')
        }),
        (_('Media'), {
            'fields': ('cover_image', 'gallery_images', 'video_url')
        }),
        (_('Technical Details'), {
            'fields': ('technologies', 'project_duration', 'team_size')
        }),
        (_('SEO'), {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
        (_('Display Settings'), {
            'fields': ('order', 'is_featured', 'is_active')
        }),
    )

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ['client_name', 'rating', 'language', 'order', 'is_active']
    list_editable = ['rating', 'order', 'is_active']
    list_filter = ['language', 'rating', 'is_active']
    search_fields = ['client_name', 'content', 'client_position']

@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'language']
    list_filter = ['language']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'author_name', 'is_published', 'published_date', 'views_count']
    list_filter = ['language', 'category', 'is_published']
    search_fields = ['title', 'content', 'excerpt', 'author_name']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['views_count', 'published_date', 'updated_date']
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('language', 'category', 'title', 'slug', 'excerpt', 'content', 'featured_image')
        }),
        (_('Author Information'), {
            'fields': ('author_name', 'author_image')
        }),
        (_('Metadata'), {
            'fields': ('tags', 'views_count')
        }),
        (_('SEO'), {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
        (_('Publication'), {
            'fields': ('is_published', 'published_date')
        }),
    )

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['name', 'email', 'subject', 'message']
    readonly_fields = ['created_at', 'ip_address', 'user_agent']
    actions = ['mark_as_read', 'mark_as_replied']
    
    def mark_as_read(self, request, queryset):
        queryset.update(status='read')
    mark_as_read.short_description = _("Mark selected messages as read")
    
    def mark_as_replied(self, request, queryset):
        queryset.update(status='replied')
    mark_as_replied.short_description = _("Mark selected messages as replied")

@admin.register(StaticPage)
class StaticPageAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'language', 'show_in_menu', 'is_published']
    list_filter = ['language', 'show_in_menu', 'is_published']
    search_fields = ['title', 'content']
    prepopulated_fields = {'slug': ('title',)}
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('language', 'title', 'slug', 'content', 'featured_image')
        }),
        (_('SEO'), {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
        (_('Display Settings'), {
            'fields': ('show_in_menu', 'menu_order', 'is_published')
        }),
    )

class MenuItemInline(admin.TabularInline):
    model = MenuItem
    extra = 1
    fields = ['title', 'url', 'url_type', 'parent', 'order', 'icon', 'open_in_new_tab', 'is_active']
    show_change_link = True

@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ['name', 'location', 'language', 'is_active']
    list_filter = ['location', 'language', 'is_active']
    search_fields = ['name']
    inlines = [MenuItemInline]

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ['title', 'menu', 'parent', 'url', 'order', 'is_active']
    list_filter = ['menu', 'url_type', 'is_active']
    search_fields = ['title', 'url']
    list_editable = ['order', 'is_active']

@admin.register(GlobalSetting)
class GlobalSettingAdmin(admin.ModelAdmin):
    list_display = ['setting_key', 'setting_value', 'setting_type', 'language']
    list_filter = ['setting_type', 'language']
    search_fields = ['setting_key', 'description']
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj and obj.setting_type == 'boolean':
            form.base_fields['setting_value'].widget = admin.widgets.AdminRadioSelect(
                choices=[('true', 'True'), ('false', 'False')]
            )
        return form

@admin.register(ReusableBlock)
class ReusableBlockAdmin(admin.ModelAdmin):
    list_display = ['block_key', 'language', 'title', 'is_active']
    list_filter = ['language', 'is_active']
    search_fields = ['block_key', 'title', 'content']
    list_editable = ['is_active']

# ======================
# تخصيص واجهة الـ Admin
# ======================

admin.site.site_header = _("core Administration")
admin.site.site_title = _("core Admin")
admin.site.index_title = _("Welcome to core Dashboard")