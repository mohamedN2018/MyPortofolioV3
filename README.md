# Mohamed NabiL - Personal Portfolio Website

موقع محفظتي الشخصية (Personal Portfolio) كمطور Backend متخصص في Python و Django. يعرض الموقع مهاراتي التقنية، خبراتي المهنية، مشاريعي، الخدمات التي أقدمها، وشهادات العملاء، مع إمكانية التواصل عبر نموذج اتصال مباشر.

## ✨ المميزات

- تصميم متجاوب بالكامل (Fully Responsive) – يعمل على الحواسب، الأجهزة اللوحية، والهواتف
- واجهة نظيفة واحترافية – ألوان مريحة وتنسيق حديث
- عرض المهارات بنسب مئوية – توضيح مستوى الإتقان لكل تقنية
- قسم المشاريع (Portfolio) – جاهز لعرض الأعمال السابقة
- قسم الخدمات (Services) – شرح للخدمات المقدمة
- شهادات العملاء (Testimonials) – آراء حقيقية تزيد المصداقية
- نموذج اتصال فعال – مع رسالة تأكيد عند الإرسال
- سهولة التخصيص – كل المحتوى قابل للتعديل بسهولة

## 🛠️ التقنيات المستخدمة

**Backend:** Python, Django, Django REST Framework

**Frontend:** HTML5, CSS3, Bootstrap 5, JavaScript, Tailwind CSS, Vue.js

**قواعد البيانات:** PostgreSQL, MySQL, SQLite, Redis

**أدوات وتطوير:** Git, GitHub, Docker, Celery, Postman, Linux/Ubuntu

**النشر:** Render, Gunicorn, WhiteNoise

## 📁 هيكل المشروع
portfolio_project/
│
├── manage.py
├── db.sqlite3
├── requirements.txt
├── .env.example
│
├── portfolio_project/
│ ├── settings.py
│ ├── urls.py
│ └── wsgi.py
│
├── portfolio/
│ ├── views.py
│ ├── models.py
│ ├── forms.py
│ ├── urls.py
│ ├── templates/
│ │ └── portfolio/
│ │ └── index.html
│ └── static/
│ └── portfolio/
│ ├── css/
│ ├── js/
│ └── images/
│
└── staticfiles/

text

## 📦 متطلبات التشغيل

- Python 3.8 أو أحدث
- pip (مدير حزم Python)
- virtualenv (موصى به)
- Git

## 🔧 طريقة التشغيل محلياً

### 1. استنساخ المستودع
```bash
git clone https://github.com/your-username/your-portfolio-repo.git
cd your-portfolio-repo
2. إنشاء وتفعيل البيئة الافتراضية
bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
3. تثبيت الاعتماديات
bash
pip install --upgrade pip
pip install -r requirements.txt
4. إعداد متغيرات البيئة
bash
cp .env.example .env
# ثم قم بتعديل ملف .env وأضف الـ SECRET_KEY الخاص بك
5. إنشاء الملفات الثابتة وتطبيق التغييرات على قاعدة البيانات
bash
python manage.py collectstatic --noinput
python manage.py migrate
6. تشغيل الخادم المحلي
bash
python manage.py runserver
7. فتح المتصفح
اذهب إلى: http://127.0.0.1:8000

📝 إنشاء ملف requirements.txt
إذا لم يكن لديك ملف requirements.txt بعد، قم بإنشائه باستخدام:

bash
pip freeze > requirements.txt
ومحتوياته المتوقعة:

text
Django==4.2.0
psycopg2-binary==2.9.6
redis==4.5.4
celery==5.3.1
gunicorn==20.1.0
whitenoise==6.4.0
python-dotenv==1.0.0
Pillow==9.5.0
🌐 النشر على الإنترنت (Deployment)
الخيار الأول: Render (مجاني - مستخدم حالياً)
ارفع الكود إلى GitHub

أنشئ حساباً على Render.com

اختر "New Web Service" واربطه بمستودع GitHub

اضبط الإعدادات:

Build Command: pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate

Start Command: gunicorn portfolio_project.wsgi:application

أضف متغيرات البيئة:

SECRET_KEY = مفتاح سري قوي

DEBUG = False

ALLOWED_HOSTS = .onrender.com, yourdomain.com

انقر "Deploy"

الخيار الثاني: PythonAnywhere
bash
# اتبع الدليل الرسمي:
# https://help.pythonanywhere.com/pages/DeployExistingDjangoProject/
الخيار الثالث: VPS (DigitalOcean, Linode)
bash
# باستخدام Docker
docker build -t portfolio .
docker run -d -p 8000:8000 portfolio

# أو باستخدام Nginx + Gunicorn
# راجع ملف deployment.md لمزيد من التفاصيل
📝 كيفية التخصيص
تعديل المحتوى النصي والمهارات
افتح ملف templates/portfolio/index.html وعدّل الأقسام مباشرة:

html
<!-- تعديل نسبة المهارة -->
<div class="skill-item">
    <span>Python</span>
    <div class="progress">
        <div class="progress-bar" style="width: 90%">90%</div>
    </div>
</div>
تغيير الصور
استبدل الملفات في مجلد static/portfolio/images/

تعديل الألوان والخطوط
افتح ملف static/portfolio/css/style.css وعدّل المتغيرات:

css
:root {
    --primary-color: #0d6efd;
    --secondary-color: #6c757d;
    --dark-bg: #1a1a2e;
}
تفعيل نموذج الاتصال لإرسال البريد الإلكتروني
في ملف settings.py:

python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
🗺️ مسار الموقع الحالي
الموقع منشور حالياً على:
https://mohamednabilpro.deplois.net

📞 معلومات التواصل
البريد الإلكتروني: MohamedNabilpro2024@gmail.com

رقم الهاتف/واتساب: +20 1060273497

الموقع: نيويورك، الولايات المتحدة الأمريكية

📄 الترخيص
هذا المشروع مرخص تحت رخصة MIT – يمكنك استخدامه وتعديله بحرية مع الإشارة إلى المصدر الأصلي.

text
MIT License

Copyright (c) 2024 Mohamed NabiL

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files...
🤝 المساهمة
المشروع مفتوح المصدر، مرحب بمساهماتكم:

Fork المشروع

أنشئ فرع جديد للميزة (git checkout -b feature/AmazingFeature)

Commit التغييرات (git commit -m 'Add some AmazingFeature')

Push إلى الفرع (git push origin feature/AmazingFeature)

افتح Pull Request

🐛 الإبلاغ عن مشاكل
إذا وجدت أي خطأ أو لديك اقتراح، يرجى فتح Issue في GitHub مع وصف المشكلة وخطوات إعادة إنتاجها.

⭐ دعم المشروع
إذا أعجبك هذا المشروع، لا تتردد في منحه نجمة على GitHub ⭐

شكراً لزيارتك ملفي الشخصي! 🚀

text

هذا هو الملف الكامل، فقط انسخه والصقه في ملف `README.md` الخاص بك.