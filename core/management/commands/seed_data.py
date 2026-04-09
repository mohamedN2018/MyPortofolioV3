"""
أمر لإدخال البيانات الأولية للموقع
الاستخدام: python manage.py seed_data
"""

from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.utils import timezone
from datetime import date
import json
import os

from core.models import *

class Command(BaseCommand):
    help = 'إدخال البيانات الأولية للموقع (Seed Data)'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('🚀 بدء إدخال البيانات الأولية...'))
        
        # ======================
        # 1. إضافة اللغات
        # ======================
        self.stdout.write('📝 إضافة اللغات...')
        
        english, _ = Language.objects.get_or_create(
            code='en',
            defaults={
                'name': 'English',
                'is_default': True,
                'is_active': True,
                'direction': 'ltr'
            }
        )
        
        arabic, _ = Language.objects.get_or_create(
            code='ar',
            defaults={
                'name': 'العربية',
                'is_default': False,
                'is_active': True,
                'direction': 'rtl'
            }
        )
        
        # ======================
        # 2. إعدادات الموقع
        # ======================
        self.stdout.write('⚙️ إعداد إعدادات الموقع...')
        
        site_settings, _ = SiteSetting.objects.get_or_create(
            id=1,
            defaults={
                'site_name': 'Mohammed Nabil | SnapFolio',
                'contact_email': 'MohaMedNabiLpro2024@gmail.com',
                'contact_phone': '+20 1060273497',
                'contact_address': 'Egypt, Cairo',
                'facebook_url': 'https://facebook.com/',
                'linkedin_url': 'https://linkedin.com/in/',
                'github_url': 'https://github.com/',
                'default_language': english,
                'enable_rtl': True,
                'maintenance_mode': False,
            }
        )
        
        # ======================
        # 3. المعلومات الشخصية (بالإنجليزية)
        # ======================
        self.stdout.write('👤 إضافة المعلومات الشخصية...')
        
        personal_info_en, _ = PersonalInfo.objects.get_or_create(
            language=english,
            defaults={
                'name': 'Mohammed Nabil',
                'title': 'Backend Developer | Python/Django Expert',
                'bio': '''Backend Developer specializing in Python and Django with practical experience in building and maintaining scalable web applications and RESTful APIs. 
Experienced in PostgreSQL, MySQL, and Redis, with hands-on work in integrating payment gateways and third-party APIs. 
Strong understanding of backend architecture, database optimization, and production systems. 
Passionate about writing clean, efficient, and maintainable code.''',
                'short_bio': 'Passionate about creating exceptional digital experiences that blend innovative design with functional development.',
                'years_experience': 3,
                'projects_completed': 25,
                'client_satisfaction': 98,
                'happy_clients': 15,
                'keywords': 'Python, Django, Backend Developer, REST API, PostgreSQL',
            }
        )
        
        # المعلومات الشخصية (بالعربية)
        personal_info_ar, _ = PersonalInfo.objects.get_or_create(
            language=arabic,
            defaults={
                'name': 'محمد نبيل',
                'title': 'مطور باك إند | متخصص في بايثون ودجانجو',
                'bio': '''مطور باك إند متخصص في بايثون ودجانجو مع خبرة عملية في بناء وصيانة تطبيقات الويب القابلة للتطوير وواجهات برمجة التطبيقات RESTful.
خبرة في PostgreSQL و MySQL و Redis، مع عمل عملي في دمج بوابات الدفع وواجهات برمجة التطبيقات الخارجية.
فهم قوي لهندسة الباك إند وتحسين قواعد البيانات وأنظمة الإنتاج.
شغوف بكتابة كود نظيف وفعال وقابل للصيانة.''',
                'short_bio': 'شغوف بإنشاء تجارب رقمية استثنائية تجمع بين التصميم المبتكر والتطوير الوظيفي.',
                'years_experience': 3,
                'projects_completed': 25,
                'client_satisfaction': 98,
                'happy_clients': 15,
                'keywords': 'بايثون، دجانجو، مطور باك إند، REST API، PostgreSQL',
            }
        )
        
        # ======================
        # 4. التعليم
        # ======================
        self.stdout.write('🎓 إضافة التعليم...')
        
        Education.objects.get_or_create(
            language=english,
            degree='Diploma',
            field_of_study='Decoration & Design - Fine Arts & Graphic Design',
            institution='Industrial Secondary School',
            start_year=2018,
            end_year=2021,
            is_current=False,
            description='Specialized in Fine Arts and Graphic Design with focus on digital design principles.',
            order=1,
            is_active=True
        )
        
        Education.objects.get_or_create(
            language=arabic,
            degree='دبلوم',
            field_of_study='الديكور والتصميم - الفنون الجميلة والجرافيك ديزاين',
            institution='المدرسة الثانوية الصناعية',
            start_year=2018,
            end_year=2021,
            is_current=False,
            description='تخصص في الفنون الجميلة والجرافيك ديزاين مع التركيز على مبادئ التصميم الرقمي.',
            order=1,
            is_active=True
        )
        
        # ======================
        # 5. الخبرات العملية
        # ======================
        self.stdout.write('💼 إضافة الخبرات العملية...')
        
        WorkExperience.objects.get_or_create(
            language=english,
            job_title='Freelance Junior Django Developer',
            company_name='Self-employed',
            company_website='',
            start_date=date(2023, 1, 1),
            end_date=None,
            is_current=True,
            description='Developed and deployed multiple web applications using Django and Docker.',
            achievements=[
                'Developed and deployed multiple web applications using Django and Docker',
                'Designed and implemented REST APIs for integration with third-party services',
                'Built responsive UIs with Bootstrap and Tailwind CSS',
                'Collaborated using Git and GitHub for version control'
            ],
            technologies='Python, Django, Docker, REST API, PostgreSQL, Git',
            order=1,
            is_active=True
        )
        
        WorkExperience.objects.get_or_create(
            language=arabic,
            job_title='مطور دجانجو مستقل (Junior)',
            company_name='عمل حر',
            company_website='',
            start_date=date(2023, 1, 1),
            end_date=None,
            is_current=True,
            description='تطوير ونشر تطبيقات ويب متعددة باستخدام Django و Docker.',
            achievements=[
                'تطوير ونشر تطبيقات ويب متعددة باستخدام Django و Docker',
                'تصميم وتنفيذ واجهات برمجة تطبيقات REST للتكامل مع خدمات الطرف الثالث',
                'بناء واجهات مستخدم متجاوبة باستخدام Bootstrap و Tailwind CSS',
                'التعاون باستخدام Git و GitHub للتحكم في الإصدارات'
            ],
            technologies='Python, Django, Docker, REST API, PostgreSQL, Git',
            order=1,
            is_active=True
        )
        
        # ======================
        # 6. فئات المهارات
        # ======================
        self.stdout.write('📚 إضافة فئات المهارات...')
        
        backend_category, _ = SkillCategory.objects.get_or_create(
            language=english,
            name='Backend Development',
            icon='server',
            order=1,
            is_active=True
        )
        
        frontend_category, _ = SkillCategory.objects.get_or_create(
            language=english,
            name='Frontend Development',
            icon='window',
            order=2,
            is_active=True
        )
        
        database_category, _ = SkillCategory.objects.get_or_create(
            language=english,
            name='Database & DevOps',
            icon='database',
            order=3,
            is_active=True
        )
        
        # فئات بالعربية
        SkillCategory.objects.get_or_create(
            language=arabic,
            name='تطوير الباك إند',
            icon='server',
            order=1,
            is_active=True
        )
        
        SkillCategory.objects.get_or_create(
            language=arabic,
            name='تطوير الواجهة الأمامية',
            icon='window',
            order=2,
            is_active=True
        )
        
        SkillCategory.objects.get_or_create(
            language=arabic,
            name='قواعد البيانات و DevOps',
            icon='database',
            order=3,
            is_active=True
        )
        
        # ======================
        # 7. المهارات
        # ======================
        self.stdout.write('⚡ إضافة المهارات...')
        
        skills_data = [
            # Backend Skills
            {'name': 'Python', 'category': backend_category, 'proficiency': 90, 'years': 3, 'order': 1},
            {'name': 'Django', 'category': backend_category, 'proficiency': 85, 'years': 3, 'order': 2},
            {'name': 'Django REST Framework', 'category': backend_category, 'proficiency': 80, 'years': 2, 'order': 3},
            {'name': 'FastAPI', 'category': backend_category, 'proficiency': 70, 'years': 1, 'order': 4},
            # Frontend Skills
            {'name': 'HTML/CSS', 'category': frontend_category, 'proficiency': 85, 'years': 3, 'order': 1},
            {'name': 'JavaScript', 'category': frontend_category, 'proficiency': 75, 'years': 2, 'order': 2},
            {'name': 'Bootstrap', 'category': frontend_category, 'proficiency': 80, 'years': 3, 'order': 3},
            {'name': 'Tailwind CSS', 'category': frontend_category, 'proficiency': 75, 'years': 2, 'order': 4},
            {'name': 'Vue.js', 'category': frontend_category, 'proficiency': 65, 'years': 1, 'order': 5},
            # Database & DevOps
            {'name': 'PostgreSQL', 'category': database_category, 'proficiency': 80, 'years': 2, 'order': 1},
            {'name': 'MySQL', 'category': database_category, 'proficiency': 75, 'years': 2, 'order': 2},
            {'name': 'Redis', 'category': database_category, 'proficiency': 70, 'years': 1, 'order': 3},
            {'name': 'Docker', 'category': database_category, 'proficiency': 75, 'years': 2, 'order': 4},
            {'name': 'Git/GitHub', 'category': database_category, 'proficiency': 85, 'years': 3, 'order': 5},
        ]
        
        for skill in skills_data:
            Skill.objects.get_or_create(
                language=english,
                name=skill['name'],
                defaults={
                    'category': skill['category'],
                    'proficiency': skill['proficiency'],
                    'years_of_experience': skill['years'],
                    'order': skill['order'],
                    'is_active': True
                }
            )
        
        # ======================
        # 8. الخدمات
        # ======================
        self.stdout.write('🔧 إضافة الخدمات...')
        
        services_data = [
            {
                'title': 'Backend Development',
                'slug': 'backend-development',
                'short_description': 'Scalable and secure backend solutions using Python and Django',
                'full_description': 'I build robust, scalable backend systems using Python and Django. From RESTful APIs to complex business logic, I ensure your application runs smoothly and securely.',
                'icon': 'code-slash',
                'features': ['RESTful API Development', 'Database Design', 'Authentication & Authorization', 'Payment Integration'],
                'order': 1
            },
            {
                'title': 'Database Design & Optimization',
                'slug': 'database-design',
                'short_description': 'Efficient database architecture and query optimization',
                'full_description': 'Expert database design with PostgreSQL and MySQL. I optimize queries, design efficient schemas, and ensure data integrity for your applications.',
                'icon': 'database',
                'features': ['Schema Design', 'Query Optimization', 'Data Migration', 'Backup Strategies'],
                'order': 2
            },
            {
                'title': 'API Development',
                'slug': 'api-development',
                'short_description': 'RESTful APIs and third-party integrations',
                'full_description': 'Design and implement RESTful APIs using Django REST Framework. Integration with third-party services and payment gateways.',
                'icon': 'hdd-stack',
                'features': ['REST API Design', 'API Documentation', 'Third-party Integrations', 'Payment Gateways'],
                'order': 3
            },
            {
                'title': 'Docker & Deployment',
                'slug': 'docker-deployment',
                'short_description': 'Containerization and production deployment',
                'full_description': 'Containerize your applications with Docker for consistent development and production environments. Deployment on various platforms.',
                'icon': 'box',
                'features': ['Docker Containerization', 'CI/CD Pipelines', 'Cloud Deployment', 'Production Monitoring'],
                'order': 4
            },
            {
                'title': 'Code Review & Optimization',
                'slug': 'code-optimization',
                'short_description': 'Clean code practices and performance optimization',
                'full_description': 'Review and optimize existing codebases for better performance, maintainability, and scalability.',
                'icon': 'graph-up',
                'features': ['Code Review', 'Performance Tuning', 'Refactoring', 'Best Practices'],
                'order': 5
            },
            {
                'title': 'Technical Consulting',
                'slug': 'technical-consulting',
                'short_description': 'Expert advice on technology stack and architecture',
                'full_description': 'Get expert advice on choosing the right technology stack, architecture decisions, and best practices for your project.',
                'icon': 'person-workspace',
                'features': ['Tech Stack Selection', 'Architecture Review', 'Project Planning', 'Team Training'],
                'order': 6
            },
        ]
        
        for service_data in services_data:
            service, _ = Service.objects.get_or_create(
                language=english,
                slug=service_data['slug'],
                defaults={
                    'title': service_data['title'],
                    'short_description': service_data['short_description'],
                    'full_description': service_data['full_description'],
                    'icon': service_data['icon'],
                    'features': service_data['features'],
                    'order': service_data['order'],
                    'is_active': True,
                    'is_featured': service_data['order'] <= 3
                }
            )
        
        # ======================
        # 9. المشاريع (Portfolio)
        # ======================
        self.stdout.write('📁 إضافة المشاريع...')
        
        # فئات المشاريع
        web_category, _ = PortfolioCategory.objects.get_or_create(
            language=english,
            name='Web Development',
            slug='web-development',
            order=1
        )
        
        backend_category_port, _ = PortfolioCategory.objects.get_or_create(
            language=english,
            name='Backend Systems',
            slug='backend-systems',
            order=2
        )
        
        projects_data = [
            {
                'title': 'Kunooz - Knowledge Platform',
                'slug': 'kunooz-knowledge-platform',
                'category': web_category,
                'client_name': 'Kunooz Education',
                'project_date': date(2025, 12, 1),
                'project_url': 'https://kunooz.example.com',
                'short_description': 'Educational platform for aggregating courses, books, and learning resources',
                'overview': 'Developed a dynamic educational platform for aggregating courses, books, and learning resources. Built scalable backend services using Django, implemented content categorization, search functionality, and optimized database performance.',
                'challenge': 'Managing large volumes of educational content with efficient categorization and search.',
                'solution': 'Implemented Django with PostgreSQL for scalable content management and Elasticsearch for fast search.',
                'result': 'Successfully launched platform with 1000+ educational resources and 500+ active users.',
                'technologies': ['Python', 'Django', 'PostgreSQL', 'Elasticsearch', 'Docker'],
                'features': ['Content Categorization', 'Advanced Search', 'User Authentication', 'Resource Management'],
                'order': 1,
                'is_featured': True
            },
            {
                'title': 'NextJobs - Job Portal',
                'slug': 'nextjobs-job-portal',
                'category': web_category,
                'client_name': 'NextJobs Inc.',
                'project_date': date(2025, 10, 15),
                'project_url': 'https://nextjobs.example.com',
                'short_description': 'Job listing and recruitment platform with advanced search',
                'overview': 'Developed a job listing and recruitment platform with advanced search and filtering functionality. Implemented user authentication, job management system, and scalable database structure.',
                'challenge': 'Building efficient job matching algorithm and handling high traffic.',
                'solution': 'Used Django with Redis caching and optimized database queries for fast job search.',
                'result': 'Platform handles 10,000+ job listings with 95% search response time under 2 seconds.',
                'technologies': ['Python', 'Django', 'PostgreSQL', 'Redis', 'Bootstrap'],
                'features': ['Job Search', 'Company Profiles', 'Resume Upload', 'Application Tracking'],
                'order': 2,
                'is_featured': True
            },
            {
                'title': 'CodeAnyway - IT Services',
                'slug': 'codeanyway-it-services',
                'category': backend_category_port,
                'client_name': 'CodeAnyway',
                'project_date': date(2025, 8, 20),
                'project_url': 'https://codeanyway.example.com',
                'short_description': 'IT services corporate platform with API infrastructure',
                'overview': 'Implemented backend infrastructure and APIs for an IT services corporate platform.',
                'challenge': 'Creating robust API infrastructure for multiple client services.',
                'solution': 'Built RESTful APIs with Django REST Framework with comprehensive documentation.',
                'result': 'APIs serving 50+ corporate clients with 99.9% uptime.',
                'technologies': ['Python', 'Django', 'DRF', 'PostgreSQL', 'JWT'],
                'features': ['API Authentication', 'Service Management', 'Client Dashboard', 'Billing System'],
                'order': 3,
                'is_featured': True
            },
            {
                'title': 'Outared - Web Service Platform',
                'slug': 'outared-platform',
                'category': backend_category_port,
                'client_name': 'Outared',
                'project_date': date(2025, 6, 10),
                'short_description': 'Core backend components for web service platform',
                'overview': 'Developed core backend components and secured user functionality for a web service platform.',
                'challenge': 'Implementing secure user authentication and data protection.',
                'solution': 'Used Django\'s built-in auth system with additional security layers and JWT.',
                'result': 'Secure platform handling 5000+ user accounts with zero security incidents.',
                'technologies': ['Python', 'Django', 'PostgreSQL', 'JWT', 'Docker'],
                'features': ['User Authentication', 'Role-Based Access', 'Data Encryption', 'Activity Logging'],
                'order': 4,
                'is_featured': False
            },
            {
                'title': 'WordPressNews - News Platform',
                'slug': 'wordpressnews-platform',
                'category': web_category,
                'client_name': 'WordPressNews',
                'project_date': date(2025, 4, 5),
                'short_description': 'News and articles platform with categorized content',
                'overview': 'Built a dynamic news platform with categorized content delivery, article management, and scalable backend architecture.',
                'challenge': 'Handling real-time news updates and content delivery at scale.',
                'solution': 'Implemented caching strategies and optimized database queries for fast content delivery.',
                'result': 'Platform delivers 100+ news articles daily with sub-second load times.',
                'technologies': ['Python', 'Django', 'MySQL', 'Redis', 'Tailwind CSS'],
                'features': ['Category Management', 'Article Publishing', 'Comment System', 'Search'],
                'order': 5,
                'is_featured': False
            },
            {
                'title': 'BackupManager - Cloud Backup',
                'slug': 'backupmanager-cloud',
                'category': backend_category_port,
                'client_name': 'BackupManager',
                'project_date': date(2025, 2, 15),
                'short_description': 'Automated cloud backup system with scheduling',
                'overview': 'Developed automated data backup & restore logic with secure scheduling and REST-based integrations.',
                'challenge': 'Creating reliable backup system with minimal performance impact.',
                'solution': 'Built async backup scheduler with compression and encryption for secure storage.',
                'result': 'System backs up 10GB+ data daily with 99.99% success rate.',
                'technologies': ['Python', 'Django', 'Celery', 'Redis', 'AWS S3'],
                'features': ['Automated Backups', 'Scheduled Tasks', 'Restore Functionality', 'Encryption'],
                'order': 6,
                'is_featured': False
            },
        ]
        
        for project_data in projects_data:
            portfolio, _ = Portfolio.objects.get_or_create(
                language=english,
                slug=project_data['slug'],
                defaults={
                    'title': project_data['title'],
                    'category': project_data['category'],
                    'client_name': project_data['client_name'],
                    'project_date': project_data['project_date'],
                    'project_url': project_data.get('project_url', ''),
                    'short_description': project_data['short_description'],
                    'overview': project_data['overview'],
                    'challenge': project_data.get('challenge', ''),
                    'solution': project_data.get('solution', ''),
                    'result': project_data.get('result', ''),
                    'technologies': project_data['technologies'],
                    'order': project_data['order'],
                    'is_featured': project_data['is_featured'],
                    'is_active': True
                }
            )
            
            # إضافة ميزات المشروع
            for i, feature_title in enumerate(project_data.get('features', [])):
                PortfolioFeature.objects.get_or_create(
                    portfolio=portfolio,
                    language=english,
                    feature_title=feature_title,
                    defaults={
                        'feature_description': f'{feature_title} functionality implemented with best practices.',
                        'order': i + 1
                    }
                )
        
        # ======================
        # 10. الشهادات (Testimonials)
        # ======================
        self.stdout.write('⭐ إضافة الشهادات...')
        
        testimonials_data = [
            {
                'client_name': 'Ahmed Khalid',
                'client_position': 'CTO at Kunooz',
                'content': 'Mohammed delivered exceptional backend work for our educational platform. His Django expertise and attention to detail made the project a huge success.',
                'rating': 5,
                'order': 1
            },
            {
                'client_name': 'Sara Mahmoud',
                'client_position': 'Project Manager at NextJobs',
                'content': 'Working with Mohammed was a great experience. He built a robust job portal that handles thousands of users efficiently.',
                'rating': 5,
                'order': 2
            },
            {
                'client_name': 'Omar Hassan',
                'client_position': 'Tech Lead at CodeAnyway',
                'content': 'Professional and skilled backend developer. His API implementations are clean, well-documented, and scalable.',
                'rating': 5,
                'order': 3
            },
            {
                'client_name': 'Nour El-Din',
                'client_position': 'Founder at Outared',
                'content': 'Mohammed is reliable and delivers high-quality code. He implemented secure authentication and backend logic perfectly.',
                'rating': 4,
                'order': 4
            },
        ]
        
        for testimonial in testimonials_data:
            Testimonial.objects.get_or_create(
                language=english,
                client_name=testimonial['client_name'],
                defaults={
                    'client_position': testimonial['client_position'],
                    'content': testimonial['content'],
                    'rating': testimonial['rating'],
                    'order': testimonial['order'],
                    'is_active': True
                }
            )
        
        # ======================
        # 11. القوائم (Menus)
        # ======================
        self.stdout.write('📋 إضافة القوائم...')
        
        # القائمة الرئيسية بالإنجليزية
        main_menu_en, _ = Menu.objects.get_or_create(
            name='Main Menu',
            location='header',
            language=english,
            defaults={'is_active': True}
        )
        
        menu_items_en = [
            {'title': 'Home', 'url': '/#hero', 'order': 1},
            {'title': 'About', 'url': '/#about', 'order': 2},
            {'title': 'Resume', 'url': '/#resume', 'order': 3},
            {'title': 'Portfolio', 'url': '/portfolio/', 'order': 4},
            {'title': 'Services', 'url': '/services/', 'order': 5},
            {'title': 'Blog', 'url': '/blog/', 'order': 6},
            {'title': 'Contact', 'url': '/contact/', 'order': 7},
        ]
        
        for item in menu_items_en:
            MenuItem.objects.get_or_create(
                menu=main_menu_en,
                title=item['title'],
                defaults={
                    'url': item['url'],
                    'order': item['order'],
                    'is_active': True
                }
            )
        
        # القائمة الرئيسية بالعربية
        main_menu_ar, _ = Menu.objects.get_or_create(
            name='القائمة الرئيسية',
            location='header',
            language=arabic,
            defaults={'is_active': True}
        )
        
        menu_items_ar = [
            {'title': 'الرئيسية', 'url': '/#hero', 'order': 1},
            {'title': 'عن الموقع', 'url': '/#about', 'order': 2},
            {'title': 'السيرة الذاتية', 'url': '/#resume', 'order': 3},
            {'title': 'المشاريع', 'url': '/portfolio/', 'order': 4},
            {'title': 'الخدمات', 'url': '/services/', 'order': 5},
            {'title': 'المدونة', 'url': '/blog/', 'order': 6},
            {'title': 'اتصل بنا', 'url': '/contact/', 'order': 7},
        ]
        
        for item in menu_items_ar:
            MenuItem.objects.get_or_create(
                menu=main_menu_ar,
                title=item['title'],
                defaults={
                    'url': item['url'],
                    'order': item['order'],
                    'is_active': True
                }
            )
        
        # ======================
        # 12. الصفحات الثابتة
        # ======================
        self.stdout.write('📄 إضافة الصفحات الثابتة...')
        
        StaticPage.objects.get_or_create(
            slug='privacy-policy',
            language=english,
            defaults={
                'title': 'Privacy Policy',
                'content': '''
# Privacy Policy

Last updated: January 2025

## Information We Collect
We collect information you provide directly to us, such as when you create an account, fill out a form, or send us a message.

## How We Use Your Information
We use the information we collect to provide, maintain, and improve our services, and to communicate with you.

## Data Security
We implement appropriate technical and organizational measures to protect your personal information.

## Contact Us
If you have questions about this Privacy Policy, please contact us at MohaMedNabiLpro2024@gmail.com
                ''',
                'show_in_menu': True,
                'menu_order': 10,
                'is_published': True
            }
        )
        
        # ======================
        # 13. الأقسام الديناميكية
        # ======================
        self.stdout.write('🏗️ إضافة الأقسام الديناميكية...')
        
        sections_data = [
            {'key': 'hero', 'type': 'hero', 'order': 1},
            {'key': 'about', 'type': 'about', 'order': 2},
            {'key': 'resume', 'type': 'resume', 'order': 3},
            {'key': 'skills', 'type': 'skills', 'order': 4},
            {'key': 'portfolio', 'type': 'portfolio', 'order': 5},
            {'key': 'services', 'type': 'services', 'order': 6},
            {'key': 'testimonials', 'type': 'testimonials', 'order': 7},
            {'key': 'contact', 'type': 'contact', 'order': 8},
        ]
        
        for section_data in sections_data:
            section, _ = DynamicSection.objects.get_or_create(
                section_key=section_data['key'],
                defaults={
                    'section_type': section_data['type'],
                    'order': section_data['order'],
                    'is_active': True
                }
            )
            
            # محتوى القسم بالإنجليزية
            SectionContent.objects.get_or_create(
                section=section,
                language=english,
                defaults={
                    'title': section_data['key'].title(),
                    'description': f'This is the {section_data["key"]} section of my portfolio website.'
                }
            )
            
            # محتوى القسم بالعربية
            arabic_titles = {
                'hero': 'الرئيسية',
                'about': 'عن الموقع',
                'resume': 'السيرة الذاتية',
                'skills': 'المهارات',
                'portfolio': 'المشاريع',
                'services': 'الخدمات',
                'testimonials': 'آراء العملاء',
                'contact': 'اتصل بنا',
            }
            
            SectionContent.objects.get_or_create(
                section=section,
                language=arabic,
                defaults={
                    'title': arabic_titles.get(section_data['key'], section_data['key'].title()),
                    'description': f'هذا هو قسم {arabic_titles.get(section_data["key"], section_data["key"])} في موقع portfolio الخاص بي.'
                }
            )
        
        # ======================
        # 14. الإعدادات العامة
        # ======================
        self.stdout.write('⚙️ إضافة الإعدادات العامة...')
        
        GlobalSetting.objects.get_or_create(
            setting_key='site_theme',
            defaults={
                'setting_value': 'dark',
                'setting_type': 'text',
                'description': 'Color theme of the website (dark/light)'
            }
        )
        
        GlobalSetting.objects.get_or_create(
            setting_key='items_per_page',
            defaults={
                'setting_value': '9',
                'setting_type': 'number',
                'description': 'Number of items to display per page'
            }
        )
        
        GlobalSetting.objects.get_or_create(
            setting_key='enable_animations',
            defaults={
                'setting_value': 'true',
                'setting_type': 'boolean',
                'description': 'Enable/disable AOS animations'
            }
        )
        
        # ======================
        # 15. بلوكات قابلة لإعادة الاستخدام
        # ======================
        self.stdout.write('🧩 إضافة البلوكات القابلة لإعادة الاستخدام...')
        
        ReusableBlock.objects.get_or_create(
            block_key='cta_block',
            language=english,
            defaults={
                'title': 'Ready to Start Your Project?',
                'content': 'Let\'s work together to bring your ideas to life. Contact me today for a free consultation.',
                'button_text': 'Get In Touch',
                'button_link': '/contact/',
                'is_active': True
            }
        )
        
        ReusableBlock.objects.get_or_create(
            block_key='cta_block',
            language=arabic,
            defaults={
                'title': 'هل أنت مستعد لبدء مشروعك؟',
                'content': 'دعنا نعمل معاً لتحويل أفكارك إلى واقع. اتصل بي اليوم للحصول على استشارة مجانية.',
                'button_text': 'اتصل بنا',
                'button_link': '/contact/',
                'is_active': True
            }
        )
        
        self.stdout.write(self.style.SUCCESS('✅ تم إدخال جميع البيانات بنجاح!'))
        self.stdout.write(self.style.SUCCESS('📊 ملخص البيانات المدخلة:'))
        self.stdout.write(f'   - اللغات: 2')
        self.stdout.write(f'   - المشاريع: {Portfolio.objects.count()}')
        self.stdout.write(f'   - الخدمات: {Service.objects.count()}')
        self.stdout.write(f'   - المهارات: {Skill.objects.count()}')
        self.stdout.write(f'   - الشهادات: {Testimonial.objects.count()}')
        self.stdout.write(f'   - الخبرات: {WorkExperience.objects.count()}')
        self.stdout.write(f'   - التعليم: {Education.objects.count()}')