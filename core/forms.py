from django import forms
from django.utils.translation import gettext_lazy as _
from .models import ContactMessage, ProjectRating
import re

class ContactForm(forms.ModelForm):
    """نموذج الاتصال"""
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Your Name'),
            'required': True
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': _('Your Email'),
            'required': True
        })
    )
    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Your Phone (Optional)')
        })
    )
    subject = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Subject'),
            'required': True
        })
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': _('Your Message'),
            'required': True
        })
    )
    
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'phone', 'subject', 'message']
    
    def clean_name(self):
        """التحقق من صحة الاسم"""
        name = self.cleaned_data.get('name')
        if name and len(name.strip()) < 2:
            raise forms.ValidationError(_('Name must be at least 2 characters long.'))
        if name and len(name.strip()) > 100:
            raise forms.ValidationError(_('Name cannot exceed 100 characters.'))
        return name.strip()
    
    def clean_email(self):
        """التحقق من صحة البريد الإلكتروني"""
        email = self.cleaned_data.get('email')
        if email:
            # التحقق من صيغة البريد
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, email):
                raise forms.ValidationError(_('Please enter a valid email address.'))
        return email.lower()
    
    def clean_phone(self):
        """التحقق من صحة رقم الهاتف"""
        phone = self.cleaned_data.get('phone')
        if phone:
            # السماح بالأرقام والمسافات والشرطات والأقواس
            phone_pattern = r'^[\d\s\+\-\(\)]{5,20}$'
            if not re.match(phone_pattern, phone):
                raise forms.ValidationError(_('Please enter a valid phone number.'))
        return phone
    
    def clean_subject(self):
        """التحقق من صحة الموضوع"""
        subject = self.cleaned_data.get('subject')
        if subject and len(subject.strip()) < 3:
            raise forms.ValidationError(_('Subject must be at least 3 characters long.'))
        if subject and len(subject.strip()) > 200:
            raise forms.ValidationError(_('Subject cannot exceed 200 characters.'))
        return subject.strip()
    
    def clean_message(self):
        """التحقق من صحة الرسالة"""
        message = self.cleaned_data.get('message')
        if message and len(message.strip()) < 10:
            raise forms.ValidationError(_('Message must be at least 10 characters long.'))
        if message and len(message.strip()) > 5000:
            raise forms.ValidationError(_('Message cannot exceed 5000 characters.'))
        return message.strip()


class NewsletterForm(forms.Form):
    """نموذج النشرة البريدية"""
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': _('Your Email Address'),
            'required': True
        })
    )
    
    def clean_email(self):
        """التحقق من صحة البريد"""
        email = self.cleaned_data.get('email')
        if not email:
            raise forms.ValidationError(_('Email is required'))
        
        # التحقق من صيغة البريد
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            raise forms.ValidationError(_('Please enter a valid email address.'))
        
        return email.lower()


class SearchForm(forms.Form):
    """نموذج البحث"""
    query = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Search...')
        })
    )
    search_type = forms.ChoiceField(
        choices=[
            ('all', _('All')),
            ('portfolio', _('Portfolio')),
            ('blog', _('Blog')),
            ('services', _('Services')),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    def clean_query(self):
        """تنظيف نص البحث"""
        query = self.cleaned_data.get('query', '')
        # إزالة المسافات الزائدة
        query = query.strip()
        # إزالة الأحرف الخاصة الخطيرة
        query = re.sub(r'[<>"\']', '', query)
        return query


class CommentForm(forms.Form):
    """نموذج التعليقات للمدونة"""
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Your Name'),
            'required': True
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': _('Your Email'),
            'required': True
        })
    )
    website = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': _('Your Website (Optional)')
        })
    )
    comment = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': _('Your Comment'),
            'required': True
        })
    )
    
    def clean_comment(self):
        comment = self.cleaned_data.get('comment')
        if comment and len(comment.strip()) < 5:
            raise forms.ValidationError(_('Comment must be at least 5 characters long.'))
        return comment.strip()


class SubscribeForm(forms.Form):
    """نموذج الاشتراك في الإشعارات"""
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': _('Enter your email'),
            'required': True
        })
    )
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise forms.ValidationError(_('Email address is required'))
        return email.lower()


class QuickContactForm(forms.Form):
    """نموذج اتصال سريع (للشريط الجانبي)"""
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Your Name')
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': _('Your Email')
        })
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': _('Your Message')
        })
    )


# نموذج للترشيح والفلترة
class FilterForm(forms.Form):
    """نموذج فلترة المحتوى"""
    category = forms.CharField(
        required=False,
        widget=forms.HiddenInput()
    )
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Search...')
        })
    )
    sort_by = forms.ChoiceField(
        choices=[
            ('date_desc', _('Newest First')),
            ('date_asc', _('Oldest First')),
            ('title_asc', _('Title A-Z')),
            ('title_desc', _('Title Z-A')),
        ],
        required=False,
        initial='date_desc',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    per_page = forms.ChoiceField(
        choices=[
            (6, _('6 items')),
            (12, _('12 items')),
            (24, _('24 items')),
            (48, _('48 items')),
        ],
        required=False,
        initial=12,
        widget=forms.Select(attrs={'class': 'form-select'})
    )



# ========== نموذج تقييم المشاريع ==========

class ProjectRatingForm(forms.ModelForm):
    """نموذج إضافة تقييم لمشروع"""
    
    class Meta:
        model = ProjectRating
        fields = ['name', 'email', 'rating', 'comment']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Your Name'),
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': _('Your Email'),
                'required': True
            }),
            'rating': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }, choices=[(i, f"{i} ★") for i in range(1, 6)]),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': _('Share your experience with this project...')
            }),
        }
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        return email.lower()
    
    def clean_comment(self):
        comment = self.cleaned_data.get('comment')
        if comment and len(comment.strip()) < 5:
            raise forms.ValidationError(_('Comment must be at least 5 characters if provided.'))
        return comment.strip() if comment else ''


# نموذج إرسال السيرة الذاتية
class JobApplicationForm(forms.Form):
    """نموذج التقديم على وظيفة"""
    full_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Full Name'),
            'required': True
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': _('Email Address'),
            'required': True
        })
    )
    phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Phone Number'),
            'required': True
        })
    )
    position = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Position Applied For'),
            'required': True
        })
    )
    cover_letter = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 6,
            'placeholder': _('Cover Letter')
        })
    )
    resume = forms.FileField(
        required=True,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.pdf,.doc,.docx'
        })
    )
    portfolio_url = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': _('Portfolio/Website URL (Optional)')
        })
    )
    
    def clean_resume(self):
        resume = self.cleaned_data.get('resume')
        if resume:
            # التحقق من حجم الملف (max 5MB)
            if resume.size > 5 * 1024 * 1024:
                raise forms.ValidationError(_('Resume file size must be less than 5MB.'))
            
            # التحقق من نوع الملف
            file_type = resume.content_type
            allowed_types = ['application/pdf', 'application/msword', 
                           'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
            if file_type not in allowed_types:
                raise forms.ValidationError(_('Only PDF and Word documents are allowed.'))
        return resume