# core/management/commands/copy_content_to_arabic.py
from django.core.management.base import BaseCommand
from django.utils import translation
from core.models import *

class Command(BaseCommand):
    help = 'Copy content from English to Arabic language'

    def handle(self, *args, **options):
        self.stdout.write('Starting to copy content to Arabic...')
        
        # جلب اللغات
        try:
            english = Language.objects.get(code='en')
            arabic = Language.objects.get(code='ar')
        except Language.DoesNotExist:
            self.stdout.write(self.style.ERROR('Languages not found! Please create languages first.'))
            return
        
        # 1. نسخ المعلومات الشخصية
        self.stdout.write('Copying Personal Info...')
        for eng_info in PersonalInfo.objects.filter(language=english):
            PersonalInfo.objects.get_or_create(
                language=arabic,
                defaults={
                    'name': eng_info.name,
                    'title': eng_info.title,
                    'bio': eng_info.bio,
                    'short_bio': eng_info.short_bio,
                    'years_experience': eng_info.years_experience,
                    'projects_completed': eng_info.projects_completed,
                    'client_satisfaction': eng_info.client_satisfaction,
                    'happy_clients': eng_info.happy_clients,
                    'profile_image': eng_info.profile_image,
                    'resume_file': eng_info.resume_file,
                    'keywords': eng_info.keywords,
                }
            )
        
        # 2. نسخ التعليم
        self.stdout.write('Copying Education...')
        for eng_edu in Education.objects.filter(language=english):
            Education.objects.get_or_create(
                language=arabic,
                degree=eng_edu.degree,
                field_of_study=eng_edu.field_of_study,
                institution=eng_edu.institution,
                defaults={
                    'start_year': eng_edu.start_year,
                    'end_year': eng_edu.end_year,
                    'is_current': eng_edu.is_current,
                    'description': eng_edu.description,
                    'grade': eng_edu.grade,
                    'order': eng_edu.order,
                    'is_active': eng_edu.is_active,
                }
            )
        
        # 3. نسخ الخبرات العملية
        self.stdout.write('Copying Work Experiences...')
        for eng_exp in WorkExperience.objects.filter(language=english):
            WorkExperience.objects.get_or_create(
                language=arabic,
                job_title=eng_exp.job_title,
                company_name=eng_exp.company_name,
                defaults={
                    'company_website': eng_exp.company_website,
                    'start_date': eng_exp.start_date,
                    'end_date': eng_exp.end_date,
                    'is_current': eng_exp.is_current,
                    'description': eng_exp.description,
                    'achievements': eng_exp.achievements,
                    'technologies': eng_exp.technologies,
                    'order': eng_exp.order,
                    'is_active': eng_exp.is_active,
                }
            )
        
        # 4. نسخ فئات المهارات
        self.stdout.write('Copying Skill Categories...')
        for eng_cat in SkillCategory.objects.filter(language=english):
            SkillCategory.objects.get_or_create(
                language=arabic,
                name=eng_cat.name,
                defaults={
                    'icon': eng_cat.icon,
                    'order': eng_cat.order,
                    'is_active': eng_cat.is_active,
                }
            )
        
        # 5. نسخ المهارات
        self.stdout.write('Copying Skills...')
        for eng_skill in Skill.objects.filter(language=english):
            # العثور على الفئة المقابلة بالعربية
            arabic_category = None
            if eng_skill.category:
                try:
                    arabic_category = SkillCategory.objects.get(
                        language=arabic,
                        name=eng_skill.category.name
                    )
                except SkillCategory.DoesNotExist:
                    pass
            
            Skill.objects.get_or_create(
                language=arabic,
                name=eng_skill.name,
                defaults={
                    'category': arabic_category,
                    'proficiency': eng_skill.proficiency,
                    'years_of_experience': eng_skill.years_of_experience,
                    'icon': eng_skill.icon,
                    'description': eng_skill.description,
                    'order': eng_skill.order,
                    'is_active': eng_skill.is_active,
                }
            )
        
        # 6. نسخ الخدمات
        self.stdout.write('Copying Services...')
        for eng_service in Service.objects.filter(language=english):
            Service.objects.get_or_create(
                language=arabic,
                slug=f"{eng_service.slug}-ar",
                defaults={
                    'title': eng_service.title,
                    'short_description': eng_service.short_description,
                    'full_description': eng_service.full_description,
                    'icon': eng_service.icon,
                    'image': eng_service.image,
                    'features': eng_service.features,
                    'meta_title': eng_service.meta_title,
                    'meta_description': eng_service.meta_description,
                    'order': eng_service.order,
                    'is_active': eng_service.is_active,
                    'is_featured': eng_service.is_featured,
                }
            )
        
        # 7. نسخ فئات المشاريع
        self.stdout.write('Copying Portfolio Categories...')
        for eng_cat in PortfolioCategory.objects.filter(language=english):
            PortfolioCategory.objects.get_or_create(
                language=arabic,
                name=eng_cat.name,
                slug=f"{eng_cat.slug}-ar",
                defaults={
                    'order': eng_cat.order,
                }
            )
        
        # 8. نسخ المشاريع
        self.stdout.write('Copying Portfolios...')
        for eng_port in Portfolio.objects.filter(language=english):
            # العثور على الفئة المقابلة بالعربية
            arabic_category = None
            if eng_port.category:
                try:
                    arabic_category = PortfolioCategory.objects.get(
                        language=arabic,
                        name=eng_port.category.name
                    )
                except PortfolioCategory.DoesNotExist:
                    pass
            
            Portfolio.objects.get_or_create(
                language=arabic,
                slug=f"{eng_port.slug}-ar",
                defaults={
                    'title': eng_port.title,
                    'category': arabic_category,
                    'client_name': eng_port.client_name,
                    'project_date': eng_port.project_date,
                    'project_url': eng_port.project_url,
                    'short_description': eng_port.short_description,
                    'overview': eng_port.overview,
                    'challenge': eng_port.challenge,
                    'solution': eng_port.solution,
                    'result': eng_port.result,
                    'cover_image': eng_port.cover_image,
                    'gallery_images': eng_port.gallery_images,
                    'video_url': eng_port.video_url,
                    'technologies': eng_port.technologies,
                    'project_duration': eng_port.project_duration,
                    'team_size': eng_port.team_size,
                    'meta_title': eng_port.meta_title,
                    'meta_description': eng_port.meta_description,
                    'order': eng_port.order,
                    'is_featured': eng_port.is_featured,
                    'is_active': eng_port.is_active,
                }
            )
        
        # 9. نسخ الشهادات
        self.stdout.write('Copying Testimonials...')
        for eng_test in Testimonial.objects.filter(language=english):
            Testimonial.objects.get_or_create(
                language=arabic,
                client_name=eng_test.client_name,
                defaults={
                    'client_position': eng_test.client_position,
                    'client_company': eng_test.client_company,
                    'client_image': eng_test.client_image,
                    'content': eng_test.content,
                    'rating': eng_test.rating,
                    'is_active': eng_test.is_active,
                    'order': eng_test.order,
                }
            )
        
        # 10. نسخ المقالات
        self.stdout.write('Copying Blog Posts...')
        for eng_post in BlogPost.objects.filter(language=english):
            BlogPost.objects.get_or_create(
                language=arabic,
                slug=f"{eng_post.slug}-ar",
                defaults={
                    'title': eng_post.title,
                    'category': None,  # سيتم ربطه لاحقاً
                    'excerpt': eng_post.excerpt,
                    'content': eng_post.content,
                    'featured_image': eng_post.featured_image,
                    'author_name': eng_post.author_name,
                    'author_image': eng_post.author_image,
                    'views_count': eng_post.views_count,
                    'tags': eng_post.tags,
                    'meta_title': eng_post.meta_title,
                    'meta_description': eng_post.meta_description,
                    'is_published': eng_post.is_published,
                    'published_date': eng_post.published_date,
                }
            )
        
        # 11. نسخ القوائم
        self.stdout.write('Copying Menus...')
        for eng_menu in Menu.objects.filter(language=english):
            arabic_menu, created = Menu.objects.get_or_create(
                language=arabic,
                name=eng_menu.name,
                location=eng_menu.location,
                defaults={
                    'is_active': eng_menu.is_active,
                }
            )
            
            # نسخ عناصر القائمة
            for eng_item in MenuItem.objects.filter(menu=eng_menu, parent=None):
                arabic_item, _ = MenuItem.objects.get_or_create(
                    menu=arabic_menu,
                    title=eng_item.title,
                    defaults={
                        'url': eng_item.url,
                        'url_type': eng_item.url_type,
                        'icon': eng_item.icon,
                        'order': eng_item.order,
                        'open_in_new_tab': eng_item.open_in_new_tab,
                        'is_active': eng_item.is_active,
                    }
                )
        
        self.stdout.write(self.style.SUCCESS('Successfully copied all content to Arabic!'))