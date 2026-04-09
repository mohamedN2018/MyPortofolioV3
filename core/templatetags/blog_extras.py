from django import template
from django.utils.translation import gettext as _
from django.utils.safestring import mark_safe
import re

register = template.Library()

@register.filter
def divide(value, arg):
    """
    Divide the value by the argument.
    Usage: {{ value|divide:arg }}
    Example: {{ 300|divide:200 }} -> 1
    """
    try:
        # Convert to integers
        val = int(value) if value else 0
        divisor = int(arg) if arg else 1
        if divisor == 0:
            return 1
        result = val // divisor
        return result if result >= 1 else 1
    except (ValueError, TypeError, ZeroDivisionError):
        return 1

@register.filter
def multiply(value, arg):
    """
    Multiply the value by the argument.
    Usage: {{ value|multiply:arg }}
    """
    try:
        val = float(value) if value else 0
        multiplier = float(arg) if arg else 1
        return int(val * multiplier)
    except (ValueError, TypeError):
        return 0

@register.filter
def reading_time(content):
    """
    Calculate reading time based on word count.
    Usage: {{ post.content|reading_time }}
    """
    try:
        # Count words in content
        if content:
            # Remove HTML tags if any
            clean_content = re.sub(r'<[^>]+>', '', str(content))
            word_count = len(clean_content.split())
            # Average reading speed: 200-250 words per minute
            minutes = max(1, round(word_count / 200))
            return minutes
        return 1
    except (ValueError, TypeError, AttributeError):
        return 1

@register.filter
def truncate_chars(value, arg):
    """
    Truncate a string to a specified number of characters.
    Usage: {{ value|truncate_chars:50 }}
    """
    try:
        length = int(arg)
        value_str = str(value)
        if len(value_str) <= length:
            return value_str
        return value_str[:length] + '...'
    except (ValueError, TypeError):
        return value

@register.filter
def get_item(dictionary, key):
    """
    Get an item from a dictionary by key.
    Usage: {{ my_dict|get_item:'key' }}
    """
    try:
        if hasattr(dictionary, 'get'):
            return dictionary.get(key)
        return None
    except (AttributeError, TypeError):
        return None

@register.simple_tag(takes_context=True)
def active_url(context, url_name, active_class='active'):
    """
    Returns active_class if the current URL matches the given url_name.
    Usage: {% active_url request 'home' 'active' %}
    """
    request = context.get('request')
    if request and hasattr(request, 'resolver_match'):
        if request.resolver_match.url_name == url_name:
            return active_class
    return ''

@register.filter
def add_class(field, css_class):
    """
    Add a CSS class to a form field.
    Usage: {{ form.field|add_class:'form-control' }}
    """
    return field.as_widget(attrs={'class': css_class})

@register.filter
def placeholder(field, text):
    """
    Add a placeholder to a form field.
    Usage: {{ form.field|placeholder:'Enter your name' }}
    """
    return field.as_widget(attrs={'placeholder': text})

@register.simple_tag
def query_transform(request, **kwargs):
    """
    Transform query parameters.
    Usage: {% query_transform request page=1 %}
    """
    updated = request.GET.copy()
    for key, value in kwargs.items():
        if value is not None:
            updated[key] = value
        else:
            updated.pop(key, None)
    return updated.urlencode()