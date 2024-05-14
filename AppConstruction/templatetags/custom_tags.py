# templatetags/custom_tags.py
from django import template

register = template.Library()


@register.filter
def get_attribute(value, arg):
    """Gets an attribute of an object dynamically."""
    return getattr(value, arg, '')


@register.filter
def get_type(value):
    """Maka type de variable"""
    return type(value).__name__
