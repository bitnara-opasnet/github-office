from django import template

register = template.Library()


@register.filter
def replace_str(value, arg1):
    return value.replace(arg1, "*")