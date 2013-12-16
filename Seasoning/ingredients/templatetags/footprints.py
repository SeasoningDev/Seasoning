from django import template

register = template.Library()

@register.simple_tag
def availablein_footprint(ingredient, available_in):
    if ingredient is None or available_in is None:
        return ''
    return '%.2f' % (ingredient.base_footprint + available_in.footprint)