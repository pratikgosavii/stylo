# vendor/templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter
def replace_underscore(value):
    return value.replace("_", " ").title()

@register.filter
def get_attr(obj, attr_name):
    return getattr(obj, attr_name, False)