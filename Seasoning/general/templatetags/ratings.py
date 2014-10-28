from django import template
from django.db.models.aggregates import Max
from recipes.models import Recipe

register = template.Library()

@register.simple_tag
def mean_footprint(footprint):
    if footprint is None:
        return '<span id="account-mean-footprint-off" style="width: 100%"></span>'
    width_percentage = int((footprint/Recipe.objects.all().aggregate(Max('footprint'))['footprint__max'])*100)
    return '<span id="account-mean-footprint-on" style="width: %d%%"></span><span id="account-mean-footprint-off" style="width: %d%%"></span>' % (width_percentage, 100-width_percentage)