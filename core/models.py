from django.db import models
from django.utils.translation import gettext_lazy as _

class Language(models.Model):
    """نموذج اللغات المدعومة"""
    code = models.CharField(max_length=10, unique=True)  # 'en', 'ar'
    name = models.CharField(max_length=50)  # 'English', 'العربية'
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    direction = models.CharField(max_length=10, choices=[('ltr', 'LTR'), ('rtl', 'RTL')], default='ltr')
    
    class Meta:
        verbose_name = _("Language")
        verbose_name_plural = _("Languages")
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if self.is_default:
            Language.objects.filter(is_default=True).update(is_default=False)
        super().save(*args, **kwargs)

class TranslationMixin(models.Model):
    """Mixin للترجمات - كل المحتوى القابل للترجمة يرث هذا"""
    language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name="%(class)s_set")
    
    class Meta:
        abstract = True
        unique_together = [('language', 'content_type', 'object_id')]

# ========== المحتوى الأساسي ==========

class SiteSetting(models.Model):
    """إعدادات الموقع العامة - يمكن تعديلها من لوحة التحكم"""
    # معلومات أساسية
    site_name = models.CharField(max_length=100, default="SnapFolio")
    site_logo = models.ImageField(upload_to='logo/', blank=True, null=True)
    favicon = models.ImageField(upload_to='favicon/', blank=True, null=True)
    footer_text = models.CharField(max_length=200, blank=True)
    
    # إعدادات التواصل
    contact_email = models.EmailField(default="snapfolio@gmail.com")
    contact_phone = models.CharField(max_length=20, blank=True)
    contact_address = models.TextField(blank=True)
    
    # روابط التواصل الاجتماعي
    facebook_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    
    # إعدادات عامة
    default_language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True, related_name='default_site')
    enable_rtl = models.BooleanField(default=True)
    maintenance_mode = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = _("Site Setting")
        verbose_name_plural = _("Site Settings")
    
    def __str__(self):
        return self.site_name

class DynamicSection(models.Model):
    """أقسام الموقع - يمكنك إضافة أي قسم تريده"""
    SECTION_TYPES = [
        ('hero', 'Hero Section'),
        ('about', 'About Section'),
        ('skills', 'Skills Section'),
        ('experience', 'Experience Section'),
        ('education', 'Education Section'),
        ('services', 'Services Section'),
        ('portfolio', 'Portfolio Section'),
        ('testimonials', 'Testimonials Section'),
        ('contact', 'Contact Section'),
        ('footer', 'Footer Section'),
        ('custom', 'Custom Section'),
    ]
    
    section_key = models.CharField(max_length=100, unique=True)  # 'hero', 'about'
    section_type = models.CharField(max_length=50, choices=SECTION_TYPES)
    order = models.IntegerField(default=0)  # ترتيب ظهور القسم
    is_active = models.BooleanField(default=True)
    background_image = models.ImageField(upload_to='sections/', blank=True, null=True)
    background_color = models.CharField(max_length=20, blank=True, help_text="HEX color code")
    custom_class = models.CharField(max_length=200, blank=True, help_text="Custom CSS class")
    
    class Meta:
        ordering = ['order']
        verbose_name = _("Dynamic Section")
        verbose_name_plural = _("Dynamic Sections")
    
    def __str__(self):
        return f"{self.get_section_type_display()} ({self.section_key})"

class SectionContent(models.Model):
    """محتوى كل قسم - متعدد اللغات"""
    section = models.ForeignKey(DynamicSection, on_delete=models.CASCADE, related_name='contents')
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    
    # محتوى عام
    title = models.CharField(max_length=200, blank=True)
    subtitle = models.CharField(max_length=300, blank=True)
    description = models.TextField(blank=True)
    button_text = models.CharField(max_length=100, blank=True)
    button_link = models.CharField(max_length=500, blank=True)
    button_text_2 = models.CharField(max_length=100, blank=True)
    button_link_2 = models.CharField(max_length=500, blank=True)
    
    # محتوى إضافي (JSON للتوسع)
    extra_data = models.JSONField(default=dict, blank=True, help_text="بيانات إضافية بصيغة JSON")
    
    class Meta:
        unique_together = [('section', 'language')]
        verbose_name = _("Section Content")
        verbose_name_plural = _("Section Contents")
    
    def __str__(self):
        return f"{self.section.section_key} - {self.language.name}"

# ========== المعلومات الشخصية ==========

class PersonalInfo(models.Model):
    """المعلومات الشخصية - متعددة اللغات"""
    language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name='personal_infos')
    
    name = models.CharField(max_length=100)
    title = models.CharField(max_length=200)  # Web Designer, Developer
    bio = models.TextField()
    short_bio = models.CharField(max_length=300, blank=True)
    
    # إحصائيات
    years_experience = models.IntegerField(default=5)
    projects_completed = models.IntegerField(default=150)
    client_satisfaction = models.IntegerField(default=98)
    happy_clients = models.IntegerField(default=120)
    
    # ملف شخصي
    profile_image = models.ImageField(upload_to='profile/', blank=True, null=True)
    resume_file = models.FileField(upload_to='resume/', blank=True, null=True)
    
    # كلمات مفتاحية للسيرة
    keywords = models.CharField(max_length=500, blank=True, help_text="SEO keywords")
    
    class Meta:
        unique_together = [('language',)]
        verbose_name = _("Personal Info")
        verbose_name_plural = _("Personal Infos")
    
    def __str__(self):
        return f"{self.name} - {self.language.name}"

# ========== التعليم ==========

class Education(models.Model):
    """الشهادات التعليمية - متعددة اللغات"""
    language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name='educations')
    
    degree = models.CharField(max_length=200)  # Bachelor of Science
    field_of_study = models.CharField(max_length=200)  # Computer Science
    institution = models.CharField(max_length=200)  # University name
    start_year = models.IntegerField()
    end_year = models.IntegerField(null=True, blank=True)
    is_current = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    grade = models.CharField(max_length=50, blank=True)  # GPA, Grade
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-end_year', 'order']
        verbose_name = _("Education")
        verbose_name_plural = _("Educations")
    
    def __str__(self):
        return f"{self.degree} - {self.institution}"

# ========== الخبرات العملية ==========

class WorkExperience(models.Model):
    """الخبرات المهنية - متعددة اللغات"""
    language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name='work_experiences')
    
    job_title = models.CharField(max_length=200)
    company_name = models.CharField(max_length=200)
    company_website = models.URLField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(default=False)
    description = models.TextField()
    achievements = models.JSONField(default=list, help_text="قائمة بالإنجازات")
    technologies = models.CharField(max_length=500, blank=True, help_text="التقنيات المستخدمة")
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-start_date', 'order']
        verbose_name = _("Work Experience")
        verbose_name_plural = _("Work Experiences")
    
    def __str__(self):
        return f"{self.job_title} at {self.company_name}"

# ========== المهارات ==========

class SkillCategory(models.Model):
    """فئات المهارات"""
    language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name='skill_categories')
    name = models.CharField(max_length=100)  # Front-End, Back-End, Design
    icon = models.CharField(max_length=50, blank=True)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name_plural = "Skill Categories"
        ordering = ['order']
    
    def __str__(self):
        return self.name

class Skill(models.Model):
    """المهارات الفردية"""
    language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name='skills')
    category = models.ForeignKey(SkillCategory, on_delete=models.CASCADE, related_name='skills')
    
    name = models.CharField(max_length=100)  # JavaScript, Python, React
    proficiency = models.IntegerField(default=80, help_text="Percentage 0-100")
    years_of_experience = models.DecimalField(max_digits=3, decimal_places=1, default=0)
    icon = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-proficiency', 'order']
        verbose_name = _("Skill")
        verbose_name_plural = _("Skills")
    
    def __str__(self):
        return self.name

# ========== الخدمات ==========

class Service(models.Model):
    """الخدمات المقدمة - متعددة اللغات"""
    language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name='services')
    
    title = models.CharField(max_length=200)
    short_description = models.CharField(max_length=300)
    full_description = models.TextField()
    icon = models.CharField(max_length=50, blank=True)  # Bootstrap icon or FontAwesome
    image = models.ImageField(upload_to='services/', blank=True, null=True)
    
    # قائمة مميزات الخدمة
    features = models.JSONField(default=list, help_text="قائمة مميزات الخدمة")
    
    # SEO
    slug = models.SlugField(max_length=200, unique=True)
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.CharField(max_length=500, blank=True)
    
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['order']
        verbose_name = _("Service")
        verbose_name_plural = _("Services")
    
    def __str__(self):
        return self.title

class ServiceDetail(models.Model):
    """تفاصيل إضافية للخدمة - محتوى طويل"""
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='details')
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    
    content_title = models.CharField(max_length=200)
    content_body = models.TextField()
    image = models.ImageField(upload_to='service_details/', blank=True, null=True)
    
    # قائمة نقاط إضافية
    points_list = models.JSONField(default=list, help_text="قائمة نقطية للمحتوى")
    
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order']
        verbose_name = _("Service Detail")
        verbose_name_plural = _("Service Details")
    
    def __str__(self):
        return f"{self.service.title} - {self.content_title}"

# ========== المشاريع (Portfolio) ==========

class PortfolioCategory(models.Model):
    """فئات المشاريع"""
    language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name='portfolio_categories')
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100)
    order = models.IntegerField(default=0)
    
    class Meta:
        verbose_name_plural = "Portfolio Categories"
    
    def __str__(self):
        return self.name

class Portfolio(models.Model):
    """المشاريع - متعددة اللغات"""
    language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name='portfolios')
    category = models.ForeignKey(PortfolioCategory, on_delete=models.SET_NULL, null=True, related_name='portfolios')
    
    # معلومات أساسية
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    client_name = models.CharField(max_length=200)
    project_date = models.DateField()
    project_url = models.URLField(blank=True, help_text="رابط المشروع المباشر")
    
    # محتوى المشروع
    short_description = models.CharField(max_length=300)
    overview = models.TextField()
    challenge = models.TextField(blank=True, help_text="التحدي في المشروع")
    solution = models.TextField(blank=True, help_text="الحل المقدم")
    result = models.TextField(blank=True, help_text="النتائج المحققة")
    
    # صور وفيديوهات
    cover_image = models.ImageField(upload_to='portfolio/cover/')
    gallery_images = models.JSONField(default=list, blank=True, null=True, help_text="قائمة بمسارات الصور")
    video_url = models.URLField(blank=True)
    
    # تقنيات مستخدمة
    technologies = models.JSONField(default=list, help_text="قائمة التقنيات المستخدمة")
    
    # إحصائيات المشروع
    project_duration = models.CharField(max_length=100, blank=True)  # "3 months"
    team_size = models.IntegerField(default=1)
    
    # SEO
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.CharField(max_length=500, blank=True)
    
    order = models.IntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-project_date', 'order']
        verbose_name = _("Portfolio")
        verbose_name_plural = _("Portfolios")
    
    def __str__(self):
        return self.title

class PortfolioFeature(models.Model):
    """ميزات المشروع - كل مشروع يمكن أن يكون له عدة ميزات"""
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='features')
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    
    feature_title = models.CharField(max_length=200)
    feature_description = models.TextField()
    feature_icon = models.CharField(max_length=50, blank=True)
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order']
        verbose_name = _("Portfolio Feature")
        verbose_name_plural = _("Portfolio Features")
    
    def __str__(self):
        return self.feature_title

# ========== الشهادات (Testimonials) ==========

class Testimonial(models.Model):
    """آراء العملاء - متعددة اللغات"""
    language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name='testimonials')
    
    client_name = models.CharField(max_length=200)
    client_position = models.CharField(max_length=200, blank=True)
    client_company = models.CharField(max_length=200, blank=True)
    client_image = models.ImageField(upload_to='testimonials/', blank=True, null=True)
    
    content = models.TextField()
    rating = models.IntegerField(default=5, choices=[(i, i) for i in range(1, 6)])
    
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order']
        verbose_name = _("Testimonial")
        verbose_name_plural = _("Testimonials")
    
    def __str__(self):
        return f"{self.client_name} - {self.rating}★"

# ========== المدونة / المقالات ==========

class BlogCategory(models.Model):
    """فئات المقالات - متعددة اللغات"""
    language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name='blog_categories')
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name

class BlogPost(models.Model):
    """المقالات - متعددة اللغات"""
    language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name='blog_posts')
    category = models.ForeignKey(BlogCategory, on_delete=models.SET_NULL, null=True, related_name='posts')
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    excerpt = models.CharField(max_length=500)
    content = models.TextField()
    featured_image = models.ImageField(upload_to='blog/')
    
    author_name = models.CharField(max_length=100, default="Admin")
    author_image = models.ImageField(upload_to='authors/', blank=True, null=True)
    
    views_count = models.IntegerField(default=0)
    tags = models.CharField(max_length=500, blank=True, help_text="Tags separated by commas")
    
    # SEO
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.CharField(max_length=500, blank=True)
    
    is_published = models.BooleanField(default=True)
    published_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-published_date']
        verbose_name = _("Blog Post")
        verbose_name_plural = _("Blog Posts")
    
    def __str__(self):
        return self.title

# ========== جهات الاتصال (Contact Messages) ==========

class ContactMessage(models.Model):
    """رسائل الاتصال من الزوار"""
    STATUS_CHOICES = [
        ('unread', 'Unread'),
        ('read', 'Read'),
        ('replied', 'Replied'),
        ('spam', 'Spam'),
    ]
    
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='unread')
    
    created_at = models.DateTimeField(auto_now_add=True)
    replied_at = models.DateTimeField(null=True, blank=True)
    reply_message = models.TextField(blank=True)
    
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.CharField(max_length=500, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = _("Contact Message")
        verbose_name_plural = _("Contact Messages")
    
    def __str__(self):
        return f"{self.name} - {self.subject}"

# ========== الصفحات الثابتة ==========

class StaticPage(models.Model):
    """صفحات ثابتة يمكن إضافتها مثل About, Privacy Policy"""
    language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name='static_pages')
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200)
    content = models.TextField()
    featured_image = models.ImageField(upload_to='pages/', blank=True, null=True)
    
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.CharField(max_length=500, blank=True)
    
    show_in_menu = models.BooleanField(default=False)
    menu_order = models.IntegerField(default=0)
    is_published = models.BooleanField(default=True)
    
    class Meta:
        unique_together = [('slug', 'language')]
        ordering = ['menu_order']
        verbose_name = _("Static Page")
        verbose_name_plural = _("Static Pages")
    
    def __str__(self):
        return self.title

# ========== القوائم (Menus) ==========

class Menu(models.Model):
    """قوائم الموقع الديناميكية"""
    name = models.CharField(max_length=100)  # 'main_menu', 'footer_menu'
    location = models.CharField(max_length=100)  # 'header', 'footer', 'sidebar'
    language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name='menus')
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.name} - {self.language.name}"

class MenuItem(models.Model):
    """عناصر القائمة"""
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, related_name='items')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    
    title = models.CharField(max_length=100)
    url = models.CharField(max_length=500)  # يمكن أن يكون '/' أو '/about' أو 'https://...'
    url_type = models.CharField(max_length=20, choices=[
        ('internal', 'Internal Page'),
        ('external', 'External Link'),
        ('section', 'Section Anchor'),
    ], default='internal')
    
    icon = models.CharField(max_length=50, blank=True)
    order = models.IntegerField(default=0)
    open_in_new_tab = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    # للروابط الداخلية
    target_page = models.ForeignKey(StaticPage, on_delete=models.SET_NULL, null=True, blank=True)
    target_section = models.CharField(max_length=100, blank=True)  # لربط بقسم معين
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return self.title

# ========== الإعدادات الإضافية ==========

class GlobalSetting(models.Model):
    """إعدادات عامة على مستوى الموقع"""
    setting_key = models.CharField(max_length=100, unique=True)
    setting_value = models.TextField()
    setting_type = models.CharField(max_length=20, choices=[
        ('text', 'Text'),
        ('number', 'Number'),
        ('boolean', 'Boolean'),
        ('json', 'JSON'),
        ('image', 'Image'),
    ], default='text')
    description = models.CharField(max_length=500, blank=True)
    language = models.ForeignKey(Language, on_delete=models.CASCADE, null=True, blank=True)
    
    class Meta:
        verbose_name = _("Global Setting")
        verbose_name_plural = _("Global Settings")
    
    def __str__(self):
        return self.setting_key

# ========== نموذج للبيانات المكررة (للعناصر المتكررة) ==========

class ReusableBlock(models.Model):
    """بلوكات قابلة لإعادة الاستخدام (مثل الـ CTA، الـ Newsletter)"""
    language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name='reusable_blocks')
    
    block_key = models.CharField(max_length=100)  # 'cta_block', 'newsletter_block'
    title = models.CharField(max_length=200)
    content = models.TextField()
    button_text = models.CharField(max_length=100, blank=True)
    button_link = models.CharField(max_length=500, blank=True)
    background_image = models.ImageField(upload_to='blocks/', blank=True, null=True)
    extra_data = models.JSONField(default=dict, blank=True)
    
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = [('block_key', 'language')]
    
    def __str__(self):
        return f"{self.block_key} - {self.language.name}"