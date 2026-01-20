from django import template

register = template.Library()

@register.filter
def mul(value, arg):
    """Nhân hai số với nhau"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def add_num(value, arg):
    return float(value) + float(arg)
