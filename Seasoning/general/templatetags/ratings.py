from django import template
from django.db.models.aggregates import Max
from recipes.models import Recipe

register = template.Library()

@register.simple_tag
def rating_display_stars(rating):
    if rating is None:
        return ''
    width_percentage = int((rating/5.0)*100)
    return '<span class="star-rating-wrapper" title="Dit recept heeft een score van %d/5"><span class="star-rating-not" style="width:%d%%"></span><span class="star-rating" style="width:%d%%"></span></span>' % (rating, 100-width_percentage, width_percentage)

@register.simple_tag
def mean_rating(rating):
    if rating is None:
        return '<span id="account-mean-rank-on" style="width: 100%"></span>'
    width_percentage = int((rating/5.0)*100)
    return '<span id="account-mean-rank-on" style="width: %d%%"></span><span id="account-mean-rank-off" style="width: %d%%"></span>' % (width_percentage, 100-width_percentage)

@register.simple_tag
def mean_footprint(footprint):
    if footprint is None:
        return '<span id="account-mean-footprint-off" style="width: 100%"></span>'
    width_percentage = int((footprint/Recipe.objects.all().aggregate(Max('footprint'))['footprint__max'])*100)
    return '<span id="account-mean-footprint-on" style="width: %d%%"></span><span id="account-mean-footprint-off" style="width: %d%%"></span>' % (width_percentage, 100-width_percentage)