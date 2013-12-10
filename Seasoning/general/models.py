from django.db import models
from recipes.models import Recipe
from ingredients.models import Ingredient
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError

class StaticPage(models.Model):
    
    class Meta:
        db_table = 'staticpage'
        
    name = models.CharField(max_length=50, unique=True)
    url = models.CharField(max_length=100, unique=True)
    
    body_html = models.TextField()
    
    last_modified = models.DateTimeField(auto_now=True)
    
    def __unicode__(self):
        return self.name

class RecipeOfTheWeek(models.Model):
    
    class Meta:
        db_table = 'rotw'
    
    recipe = models.ForeignKey(Recipe, limit_choices_to={'accepted': True})
    veganism = models.PositiveSmallIntegerField(choices=Ingredient.VEGANISMS, default=Ingredient.VEGAN, unique=True)
    
    last_updated = models.DateField(auto_now=True)
    
    def __unicode__(self):
        return _('%s is the %s recipe of the week.') % (self.recipe.name, self.get_veganism_display())
    
    def clean(self):
        if not self.recipe.veganism == self.veganism:
            raise ValidationError(_('The given recipe is not %s.') % self.get_veganism_display())
        