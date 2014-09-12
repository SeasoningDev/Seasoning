from django import template

register = template.Library()

@register.filter
def remove_protocol(url):
    return url.replace('http:', '')