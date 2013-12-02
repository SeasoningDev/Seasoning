"""
Copyright 2012, 2013 Driesen Joep

This file is part of Seasoning.

Seasoning is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Seasoning is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Seasoning.  If not, see <http://www.gnu.org/licenses/>.
    
"""
import os, time
from django.db import models
from authentication.models import User
from imagekit.models.fields import ProcessedImageField, ImageSpecField
from imagekit.processors.resize import ResizeToFill, Resize, SmartResize
from imagekit.processors.crop import Crop
import ingredients
from ingredients.models import CanUseUnit, Ingredient, Unit
import datetime
from django.core.validators import MaxValueValidator, MinValueValidator,\
    MaxLengthValidator
from django.db.models.fields import FloatField
from django.core.exceptions import ValidationError, PermissionDenied
from django.utils.translation import ugettext_lazy as _

def get_image_filename(instance, old_filename):
    filename = str(time.time()) + '.png'
    return 'images/recipes/' + filename

class Cuisine(models.Model):
    
    class Meta:
        db_table = 'cuisine'
        ordering = ["name"]
    
    name = models.CharField(max_length=50)
    
    def __unicode__(self):
        return self.name

class RecipeManager(models.Manager):
    
    def query(self, search_string='', advanced_search=False, sort_field='', 
              sort_order='', ven=True, veg=True, nveg=True, cuisines=[], 
              courses=[], include_ingredients_operator='and', include_ingredient_names=[],
              exclude_ingredient_names=[]):
        
        recipes_list = Recipe.objects
        
        name_query = models.Q(name__icontains=search_string)
            
        veg_filter = models.Q()
        incl_ingredient_filter = models.Q()
        additional_filters = models.Q(accepted=True)
        if advanced_search:
            # Filter for Veganism
            if ven:
                veg_filter = veg_filter | models.Q(veganism=Ingredient.VEGAN)
            if veg:
                veg_filter = veg_filter | models.Q(veganism=Ingredient.VEGETARIAN)
            if nveg:
                veg_filter = veg_filter | models.Q(veganism=Ingredient.NON_VEGETARIAN)
            
            # Filter for included en excluded ingredients
            if include_ingredients_operator == 'and':
                for ingredient_name in include_ingredient_names:
                    recipes_list = recipes_list.filter(ingredients__name__icontains=ingredient_name)
            elif include_ingredients_operator == 'or':
                for ingredient_name in include_ingredient_names:
                    incl_ingredient_filter = incl_ingredient_filter | models.Q(ingredients__name__icontains=ingredient_name)            
            for ingredient_name in exclude_ingredient_names:
                recipes_list = recipes_list.exclude(ingredients__name__icontains=ingredient_name)
            
            if cuisines:
                additional_filters = additional_filters & models.Q(cuisine__in=cuisines)
            
            if courses:
                additional_filters = additional_filters & models.Q(course__in=courses)
                     
        recipes_list = recipes_list.filter(name_query & veg_filter & incl_ingredient_filter & additional_filters)
        
        # SORTING
        if sort_field:
            if 'tot_time' in sort_field:
                recipes_list = recipes_list.extra(select={'tot_time': 'active_time + passive_time'})
            sort_field = sort_order + sort_field
            recipes_list = recipes_list.order_by(sort_field)
        
        return recipes_list.distinct()

class Recipe(models.Model):
    
    class Meta:
        db_table = 'recipe'
        
    objects = RecipeManager()
    
    ENTRY, BREAD, BREAKFAST, DESERT, DRINK, MAIN_COURSE, SALAD, SIDE_DISH, SOUP, MARINADE_AND_SAUCE = 0, 1, 2, 3, 4, 5, 6, 7, 8, 9
    COURSES = ((ENTRY,u'Voorgerecht'),
               (BREAD,u'Brood'),
               (BREAKFAST,u'Ontbijt'),
               (DESERT,u'Dessert'),
               (DRINK,u'Drank'),
               (MAIN_COURSE,u'Hoofdgerecht'),
               (SALAD,u'Salade'),
               (SIDE_DISH,u'Bijgerecht'),
               (SOUP,u'Soep'),
               (MARINADE_AND_SAUCE,u'Marinades en Sauzen'))
    
    name = models.CharField(max_length=100,
                            help_text=_('The names of the recipe.'))
    author = models.ForeignKey(User, related_name='recipes', editable=False, null=True)
    time_added = models.DateTimeField(auto_now_add=True, editable=False)
    
    course = models.PositiveSmallIntegerField(choices=COURSES,
                                              help_text=_("The type of course this recipe will provide."))
    cuisine = models.ForeignKey(Cuisine, db_column='cuisine', null=True, blank=True,
                                help_text=_("The type of cuisine this recipe represents."))
    description = models.TextField(validators=[MaxLengthValidator(140)],
                                   help_text=_("A few sentences describing the recipe (Maximum 140 characters)."))
    portions = models.PositiveIntegerField(help_text=_('The average amount of people that can be fed by this recipe '
                                                       'using the given amounts of ingredients.'))
    active_time = models.IntegerField(help_text=_('The time needed to prepare this recipe where you are actually doing something.'))
    passive_time = models.IntegerField(help_text=_('The time needed to prepare this recipe where you can do something else (e.g. water is boiling)'))
    
    rating = models.FloatField(null=True, blank=True, default=None, editable=False)
    number_of_votes = models.PositiveIntegerField(default=0, editable=False)
    
    ingredients = models.ManyToManyField(ingredients.models.Ingredient, through='UsesIngredient', editable=False)
    extra_info = models.TextField(default='', blank=True,
                                  help_text=_('Extra info about the ingredients or needed tools (e.g. "You will need a mixer for this recipe" or "Use big potatoes")'))
    instructions = models.TextField(help_text=_('Detailed instructions for preparing this recipe.'))
    
    image = ProcessedImageField(format='PNG', upload_to=get_image_filename, default='images/ingredients/no_image.png',
                                help_text=_('An image of this recipe. Please do not use copyrighted images, these will be removed as quick as possible.'))
    thumbnail = ImageSpecField([SmartResize(220, 220)], image_field='image', format='PNG')
    
    # Derived Parameters
    # Footprint per portion
    footprint = FloatField(editable=False)
    veganism = models.PositiveSmallIntegerField(choices=Ingredient.VEGANISMS, editable=False)
    
    accepted = models.BooleanField(default=False)        
    
    def __unicode__(self):
        return self.name
    
    @property
    def total_time(self):
        return self.active_time + self.passive_time
    
    # Set this to false if this object should not be saved (e.g. when certain fields have been 
    # overwritten for portions calculations)
    save_allowed = True
    
    def save(self, *args, **kwargs):
        """
        Calculate the recipes footprint by adding the footprint
        of every used ingredient
        Calculate the recipes veganism by searching for the ingredient
        with the lowest veganism.
        
        """
        if not self.save_allowed:
            raise PermissionDenied('Saving this object has been disallowed')
        
        self.footprint = 0
        self.veganism = Ingredient.VEGAN
        
        total_footprint = 0
        self.accepted = True
        for uses in self.uses.all():
            # Add the footprint for this used ingredient to the total
            total_footprint += uses.footprint
            
            # Check the veganism of this ingredient
            if uses.ingredient.veganism < self.veganism:
                self.veganism = uses.ingredient.veganism
            
            # Check the state of this ingredient
            if not uses.ingredient.accepted:
                self.accepted = False
        self.footprint = total_footprint / self.portions
        
                
        return super(Recipe, self).save(*args, **kwargs)
    
    def total_footprint(self):
        return self.footprint * self.portions
    
    def normalized_footprint(self):
        """
        The footprint of this recipe for 4 portions
        
        """
        return self.footprint * 4
    
    def vote(self, user, score):
        try:
            # Check if the user already voted on this recipe
            vote = self.votes.get(user=user)
            vote.score = score
        except Vote.DoesNotExist:
            # The given user has not voted on this recipe yet
            vote = Vote(recipe=self, user=user, score=score)
        vote.save()
    
    def unvote(self, user):
        vote = self.votes.get(user=user)
        vote.delete()
    
    def calculate_and_set_rating(self):
        aggregate = self.votes.all().aggregate(models.Count('score'), models.Avg('score'))
        self.rating = aggregate['score__avg']
        self.number_of_votes = aggregate['score__count']
        self.save()

class UsesIngredient(models.Model):
    
    class Meta:
        db_table = 'usesingredient'
    
    recipe = models.ForeignKey(Recipe, related_name='uses', db_column='recipe')
    ingredient = models.ForeignKey(ingredients.models.Ingredient, db_column='ingredient')
    
    group = models.CharField(max_length=100, blank=True)
    amount = models.FloatField(default=0, validators=[MinValueValidator(0.00001)])
    unit = models.ForeignKey(ingredients.models.Unit, db_column='unit')
    
    # Derived Parameters
    footprint = FloatField(null=True, editable=False)
    
    # Set this to false if this object should not be saved (e.g. when certain fields have been 
    # overwritten for portions calculations)
    save_allowed = True
    
    def normalized_footprint(self, ingredient_footprint):
        """
        Returns the footprint normalized by the used unit and the used amount
        for a given ingredient footprint
        
        """
        for canuseunit in self.ingredient.canuseunit_set.all():
            if canuseunit.unit == self.unit:
                unit_properties = canuseunit
                break
        return self.amount * unit_properties.conversion_factor * ingredient_footprint
    
    def clean(self, *args, **kwargs):
        # Validate that is ingredient is using a unit that it can use
        if self.ingredient_id is None or self.unit_id is None:
            # Something is wrong with the model, these errors will be caught elsewhere, and the
            # useable unit validation is not required 
            return self
        if not self.ingredient.accepted:
            # If the ingredient is not accepted, it might not have any useable units. To prevent
            # false positivies, skip the validation
            return self
        try:
            self.ingredient.useable_units.get(pk=self.unit.pk)
            return self
        except Unit.DoesNotExist:
            raise ValidationError('This unit cannot be used for measuring this Ingredient.')
        
    
    def save(self, *args, **kwargs):
        update_recipe = kwargs.pop('update_recipe', False)
        
        if not self.save_allowed:
            raise PermissionDenied('Saving this object has been disallowed')
        
        if self.ingredient.accepted:
            self.footprint = self.normalized_footprint(self.ingredient.footprint())
        else:
            self.footprint = 0
        
        saved = super(UsesIngredient, self).save(*args, **kwargs)
        
        if update_recipe:
            # Update the recipe as well
            self.recipe.save()
        
        return saved

class UnknownIngredient(models.Model):
    class Meta:
        db_table = 'unknown_ingredient'
    
    name = models.CharField(max_length=50L)
    requested_by = models.ForeignKey(User)
    for_recipe = models.ForeignKey(Recipe)
    
    real_ingredient = models.ForeignKey(Ingredient)
    
    def __unicode__(self):
        return self.name
    
class Vote(models.Model):
    class Meta:
        unique_together = (("recipe", "user"),)
    
    recipe = models.ForeignKey(Recipe, related_name='votes')
    user = models.ForeignKey(User)
    score = models.PositiveIntegerField(validators=[MaxValueValidator(5)])
    time_added = models.DateTimeField(default=datetime.datetime.now, editable=False)
    time_changed = models.DateTimeField(default=datetime.datetime.now, editable=False)
    
    def save(self, *args, **kwargs):
        self.time_changed = datetime.datetime.now()
        super(Vote, self).save(*args, **kwargs)
        self.recipe.calculate_and_set_rating()
    
    def delete(self, *args, **kwargs):
        super(Vote, self).delete(*args, **kwargs)
        self.recipe.calculate_and_set_rating()
    