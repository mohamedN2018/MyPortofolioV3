"""
أمر لإدخال البيانات الأولية للموقع
الاستخدام: python manage.py seed_data
"""

from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.utils import timezone
from datetime import date, datetime
from django.utils.text import slugify
import json
import os
from decimal import Decimal

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
                'native_name': 'English',
                'is_default': True,
                'is_active': True,
                'direction': 'ltr',
                'flag_icon': 'flag-usa'
            }
        )
        
        arabic, _ = Language.objects.get_or_create(
            code='ar',
            defaults={
                'name': 'العربية',
                'native_name': 'العربية',
                'is_default': False,
                'is_active': True,
                'direction': 'rtl',
                'flag_icon': 'flag-egypt'
            }
        )
        
        # ======================
        # 2. إعدادات الموقع
        # ======================
        self.stdout.write('⚙️ إعداد إعدادات الموقع...')
        
        site_settings, _ = SiteSetting.objects.get_or_create(
            id=1,
            defaults={
                'site_name_ar': 'محمد نبيل | سناب فوليو',
                'site_name_en': 'Mohammed Nabil | SnapFolio',
                'footer_text_ar': 'جميع الحقوق محفوظة © 2025 - تصميم وتطوير محمد نبيل',
                'footer_text_en': 'All Rights Reserved © 2025 - Designed & Developed by Mohammed Nabil',
                'contact_email': 'MohaMedNabiLpro2024@gmail.com',
                'contact_phone': '+20 1060273497',
                'contact_address_ar': 'مصر، القاهرة',
                'contact_address_en': 'Egypt, Cairo',
                'facebook_url': 'https://facebook.com/mohammed.nabil',
                'twitter_url': 'https://twitter.com/mohammed_nabil',
                'linkedin_url': 'https://linkedin.com/in/mohammed-nabil',
                'github_url': 'https://github.com/mohammed-nabil',
                'instagram_url': 'https://instagram.com/mohammed.nabil',
                'default_language': english,
                'enable_rtl': True,
                'maintenance_mode': False,
            }
        )
        
        # ======================
        # 3. المعلومات الشخصية
        # ======================
        self.stdout.write('👤 إضافة المعلومات الشخصية...')
        
        # الإنجليزية
        personal_info_en, _ = PersonalInfo.objects.get_or_create(
            language=english,
            defaults={
                'name': 'Mohammed Nabil',
                'title': 'Backend Developer | Python & Django Expert',
                'bio': '''I'm a passionate Backend Developer specializing in Python and Django with 3+ years of practical experience. I build scalable web applications, RESTful APIs, and robust backend systems.

My journey in programming started with a curiosity for how things work behind the scenes. Since then, I've worked on various projects ranging from educational platforms to job portals and IT service platforms.

I'm committed to writing clean, maintainable, and efficient code. I believe in continuous learning and staying updated with the latest technologies and best practices in backend development.

When I'm not coding, I enjoy contributing to open-source projects, reading tech blogs, and exploring new tools and frameworks that can improve my development workflow.''',
                'short_bio': 'Passionate Backend Developer creating scalable web applications and RESTful APIs with Python & Django.',
                'years_experience': 3,
                'projects_completed': 25,
                'client_satisfaction': 98,
                'happy_clients': 15,
                'keywords': 'Python, Django, Backend Developer, REST API, PostgreSQL, Docker, Web Development',
            }
        )
        
        # العربية
        personal_info_ar, _ = PersonalInfo.objects.get_or_create(
            language=arabic,
            defaults={
                'name': 'محمد نبيل',
                'title': 'مطور باك إند | متخصص في بايثون ودجانجو',
                'bio': '''أنا مطور باك إند متخصص في بايثون ودجانجو مع أكثر من 3 سنوات من الخبرة العملية. أقوم ببناء تطبيقات ويب قابلة للتطوير، وواجهات برمجة تطبيقات RESTful، وأنظمة خلفية قوية.

بدأت رحلتي في البرمجة بدافع الفضول لفهم كيفية عمل الأشياء خلف الكواليس. منذ ذلك الحين، عملت على مشاريع متنوعة تتراوح بين المنصات التعليمية وبوابات التوظيف ومنصات خدمات تكنولوجيا المعلومات.

أنا ملتزم بكتابة كود نظيف وقابل للصيانة وفعال. أؤمن بالتعلم المستمر والبقاء على اطلاع بأحدث التقنيات وأفضل الممارسات في تطوير الباك إند.

عندما لا أكون مشغولاً بالبرمجة، أستمتع بالمساهمة في مشاريع مفتوحة المصدر، وقراءة المدونات التقنية، واستكشاف أدوات وأطر عمل جديدة يمكنها تحسين سير عمل التطوير لدي.''',
                'short_bio': 'مطور باك إند شغوف بإنشاء تطبيقات ويب قابلة للتطوير وواجهات برمجة تطبيقات باستخدام بايثون ودجانجو.',
                'years_experience': 3,
                'projects_completed': 25,
                'client_satisfaction': 98,
                'happy_clients': 15,
                'keywords': 'بايثون، دجانجو، مطور باك إند، REST API، PostgreSQL، دوكر، تطوير ويب',
            }
        )
        
        # ======================
        # 4. التعليم
        # ======================
        self.stdout.write('🎓 إضافة التعليم...')
        
        # الإنجليزية
        Education.objects.get_or_create(
            language=english,
            degree='Diploma in Fine Arts & Graphic Design',
            field_of_study='Decoration & Design',
            institution='Industrial Secondary School',
            start_year=2018,
            end_year=2021,
            is_current=False,
            defaults={
                'description': '''Specialized in Fine Arts and Graphic Design with a strong focus on digital design principles, color theory, typography, and visual communication. 
Graduated with honors and developed a portfolio of design projects including branding, UI/UX, and print media.''',
                'grade': 'Excellent',
                'order': 1,
                'is_active': True
            }
        )
        
        # العربية
        Education.objects.get_or_create(
            language=arabic,
            degree='دبلوم في الفنون الجميلة والجرافيك ديزاين',
            field_of_study='الديكور والتصميم',
            institution='المدرسة الثانوية الصناعية',
            start_year=2018,
            end_year=2021,
            is_current=False,
            defaults={
                'description': '''تخصص في الفنون الجميلة والجرافيك ديزاين مع تركيز قوي على مبادئ التصميم الرقمي، ونظرية الألوان، والطباعة، والتواصل البصري.
تخرجت بتقدير امتياز وقمت بتطوير مجموعة من المشاريع التصميمية تشمل العلامات التجارية، وواجهات المستخدم، ووسائل الطباعة.''',
                'grade': 'امتياز',
                'order': 1,
                'is_active': True
            }
        )
        
        # ======================
        # 5. الخبرات العملية
        # ======================
        self.stdout.write('💼 إضافة الخبرات العملية...')
        
        # الإنجليزية - الخبرة الحالية
        WorkExperience.objects.get_or_create(
            language=english,
            job_title='Freelance Django Developer',
            company_name='Self-employed',
            start_date=date(2023, 1, 1),
            is_current=True,
            defaults={
                'company_website': '',
                'end_date': None,
                'description': '''As a freelance Django developer, I work with clients to build custom web applications, RESTful APIs, and backend systems. I handle everything from requirements gathering to deployment and maintenance.

Key responsibilities include:
- Designing and implementing scalable backend architectures
- Developing RESTful APIs using Django REST Framework
- Integrating third-party services and payment gateways
- Database design and optimization (PostgreSQL, MySQL)
- Containerization with Docker for consistent environments
- Deployment on various platforms (AWS, DigitalOcean, Heroku)''',
                'achievements': [
                    'Successfully delivered 15+ projects for clients worldwide',
                    'Built a knowledge platform handling 1000+ educational resources',
                    'Developed a job portal with 10,000+ job listings and 95% search response under 2 seconds',
                    'Implemented secure authentication and payment integration for e-commerce platforms',
                    'Created reusable component libraries reducing development time by 30%'
                ],
                'technologies': 'Python, Django, DRF, PostgreSQL, MySQL, Redis, Docker, Git, REST APIs',
                'order': 1,
                'is_active': True
            }
        )
        
        # العربية - الخبرة الحالية
        WorkExperience.objects.get_or_create(
            language=arabic,
            job_title='مطور دجانجو مستقل',
            company_name='عمل حر',
            start_date=date(2023, 1, 1),
            is_current=True,
            defaults={
                'company_website': '',
                'end_date': None,
                'description': '''كمطور دجانجو مستقل، أعمل مع العملاء لبناء تطبيقات ويب مخصصة، وواجهات برمجة تطبيقات RESTful، وأنظمة خلفية. أتعامل مع كل شيء بدءاً من جمع المتطلبات وحتى النشر والصيانة.

المسؤوليات الرئيسية تشمل:
- تصميم وتنفيذ هياكل خلفية قابلة للتطوير
- تطوير واجهات برمجة تطبيقات REST باستخدام Django REST Framework
- دمج خدمات الطرف الثالث وبوابات الدفع
- تصميم وتحسين قواعد البيانات (PostgreSQL، MySQL)
- استخدام الحاويات (Docker) لبيئات متسقة
- النشر على منصات متعددة (AWS، DigitalOcean، Heroku)''',
                'achievements': [
                    'نجحت في تسليم أكثر من 15 مشروعاً لعملاء حول العالم',
                    'بناء منصة معرفية تتعامل مع أكثر من 1000 مصدر تعليمي',
                    'تطوير بوابة توظيف تحتوي على أكثر من 10,000 وظيفة واستجابة بحث 95% في أقل من ثانيتين',
                    'تنفيذ توثيق آمن ودمج بوابات الدفع لمنصات التجارة الإلكترونية',
                    'إنشاء مكتبات مكونات قابلة لإعادة الاستخدام قللت وقت التطوير بنسبة 30%'
                ],
                'technologies': 'Python, Django, DRF, PostgreSQL, MySQL, Redis, Docker, Git, REST APIs',
                'order': 1,
                'is_active': True
            }
        )
        
        # ======================
        # 6. فئات المهارات
        # ======================
        self.stdout.write('📚 إضافة فئات المهارات...')
        
        # فئات بالإنجليزية - استخدام get_or_create مع slugs مختلفة
        backend_category, _ = SkillCategory.objects.get_or_create(
            language=english,
            name='Backend Development',
            defaults={
                'icon': 'server',
                'order': 1,
                'is_active': True
            }
        )
        
        frontend_category, _ = SkillCategory.objects.get_or_create(
            language=english,
            name='Frontend Development',
            defaults={
                'icon': 'window',
                'order': 2,
                'is_active': True
            }
        )
        
        database_category, _ = SkillCategory.objects.get_or_create(
            language=english,
            name='Database & DevOps',
            defaults={
                'icon': 'database',
                'order': 3,
                'is_active': True
            }
        )
        
        tools_category, _ = SkillCategory.objects.get_or_create(
            language=english,
            name='Tools & Version Control',
            defaults={
                'icon': 'tools',
                'order': 4,
                'is_active': True
            }
        )
        
        # فئات بالعربية
        SkillCategory.objects.get_or_create(
            language=arabic,
            name='تطوير الباك إند',
            defaults={
                'icon': 'server',
                'order': 1,
                'is_active': True
            }
        )
        
        SkillCategory.objects.get_or_create(
            language=arabic,
            name='تطوير الواجهة الأمامية',
            defaults={
                'icon': 'window',
                'order': 2,
                'is_active': True
            }
        )
        
        SkillCategory.objects.get_or_create(
            language=arabic,
            name='قواعد البيانات و DevOps',
            defaults={
                'icon': 'database',
                'order': 3,
                'is_active': True
            }
        )
        
        SkillCategory.objects.get_or_create(
            language=arabic,
            name='الأدوات والتحكم في الإصدارات',
            defaults={
                'icon': 'tools',
                'order': 4,
                'is_active': True
            }
        )
        
        # ======================
        # 7. المهارات
        # ======================
        self.stdout.write('⚡ إضافة المهارات...')
        
        # المهارات بالإنجليزية
        skills_data_en = [
            # Backend Skills
            {'name': 'Python', 'category': backend_category, 'proficiency': 90, 'years': 3, 'order': 1, 'description': 'Advanced Python programming with focus on clean code and best practices'},
            {'name': 'Django', 'category': backend_category, 'proficiency': 88, 'years': 3, 'order': 2, 'description': 'Expert in Django framework for building scalable web applications'},
            {'name': 'Django REST Framework', 'category': backend_category, 'proficiency': 85, 'years': 2, 'order': 3, 'description': 'Building RESTful APIs with authentication and permissions'},
            {'name': 'FastAPI', 'category': backend_category, 'proficiency': 70, 'years': 1, 'order': 4, 'description': 'Modern and fast Python web framework for building APIs'},
            {'name': 'Flask', 'category': backend_category, 'proficiency': 65, 'years': 1, 'order': 5, 'description': 'Micro-framework for lightweight web applications'},
            # Frontend Skills
            {'name': 'HTML5/CSS3', 'category': frontend_category, 'proficiency': 85, 'years': 3, 'order': 1, 'description': 'Semantic HTML and modern CSS3 including Flexbox and Grid'},
            {'name': 'JavaScript (ES6+)', 'category': frontend_category, 'proficiency': 78, 'years': 2, 'order': 2, 'description': 'Modern JavaScript with async/await, promises, and modules'},
            {'name': 'Bootstrap 5', 'category': frontend_category, 'proficiency': 85, 'years': 3, 'order': 3, 'description': 'Responsive design and components using Bootstrap framework'},
            {'name': 'Tailwind CSS', 'category': frontend_category, 'proficiency': 75, 'years': 2, 'order': 4, 'description': 'Utility-first CSS framework for rapid UI development'},
            {'name': 'Vue.js', 'category': frontend_category, 'proficiency': 65, 'years': 1, 'order': 5, 'description': 'Progressive JavaScript framework for building UIs'},
            {'name': 'jQuery', 'category': frontend_category, 'proficiency': 70, 'years': 2, 'order': 6, 'description': 'DOM manipulation and AJAX requests'},
            # Database & DevOps
            {'name': 'PostgreSQL', 'category': database_category, 'proficiency': 82, 'years': 2, 'order': 1, 'description': 'Advanced PostgreSQL including complex queries and optimization'},
            {'name': 'MySQL', 'category': database_category, 'proficiency': 78, 'years': 2, 'order': 2, 'description': 'Relational database management and optimization'},
            {'name': 'Redis', 'category': database_category, 'proficiency': 70, 'years': 1, 'order': 3, 'description': 'In-memory data structure store for caching and queues'},
            {'name': 'Docker', 'category': database_category, 'proficiency': 75, 'years': 2, 'order': 4, 'description': 'Containerization for consistent development environments'},
            {'name': 'Celery', 'category': database_category, 'proficiency': 68, 'years': 1, 'order': 5, 'description': 'Distributed task queue for background processing'},
            # Tools & Version Control
            {'name': 'Git/GitHub', 'category': tools_category, 'proficiency': 85, 'years': 3, 'order': 1, 'description': 'Version control and collaborative development workflow'},
            {'name': 'Linux/Ubuntu', 'category': tools_category, 'proficiency': 75, 'years': 2, 'order': 2, 'description': 'Server administration and command line proficiency'},
            {'name': 'Postman', 'category': tools_category, 'proficiency': 80, 'years': 2, 'order': 3, 'description': 'API testing and documentation'},
            {'name': 'VS Code', 'category': tools_category, 'proficiency': 85, 'years': 3, 'order': 4, 'description': 'Primary code editor with extensive extensions'},
        ]
        
        for skill in skills_data_en:
            Skill.objects.get_or_create(
                language=english,
                name=skill['name'],
                defaults={
                    'category': skill['category'],
                    'proficiency': skill['proficiency'],
                    'years_of_experience': skill['years'],
                    'description': skill.get('description', ''),
                    'order': skill['order'],
                    'is_active': True
                }
            )
        
        # المهارات بالعربية
        skills_data_ar = [
            # Backend Skills
            {'name': 'بايثون', 'category': backend_category, 'proficiency': 90, 'years': 3, 'order': 1},
            {'name': 'دجانجو', 'category': backend_category, 'proficiency': 88, 'years': 3, 'order': 2},
            {'name': 'إطار عمل دجانجو REST', 'category': backend_category, 'proficiency': 85, 'years': 2, 'order': 3},
            {'name': 'فاست API', 'category': backend_category, 'proficiency': 70, 'years': 1, 'order': 4},
            # Frontend Skills
            {'name': 'HTML5/CSS3', 'category': frontend_category, 'proficiency': 85, 'years': 3, 'order': 1},
            {'name': 'جافا سكريبت', 'category': frontend_category, 'proficiency': 78, 'years': 2, 'order': 2},
            {'name': 'بوستراب 5', 'category': frontend_category, 'proficiency': 85, 'years': 3, 'order': 3},
            {'name': 'تايلويند CSS', 'category': frontend_category, 'proficiency': 75, 'years': 2, 'order': 4},
            # Database & DevOps
            {'name': 'بوستجريSQL', 'category': database_category, 'proficiency': 82, 'years': 2, 'order': 1},
            {'name': 'مايSQL', 'category': database_category, 'proficiency': 78, 'years': 2, 'order': 2},
            {'name': 'ريديس', 'category': database_category, 'proficiency': 70, 'years': 1, 'order': 3},
            {'name': 'دوكر', 'category': database_category, 'proficiency': 75, 'years': 2, 'order': 4},
            # Tools
            {'name': 'جيت/جيت هاب', 'category': tools_category, 'proficiency': 85, 'years': 3, 'order': 1},
            {'name': 'لينكس/أوبونتو', 'category': tools_category, 'proficiency': 75, 'years': 2, 'order': 2},
            {'name': 'بوستمان', 'category': tools_category, 'proficiency': 80, 'years': 2, 'order': 3},
        ]
        
        for skill in skills_data_ar:
            Skill.objects.get_or_create(
                language=arabic,
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
        
        # الخدمات بالإنجليزية
        services_data_en = [
            {
                'title': 'Backend Development',
                'slug': 'backend-development',
                'short_description': 'Scalable and secure backend solutions using Python and Django',
                'full_description': '''I build robust, scalable backend systems using Python and Django. From RESTful APIs to complex business logic, I ensure your application runs smoothly and securely.

**My backend development services include:**
- Custom web application development
- RESTful API design and implementation
- User authentication and authorization systems
- Payment gateway integration
- Third-party API integration
- Performance optimization and caching strategies
- Security implementation and best practices

I follow industry best practices including:
- Clean and maintainable code architecture
- Comprehensive testing (unit, integration)
- Documentation and API specifications
- Version control with Git
- Continuous integration and deployment''',
                'icon': 'code-slash',
                'features': [
                    'RESTful API Development',
                    'Database Design & Optimization',
                    'Authentication & Authorization',
                    'Payment Gateway Integration',
                    'Third-party API Integration',
                    'Performance Optimization',
                    'Security Implementation',
                    'Code Documentation'
                ],
                'order': 1,
                'is_featured': True
            },
            {
                'title': 'Database Design & Optimization',
                'slug': 'database-design-optimization',
                'short_description': 'Efficient database architecture and query optimization',
                'full_description': '''Expert database design and optimization services for PostgreSQL and MySQL databases. I help you build efficient, scalable database architectures that perform well under load.

**What I offer:**
- Database schema design and modeling
- Complex query writing and optimization
- Indexing strategies for performance
- Data migration and transformation
- Backup and recovery strategies
- Database monitoring and maintenance
- Performance tuning and benchmarking
- Data integrity and validation

I ensure your data is organized efficiently, queries run fast, and your database scales with your business growth.''',
                'icon': 'database',
                'features': [
                    'Schema Design & Modeling',
                    'Query Optimization',
                    'Indexing Strategies',
                    'Data Migration',
                    'Backup Strategies',
                    'Performance Tuning',
                    'Data Integrity',
                    'Database Monitoring'
                ],
                'order': 2,
                'is_featured': True
            },
            {
                'title': 'API Development',
                'slug': 'api-development',
                'short_description': 'RESTful APIs and third-party integrations',
                'full_description': '''I design and implement high-quality RESTful APIs using Django REST Framework and FastAPI. My APIs are secure, well-documented, and designed for scalability.

**API development services:**
- RESTful API design following best practices
- API versioning and documentation
- Authentication (JWT, OAuth, Session-based)
- Rate limiting and throttling
- Request/Response caching
- API testing and validation
- Third-party API integration
- Webhook implementation

I provide comprehensive API documentation using tools like Swagger/OpenAPI and Postman collections.''',
                'icon': 'hdd-stack',
                'features': [
                    'REST API Design',
                    'API Documentation (Swagger)',
                    'Authentication & Permissions',
                    'Rate Limiting',
                    'Caching Strategies',
                    'API Testing',
                    'Third-party Integrations',
                    'Webhook Implementation'
                ],
                'order': 3,
                'is_featured': True
            },
            {
                'title': 'Docker & Deployment',
                'slug': 'docker-deployment',
                'short_description': 'Containerization and production deployment',
                'full_description': '''I help you containerize your applications with Docker for consistent development and production environments. I also handle deployment on various cloud platforms.

**DevOps services:**
- Docker containerization for applications
- Docker Compose for multi-container setups
- CI/CD pipeline setup (GitHub Actions, GitLab CI)
- Deployment on cloud platforms (AWS, DigitalOcean, Heroku)
- Server configuration and optimization
- Environment management (development, staging, production)
- SSL certificate setup and HTTPS enforcement
- Application monitoring and logging

I ensure your application is deployed securely and runs reliably in production.''',
                'icon': 'box',
                'features': [
                    'Docker Containerization',
                    'Docker Compose Setup',
                    'CI/CD Pipelines',
                    'Cloud Deployment',
                    'Server Configuration',
                    'Environment Management',
                    'SSL/HTTPS Setup',
                    'Application Monitoring'
                ],
                'order': 4,
                'is_featured': True
            },
            {
                'title': 'Code Review & Optimization',
                'slug': 'code-review-optimization',
                'short_description': 'Clean code practices and performance optimization',
                'full_description': '''I provide professional code review and optimization services to improve your codebase quality, performance, and maintainability.

**Services include:**
- Comprehensive code review and analysis
- Performance profiling and bottleneck identification
- Code refactoring for better maintainability
- Security vulnerability assessment
- Best practices implementation
- Technical debt reduction
- Test coverage improvement
- Documentation enhancement

I help you write cleaner, faster, and more maintainable code that follows industry best practices.''',
                'icon': 'graph-up',
                'features': [
                    'Code Review',
                    'Performance Profiling',
                    'Code Refactoring',
                    'Security Assessment',
                    'Best Practices Implementation',
                    'Technical Debt Reduction',
                    'Test Coverage Improvement',
                    'Documentation Enhancement'
                ],
                'order': 5,
                'is_featured': False
            },
            {
                'title': 'Technical Consulting',
                'slug': 'technical-consulting',
                'short_description': 'Expert advice on technology stack and architecture',
                'full_description': '''I offer technical consulting services to help you make informed decisions about your technology stack, architecture, and development processes.

**Consulting areas:**
- Technology stack selection and evaluation
- System architecture design and review
- Project planning and estimation
- Team training and mentoring
- Development process improvement
- Database design consultation
- API design and strategy
- Performance and scalability planning

I help you build better software by providing expert advice based on real-world experience.''',
                'icon': 'person-workspace',
                'features': [
                    'Tech Stack Selection',
                    'Architecture Review',
                    'Project Planning',
                    'Team Training',
                    'Process Improvement',
                    'Database Consultation',
                    'API Strategy',
                    'Scalability Planning'
                ],
                'order': 6,
                'is_featured': False
            },
        ]
        
        for service_data in services_data_en:
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
                    'is_featured': service_data['is_featured']
                }
            )
        
        # الخدمات بالعربية
        services_data_ar = [
            {
                'title': 'تطوير الباك إند',
                'slug': 'backend-development-ar',
                'short_description': 'حلول خلفية قابلة للتطوير وآمنة باستخدام بايثون ودجانجو',
                'full_description': 'أقوم ببناء أنظمة خلفية قوية وقابلة للتطوير باستخدام بايثون ودجانجو. من واجهات برمجة التطبيقات RESTful إلى منطق الأعمال المعقد، أضمن تشغيل تطبيقك بسلاسة وأمان.',
                'icon': 'code-slash',
                'features': [
                    'تطوير واجهات برمجة تطبيقات RESTful',
                    'تصميم وتحسين قواعد البيانات',
                    'المصادقة والترخيص',
                    'دمج بوابات الدفع',
                    'دمج واجهات برمجة تطبيقات الطرف الثالث',
                    'تحسين الأداء',
                    'تنفيذ الأمان',
                    'توثيق الكود'
                ],
                'order': 1,
                'is_featured': True
            },
            {
                'title': 'تصميم وتحسين قواعد البيانات',
                'slug': 'database-design-ar',
                'short_description': 'هيكلة قاعدة بيانات فعالة وتحسين الاستعلامات',
                'full_description': 'خدمات تصميم وتحسين قواعد بيانات متخصصة لقواعد بيانات PostgreSQL و MySQL. أساعدك في بناء هياكل قواعد بيانات فعالة وقابلة للتطوير تعمل بشكل جيد تحت الضغط.',
                'icon': 'database',
                'features': [
                    'تصميم هيكل قاعدة البيانات',
                    'تحسين الاستعلامات',
                    'استراتيجيات الفهرسة',
                    'ترحيل البيانات',
                    'استراتيجيات النسخ الاحتياطي',
                    'ضبط الأداء',
                    'سلامة البيانات',
                    'مراقبة قاعدة البيانات'
                ],
                'order': 2,
                'is_featured': True
            },
            {
                'title': 'تطوير واجهات برمجة التطبيقات',
                'slug': 'api-development-ar',
                'short_description': 'واجهات برمجة تطبيقات RESTful ودمج خدمات الطرف الثالث',
                'full_description': 'أقوم بتصميم وتنفيذ واجهات برمجة تطبيقات RESTful عالية الجودة باستخدام Django REST Framework و FastAPI. واجهات برمجية آمنة وموثقة جيداً ومصممة للتوسع.',
                'icon': 'hdd-stack',
                'features': [
                    'تصميم واجهات برمجة تطبيقات REST',
                    'توثيق واجهات البرمجة',
                    'المصادقة والأذونات',
                    'تحديد المعدل',
                    'استراتيجيات التخزين المؤقت',
                    'اختبار واجهات البرمجة',
                    'دمج خدمات الطرف الثالث',
                    'تنفيذ Webhook'
                ],
                'order': 3,
                'is_featured': True
            },
            {
                'title': 'الحاويات والنشر',
                'slug': 'docker-deployment-ar',
                'short_description': 'استخدام الحاويات والنشر في بيئة الإنتاج',
                'full_description': 'أساعدك في وضع تطبيقاتك في حاويات باستخدام Docker لبيئات تطوير وإنتاج متسقة. كما أتعامل مع النشر على منصات سحابية مختلفة.',
                'icon': 'box',
                'features': [
                    'وضع التطبيقات في حاويات Docker',
                    'إعداد Docker Compose',
                    'أنابيب CI/CD',
                    'النشر على السحابة',
                    'تكوين الخادم',
                    'إدارة البيئات',
                    'إعداد SSL/HTTPS',
                    'مراقبة التطبيق'
                ],
                'order': 4,
                'is_featured': True
            },
            {
                'title': 'مراجعة وتحسين الكود',
                'slug': 'code-review-ar',
                'short_description': 'ممارسات الكود النظيف وتحسين الأداء',
                'full_description': 'أقدم خدمات مراجعة وتحسين الكود المهنية لتحسين جودة قاعدة الكود الخاصة بك وأدائها وقابليتها للصيانة.',
                'icon': 'graph-up',
                'features': [
                    'مراجعة شاملة للكود',
                    'تحليل الأداء',
                    'إعادة هيكلة الكود',
                    'تقييم الثغرات الأمنية',
                    'تنفيذ أفضل الممارسات',
                    'تقليل الديون التقنية',
                    'تحسين تغطية الاختبارات',
                    'تحسين التوثيق'
                ],
                'order': 5,
                'is_featured': False
            },
            {
                'title': 'استشارات تقنية',
                'slug': 'technical-consulting-ar',
                'short_description': 'نصائح الخبراء حول مجموعة التقنيات والهندسة المعمارية',
                'full_description': 'أقدم خدمات استشارات تقنية لمساعدتك في اتخاذ قرارات مستنيرة بشأن مجموعة التقنيات الخاصة بك والهندسة المعمارية وعمليات التطوير.',
                'icon': 'person-workspace',
                'features': [
                    'اختيار مجموعة التقنيات',
                    'مراجعة الهندسة المعمارية',
                    'تخطيط المشاريع',
                    'تدريب الفريق',
                    'تحسين العمليات',
                    'استشارات قواعد البيانات',
                    'استراتيجية واجهات البرمجة',
                    'تخطيط قابلية التوسع'
                ],
                'order': 6,
                'is_featured': False
            },
        ]
        
        for service_data in services_data_ar:
            service, _ = Service.objects.get_or_create(
                language=arabic,
                slug=service_data['slug'],
                defaults={
                    'title': service_data['title'],
                    'short_description': service_data['short_description'],
                    'full_description': service_data['full_description'],
                    'icon': service_data['icon'],
                    'features': service_data['features'],
                    'order': service_data['order'],
                    'is_active': True,
                    'is_featured': service_data['is_featured']
                }
            )
        
        # ======================
        # 9. المشاريع (Portfolio)
        # ======================
        self.stdout.write('📁 إضافة المشاريع...')
        
        # فئات المشاريع بالإنجليزية - استخدام get_or_create مع slugs فريدة
        web_category, _ = PortfolioCategory.objects.get_or_create(
            language=english,
            slug='web-development',
            defaults={
                'name': 'Web Development',
                'order': 1
            }
        )
        
        backend_category_port, _ = PortfolioCategory.objects.get_or_create(
            language=english,
            slug='backend-systems',
            defaults={
                'name': 'Backend Systems',
                'order': 2
            }
        )
        
        ecommerce_category, _ = PortfolioCategory.objects.get_or_create(
            language=english,
            slug='e-commerce',
            defaults={
                'name': 'E-commerce',
                'order': 3
            }
        )
        
        # فئات المشاريع بالعربية
        PortfolioCategory.objects.get_or_create(
            language=arabic,
            slug='web-development-ar',
            defaults={
                'name': 'تطوير الويب',
                'order': 1
            }
        )
        
        PortfolioCategory.objects.get_or_create(
            language=arabic,
            slug='backend-systems-ar',
            defaults={
                'name': 'أنظمة الباك إند',
                'order': 2
            }
        )
        
        PortfolioCategory.objects.get_or_create(
            language=arabic,
            slug='e-commerce-ar',
            defaults={
                'name': 'التجارة الإلكترونية',
                'order': 3
            }
        )
        
        # المشاريع بالإنجليزية
        projects_data_en = [
            {
                'title': 'Kunooz - Knowledge Platform',
                'slug': 'kunooz-knowledge-platform',
                'category': web_category,
                'client_name': 'Kunooz Education',
                'project_date': date(2025, 12, 1),
                'project_url': 'https://kunooz.example.com',
                'short_description': 'Educational platform for aggregating courses, books, and learning resources',
                'overview': '''Developed a dynamic educational platform for aggregating courses, books, and learning resources. Built scalable backend services using Django, implemented content categorization, search functionality, and optimized database performance.

**Key accomplishments:**
- Architected and implemented a scalable backend using Django
- Created comprehensive content categorization system
- Implemented advanced search with filtering capabilities
- Optimized database queries for fast content retrieval
- Built user authentication and profile management
- Integrated payment gateway for premium content
- Implemented responsive design for all devices''',
                'challenge': 'Managing large volumes of educational content with efficient categorization and fast search capabilities while maintaining performance under heavy load.',
                'solution': 'Implemented Django with PostgreSQL for scalable content management, Redis for caching, and Elasticsearch for fast full-text search across all content types.',
                'result': 'Successfully launched platform with 1000+ educational resources and 500+ active users. Search response time under 500ms and 99.9% uptime.',
                'technologies': ['Python', 'Django', 'PostgreSQL', 'Elasticsearch', 'Redis', 'Docker', 'Bootstrap 5'],
                'features': ['Content Categorization', 'Advanced Search', 'User Authentication', 'Resource Management', 'Payment Integration', 'Analytics Dashboard'],
                'order': 1,
                'is_featured': True,
                'project_duration': '4 months',
                'team_size': 2
            },
            {
                'title': 'NextJobs - Job Portal',
                'slug': 'nextjobs-job-portal',
                'category': web_category,
                'client_name': 'NextJobs Inc.',
                'project_date': date(2025, 10, 15),
                'project_url': 'https://nextjobs.example.com',
                'short_description': 'Job listing and recruitment platform with advanced search',
                'overview': '''Developed a comprehensive job listing and recruitment platform with advanced search and filtering functionality. Implemented user authentication for job seekers and employers, job management system, and scalable database structure.

**Key accomplishments:**
- Built multi-role authentication system (job seekers, employers, admins)
- Implemented advanced job search with multiple filters
- Created resume upload and management system
- Developed application tracking system
- Built company profile pages with job listings
- Implemented email notifications for applications
- Created admin dashboard for platform management''',
                'challenge': 'Building efficient job matching algorithm and handling high traffic with thousands of concurrent users searching and applying for jobs.',
                'solution': 'Used Django with PostgreSQL, implemented Redis caching for frequent queries, and optimized database indexes for fast job search and filtering.',
                'result': 'Platform handles 10,000+ job listings with 95% search response time under 2 seconds. Successfully onboarded 200+ employers and 5,000+ job seekers.',
                'technologies': ['Python', 'Django', 'PostgreSQL', 'Redis', 'Celery', 'Docker', 'Bootstrap 5', 'jQuery'],
                'features': ['Job Search', 'Company Profiles', 'Resume Upload', 'Application Tracking', 'Email Notifications', 'Admin Dashboard', 'Analytics'],
                'order': 2,
                'is_featured': True,
                'project_duration': '5 months',
                'team_size': 3
            },
            {
                'title': 'CodeAnyway - IT Services Platform',
                'slug': 'codeanyway-it-services',
                'category': backend_category_port,
                'client_name': 'CodeAnyway',
                'project_date': date(2025, 8, 20),
                'project_url': 'https://codeanyway.example.com',
                'short_description': 'IT services corporate platform with API infrastructure',
                'overview': '''Implemented robust backend infrastructure and RESTful APIs for an IT services corporate platform. Built comprehensive service management system with client portals and billing integration.

**Key accomplishments:**
- Designed and implemented RESTful API architecture
- Built service catalog and management system
- Created client portal for service requests
- Implemented billing and invoice generation
- Integrated third-party payment gateway
- Developed admin dashboard for service management
- Implemented API authentication with JWT
- Created comprehensive API documentation''',
                'challenge': 'Creating robust API infrastructure capable of handling multiple client services simultaneously with different requirements and service levels.',
                'solution': 'Built RESTful APIs with Django REST Framework with comprehensive documentation, implemented rate limiting, and used Celery for background tasks.',
                'result': 'APIs serving 50+ corporate clients with 99.9% uptime. Successfully processed 10,000+ API requests daily with average response time under 300ms.',
                'technologies': ['Python', 'Django', 'DRF', 'PostgreSQL', 'Celery', 'Redis', 'JWT', 'Docker', 'AWS'],
                'features': ['API Authentication', 'Service Management', 'Client Dashboard', 'Billing System', 'Payment Integration', 'API Documentation', 'Rate Limiting'],
                'order': 3,
                'is_featured': True,
                'project_duration': '6 months',
                'team_size': 4
            },
            {
                'title': 'Outared - Web Service Platform',
                'slug': 'outared-platform',
                'category': backend_category_port,
                'client_name': 'Outared',
                'project_date': date(2025, 6, 10),
                'project_url': 'https://outared.example.com',
                'short_description': 'Core backend components for web service platform',
                'overview': '''Developed core backend components and secured user functionality for a web service platform. Implemented comprehensive security measures and user management system.

**Key accomplishments:**
- Implemented secure user authentication and authorization
- Built role-based access control system
- Created user profile and account management
- Implemented data encryption for sensitive information
- Developed activity logging and audit trail
- Built password reset and email verification
- Implemented session management and security
- Created admin panel for user management''',
                'challenge': 'Implementing secure user authentication and data protection while maintaining good user experience and performance.',
                'solution': 'Used Django\'s built-in authentication system with additional security layers, implemented JWT for API authentication, and used encryption for sensitive data.',
                'result': 'Secure platform handling 5000+ user accounts with zero security incidents. Successfully passed security audit with no critical vulnerabilities.',
                'technologies': ['Python', 'Django', 'PostgreSQL', 'JWT', 'Docker', 'Redis', 'Bootstrap'],
                'features': ['User Authentication', 'Role-Based Access', 'Data Encryption', 'Activity Logging', 'Session Management', 'Password Recovery', 'Email Verification'],
                'order': 4,
                'is_featured': False,
                'project_duration': '3 months',
                'team_size': 1
            },
            {
                'title': 'WordPressNews - News Platform',
                'slug': 'wordpressnews-platform',
                'category': web_category,
                'client_name': 'WordPressNews',
                'project_date': date(2025, 4, 5),
                'project_url': 'https://wordpressnews.example.com',
                'short_description': 'News and articles platform with categorized content',
                'overview': '''Built a dynamic news platform with categorized content delivery, article management system, and scalable backend architecture for high-traffic news delivery.

**Key accomplishments:**
- Built content management system for articles
- Implemented category and tag system
- Created author management and bylines
- Implemented comment system with moderation
- Built search functionality with full-text search
- Created RSS feeds for syndication
- Implemented caching for high traffic
- Built analytics for article views''',
                'challenge': 'Handling real-time news updates and content delivery at scale while maintaining fast page loads and SEO optimization.',
                'solution': 'Implemented caching strategies with Redis, optimized database queries, and used CDN for static assets delivery.',
                'result': 'Platform delivers 100+ news articles daily with sub-second load times. Achieved 500,000+ monthly page views with 99.95% uptime.',
                'technologies': ['Python', 'Django', 'MySQL', 'Redis', 'Celery', 'Docker', 'Tailwind CSS', 'Alpine.js'],
                'features': ['Category Management', 'Article Publishing', 'Comment System', 'Search', 'RSS Feeds', 'Analytics', 'SEO Optimization', 'Caching'],
                'order': 5,
                'is_featured': False,
                'project_duration': '4 months',
                'team_size': 2
            },
            {
                'title': 'BackupManager - Cloud Backup System',
                'slug': 'backupmanager-cloud',
                'category': backend_category_port,
                'client_name': 'BackupManager',
                'project_date': date(2025, 2, 15),
                'project_url': 'https://backupmanager.example.com',
                'short_description': 'Automated cloud backup system with scheduling',
                'overview': '''Developed automated data backup and restore system with secure scheduling, compression, encryption, and REST-based integrations for cloud storage.

**Key accomplishments:**
- Built automated backup scheduler with Celery
- Implemented file compression and encryption
- Created backup verification and integrity checks
- Built restore functionality with versioning
- Integrated multiple cloud storage providers (AWS S3, Google Cloud)
- Created backup monitoring and alerting system
- Built admin dashboard for backup management
- Implemented backup logs and reporting''',
                'challenge': 'Creating reliable backup system with minimal performance impact on production systems while ensuring data integrity and security.',
                'solution': 'Built async backup scheduler with Celery, implemented compression and encryption for secure storage, and created comprehensive monitoring system.',
                'result': 'System backs up 10GB+ data daily with 99.99% success rate. Restore time average under 30 minutes for 1GB of data.',
                'technologies': ['Python', 'Django', 'Celery', 'Redis', 'AWS S3', 'Docker', 'PostgreSQL'],
                'features': ['Automated Backups', 'Scheduled Tasks', 'Restore Functionality', 'Encryption', 'Compression', 'Cloud Storage', 'Monitoring', 'Reporting'],
                'order': 6,
                'is_featured': False,
                'project_duration': '3 months',
                'team_size': 1
            },
        ]
        
        for project_data in projects_data_en:
            portfolio, created = Portfolio.objects.get_or_create(
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
                    'project_duration': project_data.get('project_duration', ''),
                    'team_size': project_data.get('team_size', 1),
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
                        'feature_description': f'{feature_title} functionality implemented with industry best practices and optimized for performance.',
                        'order': i + 1
                    }
                )
        
        # المشاريع بالعربية
        projects_data_ar = [
            {
                'title': 'كنوز - منصة المعرفة',
                'slug': 'kunooz-knowledge-platform-ar',
                'category': web_category,
                'client_name': 'كنوز للتعليم',
                'project_date': date(2025, 12, 1),
                'project_url': 'https://kunooz.example.com',
                'short_description': 'منصة تعليمية لتجميع الدورات والكتب والموارد التعليمية',
                'overview': 'تطوير منصة تعليمية ديناميكية لتجميع الدورات والكتب والموارد التعليمية. بناء خدمات خلفية قابلة للتطوير باستخدام Django، وتنفيذ تصنيف المحتوى، ووظيفة البحث، وتحسين أداء قاعدة البيانات.',
                'challenge': 'إدارة كميات كبيرة من المحتوى التعليمي مع تصنيف فعال وبحث سريع.',
                'solution': 'استخدام Django مع PostgreSQL لإدارة المحتوى القابلة للتطوير، و Redis للتخزين المؤقت، و Elasticsearch للبحث السريع.',
                'result': 'تم إطلاق المنصة بنجاح مع أكثر من 1000 مصدر تعليمي و 500+ مستخدم نشط.',
                'technologies': ['Python', 'Django', 'PostgreSQL', 'Elasticsearch', 'Redis', 'Docker', 'Bootstrap 5'],
                'features': ['تصنيف المحتوى', 'بحث متقدم', 'توثيق المستخدمين', 'إدارة الموارد'],
                'order': 1,
                'is_featured': True,
                'project_duration': '4 أشهر',
                'team_size': 2
            },
            {
                'title': 'NextJobs - بوابة التوظيف',
                'slug': 'nextjobs-job-portal-ar',
                'category': web_category,
                'client_name': 'NextJobs Inc.',
                'project_date': date(2025, 10, 15),
                'project_url': 'https://nextjobs.example.com',
                'short_description': 'منصة توظيف وبحث عن وظائف مع بحث متقدم',
                'overview': 'تطوير منصة توظيف وبحث عن وظائف شاملة مع وظائف بحث وتصفية متقدمة. تنفيذ توثيق المستخدمين ونظام إدارة الوظائف وهيكل قاعدة بيانات قابل للتطوير.',
                'challenge': 'بناء خوارزمية مطابقة وظائف فعالة والتعامل مع حركة المرور العالية.',
                'solution': 'استخدام Django مع PostgreSQL، وتنفيذ Redis للتخزين المؤقت، وتحسين فهارس قاعدة البيانات.',
                'result': 'تتعامل المنصة مع أكثر من 10,000 قائمة وظائف مع وقت استجابة بحث 95% أقل من ثانيتين.',
                'technologies': ['Python', 'Django', 'PostgreSQL', 'Redis', 'Celery', 'Docker', 'Bootstrap 5'],
                'features': ['بحث عن وظائف', 'ملفات تعريف الشركات', 'رفع السيرة الذاتية', 'تتبع التقديمات'],
                'order': 2,
                'is_featured': True,
                'project_duration': '5 أشهر',
                'team_size': 3
            },
            {
                'title': 'كود أنيوي - منصة خدمات تكنولوجيا المعلومات',
                'slug': 'codeanyway-it-services-ar',
                'category': backend_category_port,
                'client_name': 'كود أنيوي',
                'project_date': date(2025, 8, 20),
                'project_url': 'https://codeanyway.example.com',
                'short_description': 'منصة خدمات تكنولوجيا معلومات مع بنية تحتية لواجهات برمجة التطبيقات',
                'overview': 'تنفيذ بنية خلفية قوية وواجهات برمجة تطبيقات RESTful لمنصة خدمات تكنولوجيا معلومات للشركات.',
                'challenge': 'إنشاء بنية تحتية قوية لواجهات برمجة التطبيقات قادرة على التعامل مع خدمات عملاء متعددة.',
                'solution': 'بناء واجهات برمجة تطبيقات REST مع Django REST Framework وتوثيق شامل.',
                'result': 'واجهات برمجة التطبيقات تخدم أكثر من 50 عميلاً من الشركات مع وقت تشغيل 99.9%.',
                'technologies': ['Python', 'Django', 'DRF', 'PostgreSQL', 'Celery', 'Redis', 'JWT', 'Docker'],
                'features': ['توثيق واجهات البرمجة', 'إدارة الخدمات', 'لوحة تحكم العملاء', 'نظام الفواتير'],
                'order': 3,
                'is_featured': True,
                'project_duration': '6 أشهر',
                'team_size': 4
            },
        ]
        
        for project_data in projects_data_ar:
            Portfolio.objects.get_or_create(
                language=arabic,
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
                    'project_duration': project_data.get('project_duration', ''),
                    'team_size': project_data.get('team_size', 1),
                    'is_active': True
                }
            )
        
        # ======================
        # 10. الشهادات (Testimonials)
        # ======================
        self.stdout.write('⭐ إضافة الشهادات...')
        
        # بالإنجليزية
        testimonials_data_en = [
            {
                'client_name': 'Ahmed Khalid',
                'client_position': 'CTO at Kunooz Education',
                'client_company': 'Kunooz Education',
                'content': 'Mohammed delivered exceptional backend work for our educational platform. His Django expertise and attention to detail made the project a huge success. He was responsive, professional, and delivered ahead of schedule.',
                'rating': 5,
                'order': 1
            },
            {
                'client_name': 'Sara Mahmoud',
                'client_position': 'Project Manager at NextJobs Inc.',
                'client_company': 'NextJobs Inc.',
                'content': 'Working with Mohammed was a great experience. He built a robust job portal that handles thousands of users efficiently. His code is clean, well-documented, and he provided excellent support after launch.',
                'rating': 5,
                'order': 2
            },
            {
                'client_name': 'Omar Hassan',
                'client_position': 'Tech Lead at CodeAnyway',
                'client_company': 'CodeAnyway',
                'content': 'Professional and skilled backend developer. His API implementations are clean, well-documented, and scalable. He understands business requirements and translates them into efficient technical solutions.',
                'rating': 5,
                'order': 3
            },
            {
                'client_name': 'Nour El-Din',
                'client_position': 'Founder at Outared',
                'client_company': 'Outared',
                'content': 'Mohammed is reliable and delivers high-quality code. He implemented secure authentication and backend logic perfectly. I would definitely hire him again for future projects.',
                'rating': 4,
                'order': 4
            },
            {
                'client_name': 'Yasmin Ibrahim',
                'client_position': 'Product Owner at WordPressNews',
                'client_company': 'WordPressNews',
                'content': 'Excellent developer who really understands the requirements. He built a high-performance news platform that handles heavy traffic with ease. His problem-solving skills are outstanding.',
                'rating': 5,
                'order': 5
            },
        ]
        
        for testimonial in testimonials_data_en:
            Testimonial.objects.get_or_create(
                language=english,
                client_name=testimonial['client_name'],
                defaults={
                    'client_position': testimonial['client_position'],
                    'client_company': testimonial.get('client_company', ''),
                    'content': testimonial['content'],
                    'rating': testimonial['rating'],
                    'order': testimonial['order'],
                    'is_active': True
                }
            )
        
        # بالعربية
        testimonials_data_ar = [
            {
                'client_name': 'أحمد خالد',
                'client_position': 'مدير التقنية في كنوز للتعليم',
                'client_company': 'كنوز للتعليم',
                'content': 'قدم محمد عملاً استثنائياً في الباك إند لمنصتنا التعليمية. خبرته في Django واهتمامه بالتفاصيل جعل المشروع نجاحاً كبيراً. كان متجاوباً ومهنياً، وسلم العمل قبل الموعد المحدد.',
                'rating': 5,
                'order': 1
            },
            {
                'client_name': 'سارة محمود',
                'client_position': 'مديرة المشاريع في NextJobs Inc.',
                'client_company': 'NextJobs Inc.',
                'content': 'العمل مع محمد كانت تجربة رائعة. قام ببناء بوابة توظيف قوية تتعامل مع آلاف المستخدمين بكفاءة. كوده نظيف وموثق جيداً، وقدم دعماً ممتازاً بعد الإطلاق.',
                'rating': 5,
                'order': 2
            },
            {
                'client_name': 'عمر حسن',
                'client_position': 'قائد تقني في كود أنيوي',
                'client_company': 'كود أنيوي',
                'content': 'مطور محترف وماهر في الباك إند. تطبيقاته لواجهات البرمجة نظيفة وموثقة جيداً وقابلة للتطوير. يفهم متطلبات العمل ويترجمها إلى حلول تقنية فعالة.',
                'rating': 5,
                'order': 3
            },
            {
                'client_name': 'نور الدين',
                'client_position': 'مؤسس في أوتارد',
                'client_company': 'أوتارد',
                'content': 'محمد موثوق ويقدم كوداً عالي الجودة. قام بتنفيذ توثيق آمن ومنطق الباك إند بشكل مثالي. سأوظفه بالتأكيد مرة أخرى للمشاريع القادمة.',
                'rating': 4,
                'order': 4
            },
        ]
        
        for testimonial in testimonials_data_ar:
            Testimonial.objects.get_or_create(
                language=arabic,
                client_name=testimonial['client_name'],
                defaults={
                    'client_position': testimonial['client_position'],
                    'client_company': testimonial.get('client_company', ''),
                    'content': testimonial['content'],
                    'rating': testimonial['rating'],
                    'order': testimonial['order'],
                    'is_active': True
                }
            )
        
        # ======================
        # 11. المقالات (Blog)
        # ======================
        self.stdout.write('📝 إضافة المقالات...')
        
        # فئات المقالات بالإنجليزية
        django_category, _ = BlogCategory.objects.get_or_create(
            language=english,
            slug='django',
            defaults={
                'name': 'Django',
                'description': 'Articles about Django framework development tips and best practices'
            }
        )
        
        python_category, _ = BlogCategory.objects.get_or_create(
            language=english,
            slug='python',
            defaults={
                'name': 'Python',
                'description': 'Python programming tutorials and advanced concepts'
            }
        )
        
        backend_category_blog, _ = BlogCategory.objects.get_or_create(
            language=english,
            slug='backend-development',
            defaults={
                'name': 'Backend Development',
                'description': 'Backend architecture, APIs, and server-side development'
            }
        )
        
        # فئات المقالات بالعربية
        BlogCategory.objects.get_or_create(
            language=arabic,
            slug='django-ar',
            defaults={
                'name': 'دجانجو',
                'description': 'مقالات عن تطوير دجانجو وأفضل الممارسات'
            }
        )
        
        BlogCategory.objects.get_or_create(
            language=arabic,
            slug='python-ar',
            defaults={
                'name': 'بايثون',
                'description': 'دروس برمجة بايثون ومفاهيم متقدمة'
            }
        )
        
        BlogCategory.objects.get_or_create(
            language=arabic,
            slug='backend-development-ar',
            defaults={
                'name': 'تطوير الباك إند',
                'description': 'هندسة الباك إند وواجهات البرمجة وتطوير جانب الخادم'
            }
        )
        
        # المقالات بالإنجليزية
        blog_posts_en = [
            {
                'title': '10 Django Best Practices for Scalable Applications',
                'slug': 'django-best-practices-scalable-applications',
                'category': django_category,
                'excerpt': 'Learn the essential Django best practices that will help you build scalable and maintainable web applications.',
                'content': '''
# 10 Django Best Practices for Scalable Applications

## Introduction
Building scalable applications with Django requires following certain best practices. In this article, I'll share 10 essential practices that have helped me build production-ready applications.

## 1. Use Environment Variables
Never hardcode sensitive information like secret keys, database passwords, or API keys. Use environment variables instead with python-decouple or django-environ.

## 2. Optimize Database Queries
Use `select_related()` and `prefetch_related()` to reduce database queries. Use `only()` and `defer()` to load only needed fields.

## 3. Implement Caching
Use Redis or Memcached to cache expensive queries and API responses. Django's cache framework makes this easy to implement.

## 4. Use Class-Based Views
CBVs provide better code organization and reusability. They also come with built-in functionality for common patterns.

## 5. Write Tests
Write unit tests for your models, views, and forms. Aim for at least 80% test coverage.

## 6. Use Django REST Framework for APIs
DRF provides powerful tools for building RESTful APIs including serializers, authentication, and permissions.

## 7. Implement Logging
Configure proper logging to track errors and monitor application behavior in production.

## 8. Use Middleware Wisely
Custom middleware can help with authentication, logging, and request/response processing.

## 9. Optimize Static Files
Use WhiteNoise or a CDN to serve static files efficiently. Compress and minify CSS and JavaScript.

## 10. Monitor Performance
Use tools like Django Debug Toolbar during development and New Relic or Sentry in production.

## Conclusion
Following these best practices will help you build Django applications that are scalable, maintainable, and production-ready.
                ''',
                'tags': 'Django, Best Practices, Scalability, Web Development',
                'is_published': True,
                'published_date': datetime(2025, 1, 15, 10, 0, 0),
                'order': 1
            },
            {
                'title': 'Understanding Django REST Framework Serializers',
                'slug': 'django-rest-framework-serializers',
                'category': django_category,
                'excerpt': 'A comprehensive guide to understanding and using serializers in Django REST Framework.',
                'content': '''
# Understanding Django REST Framework Serializers

## What are Serializers?
Serializers in DRF allow complex data types (like querysets and model instances) to be converted to JSON, XML, or other content types.

## Types of Serializers

### ModelSerializer
The most commonly used serializer that automatically generates fields based on the model.

### HyperlinkedModelSerializer
Similar to ModelSerializer but uses hyperlinks for relationships instead of primary keys.

### ListSerializer
Used for serializing lists of objects.

## Serializer Methods

### create() and update()
Override these methods to customize object creation and updating.

### validate()
Add custom validation logic for your data.

### to_representation()
Customize how data is output.

## Best Practices

1. Keep serializers focused and single-purpose
2. Use `depth` wisely to avoid infinite recursion
3. Implement custom validation for business rules
4. Use `source` to map different field names
5. Leverage `SerializerMethodField` for computed fields

## Conclusion
Mastering serializers is key to building effective APIs with Django REST Framework.
                ''',
                'tags': 'Django REST Framework, Serializers, API Development',
                'is_published': True,
                'published_date': datetime(2025, 2, 10, 14, 30, 0),
                'order': 2
            },
            {
                'title': 'Optimizing PostgreSQL Queries in Django',
                'slug': 'optimizing-postgresql-queries-django',
                'category': python_category,
                'excerpt': 'Learn how to optimize your PostgreSQL database queries in Django for better performance.',
                'content': '''
# Optimizing PostgreSQL Queries in Django

## Why Query Optimization Matters
Poorly optimized queries can significantly impact application performance. As your data grows, inefficient queries become a bottleneck.

## Tools for Query Analysis

### Django Debug Toolbar
Shows you the number of queries and execution time for each page.

### django-sql-utils
Provides additional tools for analyzing query performance.

### EXPLAIN and ANALYZE
Use PostgreSQL's EXPLAIN to understand how queries are executed.

## Optimization Techniques

### 1. Use Indexes Wisely
Add indexes on columns that are frequently used in WHERE clauses, JOIN conditions, and ORDER BY.

### 2. Avoid N+1 Queries
Use `select_related()` for ForeignKey relationships and `prefetch_related()` for ManyToMany.

### 3. Use Values and ValuesList
Only select the fields you need using `values()` or `values_list()`.

### 4. Batch Operations
Use `bulk_create()` and `bulk_update()` for multiple records.

### 5. Use Raw SQL When Necessary
For complex queries that are hard to express with the ORM, use raw SQL.

## Monitoring in Production
- Set up slow query logging
- Use pg_stat_statements extension
- Monitor connection pool usage

## Conclusion
Regular query optimization is essential for maintaining application performance as your database grows.
                ''',
                'tags': 'PostgreSQL, Django, Database Optimization, Performance',
                'is_published': True,
                'published_date': datetime(2025, 3, 5, 9, 0, 0),
                'order': 3
            },
        ]
        
        for post_data in blog_posts_en:
            BlogPost.objects.get_or_create(
                language=english,
                slug=post_data['slug'],
                defaults={
                    'title': post_data['title'],
                    'category': post_data['category'],
                    'excerpt': post_data['excerpt'],
                    'content': post_data['content'],
                    'author_name': 'Mohammed Nabil',
                    'tags': post_data['tags'],
                    'is_published': post_data['is_published'],
                    'published_date': post_data['published_date'],
                }
            )
        
        # ======================
        # 12. القوائم (Menus)
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
            {'title': 'Home', 'url': '/', 'order': 1, 'icon': 'house'},
            {'title': 'About', 'url': '/about/', 'order': 2, 'icon': 'person'},
            {'title': 'Portfolio', 'url': '/portfolio/', 'order': 3, 'icon': 'images'},
            {'title': 'Services', 'url': '/services/', 'order': 4, 'icon': 'grid'},
            {'title': 'Blog', 'url': '/blog/', 'order': 5, 'icon': 'pen'},
            {'title': 'Contact', 'url': '/contact/', 'order': 6, 'icon': 'envelope'},
        ]
        
        for item in menu_items_en:
            MenuItem.objects.get_or_create(
                menu=main_menu_en,
                title=item['title'],
                defaults={
                    'url': item['url'],
                    'icon': item['icon'],
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
            {'title': 'الرئيسية', 'url': '/', 'order': 1, 'icon': 'house'},
            {'title': 'عني', 'url': '/about/', 'order': 2, 'icon': 'person'},
            {'title': 'أعمالي', 'url': '/portfolio/', 'order': 3, 'icon': 'images'},
            {'title': 'الخدمات', 'url': '/services/', 'order': 4, 'icon': 'grid'},
            {'title': 'المدونة', 'url': '/blog/', 'order': 5, 'icon': 'pen'},
            {'title': 'اتصل بي', 'url': '/contact/', 'order': 6, 'icon': 'envelope'},
        ]
        
        for item in menu_items_ar:
            MenuItem.objects.get_or_create(
                menu=main_menu_ar,
                title=item['title'],
                defaults={
                    'url': item['url'],
                    'icon': item['icon'],
                    'order': item['order'],
                    'is_active': True
                }
            )
        
        # قائمة الفوتر بالإنجليزية
        footer_menu_en, _ = Menu.objects.get_or_create(
            name='Footer Menu',
            location='footer',
            language=english,
            defaults={'is_active': True}
        )
        
        footer_items_en = [
            {'title': 'Privacy Policy', 'url': '/page/privacy-policy/', 'order': 1},
            {'title': 'Terms of Service', 'url': '/page/terms/', 'order': 2},
            {'title': 'Sitemap', 'url': '/sitemap.xml', 'order': 3},
        ]
        
        for item in footer_items_en:
            MenuItem.objects.get_or_create(
                menu=footer_menu_en,
                title=item['title'],
                defaults={
                    'url': item['url'],
                    'order': item['order'],
                    'is_active': True
                }
            )
        
        # ======================
        # 13. الصفحات الثابتة
        # ======================
        self.stdout.write('📄 إضافة الصفحات الثابتة...')
        
        # صفحة سياسة الخصوصية بالإنجليزية
        StaticPage.objects.get_or_create(
            slug='privacy-policy',
            language=english,
            defaults={
                'title': 'Privacy Policy',
                'content': '''
# Privacy Policy

**Last updated:** January 15, 2025

## Introduction
Welcome to Mohammed Nabil's portfolio website. We respect your privacy and are committed to protecting your personal data.

## Information We Collect
We collect information you provide directly to us, such as when you:
- Fill out the contact form
- Subscribe to the newsletter
- Leave a comment on blog posts
- Send us an email

## How We Use Your Information
We use the information we collect to:
- Respond to your inquiries
- Send you updates and newsletters (with your consent)
- Improve our website and services
- Analyze website traffic and user behavior

## Data Security
We implement appropriate technical and organizational measures to protect your personal information against unauthorized access, alteration, disclosure, or destruction.

## Cookies
Our website uses cookies to enhance your browsing experience. You can control cookies through your browser settings.

## Third-Party Services
We may use third-party services like Google Analytics to analyze website traffic. These services have their own privacy policies.

## Your Rights
You have the right to:
- Access your personal data
- Correct inaccurate data
- Request deletion of your data
- Opt-out of marketing communications

## Contact Us
If you have questions about this Privacy Policy, please contact us at MohaMedNabiLpro2024@gmail.com
                ''',
                'show_in_menu': True,
                'menu_order': 10,
                'is_published': True
            }
        )
        
        # صفحة سياسة الخصوصية بالعربية
        StaticPage.objects.get_or_create(
            slug='privacy-policy-ar',
            language=arabic,
            defaults={
                'title': 'سياسة الخصوصية',
                'content': '''
# سياسة الخصوصية

**آخر تحديث:** 15 يناير 2025

## مقدمة
مرحباً بكم في موقع محمد نبيل الشخصي. نحن نحترم خصوصيتكم ونلتزم بحماية بياناتكم الشخصية.

## المعلومات التي نجمعها
نقوم بجمع المعلومات التي تقدمها لنا مباشرة، مثل عندما:
- تملأ نموذج الاتصال
- تشترك في النشرة البريدية
- تترك تعليقاً على مقالات المدونة
- ترسل لنا بريداً إلكترونياً

## كيفية استخدام معلوماتك
نستخدم المعلومات التي نجمعها من أجل:
- الرد على استفساراتك
- إرسال التحديثات والنشرات البريدية (بموافقتك)
- تحسين موقعنا وخدماتنا
- تحليل حركة المرور على الموقع وسلوك المستخدمين

## أمن البيانات
نحن نطبق تدابير تقنية وتنظيمية مناسبة لحماية معلوماتك الشخصية من الوصول غير المصرح به أو التغيير أو الكشف أو التدمير.

## ملفات تعريف الارتباط (Cookies)
يستخدم موقعنا ملفات تعريف الارتباط لتحسين تجربة التصفح الخاصة بك. يمكنك التحكم في ملفات تعريف الارتباط من خلال إعدادات المتصفح الخاص بك.

## خدمات الطرف الثالث
قد نستخدم خدمات طرف ثالث مثل Google Analytics لتحليل حركة المرور على الموقع. هذه الخدمات لها سياسات الخصوصية الخاصة بها.

## حقوقك
لديك الحق في:
- الوصول إلى بياناتك الشخصية
- تصحيح البيانات غير الدقيقة
- طلب حذف بياناتك
- إلغاء الاشتراك في الاتصالات التسويقية

## اتصل بنا
إذا كانت لديك أسئلة حول سياسة الخصوصية هذه، يرجى الاتصال بنا على MohaMedNabiLpro2024@gmail.com
                ''',
                'show_in_menu': True,
                'menu_order': 10,
                'is_published': True
            }
        )
        
        # ======================
        # 14. الأقسام الديناميكية
        # ======================
        self.stdout.write('🏗️ إضافة الأقسام الديناميكية...')
        
        sections_data = [
            {'key': 'hero', 'type': 'hero', 'order': 1},
            {'key': 'about', 'type': 'about', 'order': 2},
            {'key': 'resume', 'type': 'experience', 'order': 3},
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
                    'description': f'This is the {section_data["key"]} section of my portfolio website where I showcase my work and skills.'
                }
            )
            
            # محتوى القسم بالعربية
            arabic_titles = {
                'hero': 'الرئيسية',
                'about': 'من أنا',
                'resume': 'السيرة الذاتية',
                'skills': 'المهارات',
                'portfolio': 'أعمالي',
                'services': 'الخدمات',
                'testimonials': 'آراء العملاء',
                'contact': 'اتصل بي',
            }
            
            SectionContent.objects.get_or_create(
                section=section,
                language=arabic,
                defaults={
                    'title': arabic_titles.get(section_data['key'], section_data['key'].title()),
                    'description': f'هذا هو قسم {arabic_titles.get(section_data["key"], section_data["key"])} في موقع portfolio الخاص بي حيث أعرض أعمالي ومهاراتي.'
                }
            )
        
        # ======================
        # 15. الإعدادات العامة
        # ======================
        self.stdout.write('⚙️ إضافة الإعدادات العامة...')
        
        global_settings_data = [
            {'key': 'site_theme', 'value': 'dark', 'type': 'text', 'description': 'Color theme of the website (dark/light)'},
            {'key': 'items_per_page', 'value': '9', 'type': 'number', 'description': 'Number of items to display per page'},
            {'key': 'enable_animations', 'value': 'true', 'type': 'boolean', 'description': 'Enable/disable AOS animations'},
            {'key': 'enable_comments', 'value': 'true', 'type': 'boolean', 'description': 'Enable/disable blog comments'},
            {'key': 'enable_newsletter', 'value': 'true', 'type': 'boolean', 'description': 'Enable/disable newsletter subscription'},
            {'key': 'contact_form_recipient', 'value': 'MohaMedNabiLpro2024@gmail.com', 'type': 'text', 'description': 'Email address to receive contact form submissions'},
        ]
        
        for setting in global_settings_data:
            GlobalSetting.objects.get_or_create(
                setting_key=setting['key'],
                defaults={
                    'setting_value': setting['value'],
                    'setting_type': setting['type'],
                    'description': setting['description']
                }
            )
        
        # ======================
        # 16. بلوكات قابلة لإعادة الاستخدام
        # ======================
        self.stdout.write('🧩 إضافة البلوكات القابلة لإعادة الاستخدام...')
        
        # CTA Block - English
        ReusableBlock.objects.get_or_create(
            block_key='cta_block',
            language=english,
            defaults={
                'title': 'Ready to Start Your Project?',
                'content': 'Let\'s work together to bring your ideas to life. Contact me today for a free consultation and let\'s discuss how I can help you achieve your goals.',
                'button_text': 'Get In Touch',
                'button_link': '/contact/',
                'is_active': True
            }
        )
        
        # CTA Block - Arabic
        ReusableBlock.objects.get_or_create(
            block_key='cta_block',
            language=arabic,
            defaults={
                'title': 'هل أنت مستعد لبدء مشروعك؟',
                'content': 'دعنا نعمل معاً لتحويل أفكارك إلى واقع. اتصل بي اليوم للحصول على استشارة مجانية ودعنا نناقش كيف يمكنني مساعدتك في تحقيق أهدافك.',
                'button_text': 'اتصل بنا',
                'button_link': '/contact/',
                'is_active': True
            }
        )
        
        # Newsletter Block - English
        ReusableBlock.objects.get_or_create(
            block_key='newsletter_block',
            language=english,
            defaults={
                'title': 'Subscribe to My Newsletter',
                'content': 'Get the latest updates about my work, new blog posts, and tech insights delivered straight to your inbox.',
                'button_text': 'Subscribe',
                'button_link': '#',
                'is_active': True
            }
        )
        
        # Newsletter Block - Arabic
        ReusableBlock.objects.get_or_create(
            block_key='newsletter_block',
            language=arabic,
            defaults={
                'title': 'اشترك في نشرتي البريدية',
                'content': 'احصل على آخر التحديثات حول أعمالي والمقالات الجديدة ورؤى التقنية مباشرة إلى بريدك الوارد.',
                'button_text': 'اشتراك',
                'button_link': '#',
                'is_active': True
            }
        )
        
        # ======================
        # 17. تفاصيل الخدمات الإضافية
        # ======================
        self.stdout.write('📝 إضافة تفاصيل الخدمات...')
        
        # إضافة تفاصيل إضافية للخدمات
        for service in Service.objects.filter(language=english, is_active=True):
            ServiceDetail.objects.get_or_create(
                service=service,
                language=english,
                content_title=f'Why Choose Our {service.title} Service?',
                defaults={
                    'content_body': f'''
Our {service.title} service is designed to deliver high-quality results that meet your specific needs. 

**What makes our service stand out:**

- **Expertise**: Deep knowledge and experience in {service.title.lower()}
- **Quality**: Commitment to delivering clean, maintainable, and efficient code
- **Communication**: Regular updates and transparent communication throughout the project
- **Support**: Ongoing support and maintenance after project completion
- **Best Practices**: Following industry best practices and latest technologies

Whether you need a complete solution or just specific components, I'm here to help you succeed.
                    ''',
                    'points_list': [
                        'Customized solutions tailored to your needs',
                        'Professional and responsive communication',
                        'On-time delivery with attention to detail',
                        'Competitive pricing and flexible engagement',
                        'Post-launch support and maintenance'
                    ],
                    'order': 1
                }
            )
        
        # ======================
        # إحصائيات النهاية
        # ======================
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('✅ تم إدخال جميع البيانات بنجاح!'))
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(self.style.SUCCESS('📊 ملخص البيانات المدخلة:'))
        self.stdout.write(f'   🌐 اللغات: {Language.objects.count()}')
        self.stdout.write(f'   ⚙️ إعدادات الموقع: {SiteSetting.objects.count()}')
        self.stdout.write(f'   👤 المعلومات الشخصية: {PersonalInfo.objects.count()}')
        self.stdout.write(f'   🎓 التعليم: {Education.objects.count()}')
        self.stdout.write(f'   💼 الخبرات: {WorkExperience.objects.count()}')
        self.stdout.write(f'   📚 فئات المهارات: {SkillCategory.objects.count()}')
        self.stdout.write(f'   ⚡ المهارات: {Skill.objects.count()}')
        self.stdout.write(f'   🔧 الخدمات: {Service.objects.count()}')
        self.stdout.write(f'   📝 تفاصيل الخدمات: {ServiceDetail.objects.count()}')
        self.stdout.write(f'   📁 المشاريع: {Portfolio.objects.count()}')
        self.stdout.write(f'   ⭐ الشهادات: {Testimonial.objects.count()}')
        self.stdout.write(f'   📝 المقالات: {BlogPost.objects.count()}')
        self.stdout.write(f'   📋 القوائم: {Menu.objects.count()}')
        self.stdout.write(f'   📄 الصفحات الثابتة: {StaticPage.objects.count()}')
        self.stdout.write(f'   🧩 البلوكات: {ReusableBlock.objects.count()}')
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(self.style.SUCCESS('🎉 يمكنك الآن تشغيل الخادم ومشاهدة الموقع!'))