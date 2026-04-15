from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import translation
from django.urls import reverse


class Language(models.Model):
    """نموذج اللغات المدعومة"""
    code = models.CharField(max_length=10, unique=True)  # 'en', 'ar'
    name = models.CharField(max_length=50)  # 'English', 'العربية'
    native_name = models.CharField(max_length=50, blank=True)  # 'English', 'العربية'
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    direction = models.CharField(max_length=10, choices=[('ltr', 'LTR'), ('rtl', 'RTL')], default='ltr')
    flag_icon = models.CharField(max_length=50, blank=True, help_text="FontAwesome or Bootstrap icon class")
    
    class Meta:
        verbose_name = _("Language")
        verbose_name_plural = _("Languages")
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if self.is_default:
            Language.objects.filter(is_default=True).update(is_default=False)
        super().save(*args, **kwargs)

class TranslatableModel(models.Model):
    """Model base للترجمة"""
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    
    class Meta:
        abstract = True

class SiteSetting(models.Model):
    """إعدادات الموقع العامة - متعددة اللغات"""
    # حقول غير مترجمة
    site_logo = models.ImageField(upload_to='logo/', blank=True, null=True)
    favicon = models.ImageField(upload_to='favicon/', blank=True, null=True)
    
    # حقول مترجمة
    site_name_ar = models.CharField(max_length=100, default="سناب فوليو", verbose_name="Site Name (Arabic)")
    site_name_en = models.CharField(max_length=100, default="SnapFolio", verbose_name="Site Name (English)")
    footer_text_ar = models.CharField(max_length=200, blank=True, verbose_name="Footer Text (Arabic)")
    footer_text_en = models.CharField(max_length=200, blank=True, verbose_name="Footer Text (English)")
    
    # إعدادات التواصل (غير مترجمة)
    contact_email = models.EmailField(default="snapfolio@gmail.com")
    contact_phone = models.CharField(max_length=20, blank=True)
    contact_address_ar = models.TextField(blank=True, verbose_name="Address (Arabic)")
    contact_address_en = models.TextField(blank=True, verbose_name="Address (English)")
    
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
        return self.get_site_name()
    
    def get_site_name(self):
        """جلب اسم الموقع حسب اللغة الحالية"""
        current_lang = translation.get_language()
        if current_lang == 'ar' and self.site_name_ar:
            return self.site_name_ar
        return self.site_name_en or self.site_name_ar
    
    def get_footer_text(self):
        """جلب نص الفوتر حسب اللغة الحالية"""
        current_lang = translation.get_language()
        if current_lang == 'ar' and self.footer_text_ar:
            return self.footer_text_ar
        return self.footer_text_en or self.footer_text_ar
    
    def get_contact_address(self):
        """جلب العنوان حسب اللغة الحالية"""
        current_lang = translation.get_language()
        if current_lang == 'ar' and self.contact_address_ar:
            return self.contact_address_ar
        return self.contact_address_en or self.contact_address_ar

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
class PersonalInfo(TranslatableModel):
    """المعلومات الشخصية - مترجمة"""
    name = models.CharField(max_length=100)
    title = models.CharField(max_length=200)
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
    
    # كلمات مفتاحية
    keywords = models.CharField(max_length=500, blank=True, help_text="SEO keywords")
    
    class Meta:
        unique_together = [('language',)]
        verbose_name = _("Personal Info")
        verbose_name_plural = _("Personal Infos")
    
    def __str__(self):
        return f"{self.name} - {self.language.name}"
    
    def get_absolute_url(self):
        return reverse('personal_info', args=[self.language.code])
    
# ========== التعليم ==========
class Education(TranslatableModel):
    """الشهادات التعليمية - مترجمة"""
    degree = models.CharField(max_length=200)
    field_of_study = models.CharField(max_length=200)
    institution = models.CharField(max_length=200)
    start_year = models.IntegerField()
    end_year = models.IntegerField(null=True, blank=True)
    is_current = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    grade = models.CharField(max_length=50, blank=True)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-end_year', 'order']
        verbose_name = _("Education")
        verbose_name_plural = _("Educations")
    
    def __str__(self):
        return f"{self.degree} - {self.institution}"

    def get_absolute_url(self):
        return reverse('education', args=[self.language.code])

# ========== الخبرات العملية ==========
class WorkExperience(TranslatableModel):
    """الخبرات المهنية - مترجمة"""
    job_title = models.CharField(max_length=200)
    company_name = models.CharField(max_length=200)
    company_website = models.URLField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(default=False)
    description = models.TextField()
    achievements = models.JSONField(default=list)
    technologies = models.CharField(max_length=500, blank=True)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-start_date', 'order']
        verbose_name = _("Work Experience")
        verbose_name_plural = _("Work Experiences")
    
    def __str__(self):
        return f"{self.job_title} at {self.company_name}"

    def get_absolute_url(self):
        return reverse('work_experience', args=[self.language.code])

# ========== المهارات ==========

class SkillCategory(TranslatableModel):
    """فئات المهارات - مترجمة"""
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, blank=True)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name_plural = "Skill Categories"
        ordering = ['order']
    
    def __str__(self):
        return self.name


class Skill(TranslatableModel):
    """المهارات الفردية - مترجمة"""
    category = models.ForeignKey(SkillCategory, on_delete=models.CASCADE, related_name='skills')
    
    name = models.CharField(max_length=100)
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
class Service(TranslatableModel):
    """الخدمات المقدمة - مترجمة"""
    title = models.CharField(max_length=200)
    short_description = models.CharField(max_length=300)
    full_description = models.TextField()
    icon = models.CharField(max_length=50, blank=True)
    image = models.ImageField(upload_to='services/', blank=True, null=True)
    
    # قائمة مميزات الخدمة
    features = models.JSONField(default=list, help_text="قائمة مميزات الخدمة")
    
    # SEO
    slug = models.SlugField(max_length=200)
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.CharField(max_length=500, blank=True)
    
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['order']
        unique_together = [('slug', 'language')]
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
class PortfolioCategory(TranslatableModel):
    """فئات المشاريع - مترجمة"""
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100)
    order = models.IntegerField(default=0)
    
    class Meta:
        unique_together = [('slug', 'language')]
        verbose_name_plural = "Portfolio Categories"
    
    def __str__(self):
        return self.name

class Portfolio(TranslatableModel):
    """المشاريع - مترجمة"""
    category = models.ForeignKey(PortfolioCategory, on_delete=models.SET_NULL, null=True, related_name='portfolios')
    
    # معلومات أساسية
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200)
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
    gallery_images = models.JSONField(default=list, blank=True, null=True)
    video_url = models.URLField(blank=True)
    
    # تقنيات مستخدمة
    technologies = models.JSONField(default=list)
    
    # إحصائيات المشروع
    project_duration = models.CharField(max_length=100, blank=True)
    team_size = models.IntegerField(default=1)
    
    # SEO
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.CharField(max_length=500, blank=True)
    
    order = models.IntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    
    @property
    def average_rating(self):
        """متوسط التقييمات المقبولة"""
        approved_ratings = self.ratings.filter(is_approved=True)
        if approved_ratings.exists():
            return round(approved_ratings.aggregate(models.Avg('rating'))['rating__avg'], 1)
        return 0
    
    @property
    def ratings_count(self):
        """عدد التقييمات المقبولة"""
        return self.ratings.filter(is_approved=True).count()
    
    @property
    def total_ratings_submitted(self):
        """إجمالي التقييمات المرسلة (بما فيها غير المقبولة)"""
        return self.ratings.count()

    @property
    def avg_rating(self):
        """اسم مختصر لـ average_rating"""
        return self.average_rating
    
    @property
    def rating_count(self):
        """اسم مختصر لـ ratings_count"""
        return self.ratings_count

    class Meta:
        ordering = ['-project_date', 'order']
        unique_together = [('slug', 'language')]
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

# ========== نظام التقييمات (Ratings) ==========
class ProjectRating(models.Model):
    """تقييمات العملاء على المشاريع"""
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='ratings')
    
    name = models.CharField(max_length=100, verbose_name=_("Your Name"))
    email = models.EmailField(verbose_name=_("Your Email"))
    rating = models.IntegerField(
        choices=[(i, f"{i} ★") for i in range(1, 6)],
        verbose_name=_("Rating")
    )
    comment = models.TextField(blank=True, verbose_name=_("Comment (Optional)"))
    
    is_approved = models.BooleanField(default=False, verbose_name=_("Approved"))
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = [('portfolio', 'email')]  # منع تكرار التقييم من نفس البريد
        ordering = ['-created_at']
        verbose_name = _("Project Rating")
        verbose_name_plural = _("Project Ratings")
    
    def __str__(self):
        return f"{self.name} - {self.portfolio.title} - {self.rating}★"


# ========== الشهادات (Testimonials) ==========
class Testimonial(TranslatableModel):
    """آراء العملاء - مترجمة"""
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
class BlogCategory(TranslatableModel):
    """فئات المقالات - مترجمة"""
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100)
    description = models.TextField(blank=True)
    
    class Meta:
        unique_together = [('slug', 'language')]
        verbose_name_plural = "Blog Categories"
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('blog_category', args=[self.slug])

class BlogPost(TranslatableModel):
    """المقالات - مترجمة"""
    category = models.ForeignKey(BlogCategory, on_delete=models.SET_NULL, null=True, related_name='posts')
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200)
    excerpt = models.CharField(max_length=500)
    content = models.TextField()
    featured_image = models.ImageField(upload_to='blog/')
    
    author_name = models.CharField(max_length=100, default="Admin")
    author_image = models.ImageField(upload_to='authors/', blank=True, null=True)
    
    views_count = models.IntegerField(default=0)
    tags = models.CharField(max_length=500, blank=True)
    
    # SEO
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.CharField(max_length=500, blank=True)
    
    is_published = models.BooleanField(default=True)
    published_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-published_date']
        unique_together = [('slug', 'language')]
        verbose_name = _("Blog Post")
        verbose_name_plural = _("Blog Posts")
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('blog_detail', args=[self.slug])

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
    
    
    
    

