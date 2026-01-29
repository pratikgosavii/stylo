from django import template
from num2words import num2words

register = template.Library()

@register.filter
def in_words(value):
    try:
        return num2words(value, to="cardinal", lang="en_IN").title() + " Only"
    except Exception:
        return value
