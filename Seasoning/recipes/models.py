import time
import ingredients
import datetime
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator,\
    MaxLengthValidator
from django.core.exceptions import ValidationError, PermissionDenied
from django.utils.translation import ugettext_lazy as _
from authentication.models import User
from imagekit.models.fields import ProcessedImageField, ImageSpecField
from imagekit.processors.resize import SmartResize
from ingredients.models import Ingredient, Unit
from general import validate_image_size

def get_image_filename(instance, old_filename):
    extension = old_filename.split('.')[-1]
    filename = '%s.%s' % (str(time.time()), extension)
    return 'images/recipes/' + filename

class Cuisine(models.Model):
    
    class Meta:
        db_table = 'cuisine'
        ordering = ["name"]
    
    name = models.CharField(max_length=50)
    
    def __unicode__(self):
        return self.name

class RecipeManager(models.Manager):
    
    def query(self, search_string='', advanced_search=False, sort_field='time_added', 
              sort_order='-', inseason=False, ven=True, veg=True, nveg=True, cuisines=[], 
              courses=[], include_ingredients_operator='and', include_ingredient_names=[],
              exclude_ingredient_names=[]):
        
        recipes_list = self
        
        name_query = models.Q(name__icontains=search_string)
            
        incl_ingredient_filter = models.Q()
        additional_filters = models.Q(visible=True, accepted=True)
        if advanced_search:
            # Filter for included en excluded ingredients
            if include_ingredients_operator == 'and':
                for ingredient_name in include_ingredient_names:
                    ing_filter = models.Q(ingredients__name__icontains=ingredient_name) | models.Q(ingredients__synonyms__name__icontains=ingredient_name)
                    recipes_list = recipes_list.filter(ing_filter)
            elif include_ingredients_operator == 'or':
                for ingredient_name in include_ingredient_names:
                    ing_filter = models.Q(ingredients__name__icontains=ingredient_name) | models.Q(ingredients__synonyms__name__icontains=ingredient_name)
                    incl_ingredient_filter = incl_ingredient_filter | models.Q(ing_filter)            
            for ingredient_name in exclude_ingredient_names:
                recipes_list = recipes_list.exclude(ingredients__name__icontains=ingredient_name)
                recipes_list = recipes_list.exclude(ingredients__synonyms__name__icontains=ingredient_name)
            
            if cuisines:
                additional_filters = additional_filters & models.Q(cuisine__in=cuisines)
            
            if courses:
                additional_filters = additional_filters & models.Q(course__in=courses)
                     
        recipes_list = recipes_list.filter(name_query & incl_ingredient_filter & additional_filters)
        
        # SORTING
        if sort_field:
            if 'tot_time' in sort_field:
                recipes_list = recipes_list.extra(select={'tot_time': 'active_time + passive_time'})
            sort_field = sort_order + sort_field
            recipes_list = recipes_list.order_by(sort_field)
        
        search_results = recipes_list.distinct()
        
        # Aggregate values filters
        agg_filter = lambda x: x.complete_information
        
        if not ven or not veg or not nveg:
            if not ven:
                agg_filter = lambda x: agg_filter(x) and x.veganism != Ingredient.VEGAN
            if not veg:
                agg_filter = lambda x: agg_filter(x) and x.veganism != Ingredient.VEGETARIAN
            if not nveg:
                agg_filter = lambda x: agg_filter(x) and x.veganism != Ingredient.NON_VEGETARIAN
        
        if inseason:
            agg_filter = lambda x: agg_filter(x) and x.inseason
            
        if not ven or not veg or not nveg or inseason:
            search_results = filter(agg_filter, search_results)
                
        return search_results
    
    def accepted(self):
        return self.filter(accepted=True)

class ExternalSite(models.Model):
    
    name = models.CharField(_('Name'), max_length=200,
                            help_text=_('The names of the external website.'))
    url = models.CharField(_('URL'), max_length=200,
                            help_text=_('The home url of the external website'))
    
    def __unicode__(self):
        return self.name

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
               (MARINADE_AND_SAUCE,u'Marinades en sauzen'))
    
    name = models.CharField(_('Name'), max_length=100,
                            help_text=_('The names of the recipe.'))
    author = models.ForeignKey(User, related_name='recipes', null=True)
    time_added = models.DateTimeField(auto_now_add=True, editable=False)
    
    external = models.BooleanField(default=False)
    external_url = models.CharField(max_length=1000, null=True, blank=True)
    external_site = models.ForeignKey(ExternalSite, null=True, blank=True)
    
    course = models.PositiveSmallIntegerField(_('Course'), choices=COURSES,
                                              help_text=_("The type of course this recipe will provide."))
    cuisine = models.ForeignKey(Cuisine, verbose_name=_('Cuisine'), db_column='cuisine', null=True, blank=True,
                                help_text=_("The type of cuisine this recipe represents."))
    description = models.TextField(_('Description'), validators=[MaxLengthValidator(140)],
                                   help_text=_("A few sentences describing the recipe (Maximum 140 characters)."))
    portions = models.PositiveIntegerField(_('Portions'), help_text=_('The average amount of people that can be fed by this recipe '
                                                       'using the given amounts of ingredients.'))
    active_time = models.IntegerField(_('Active time'), help_text=_('The time needed to prepare this recipe where you are actually doing something.'))
    passive_time = models.IntegerField(_('Passive time'), help_text=_('The time needed to prepare this recipe where you can do something else (e.g. water is boiling)'))
    
    ingredients = models.ManyToManyField(ingredients.models.Ingredient, through='UsesIngredient', editable=False)
    extra_info = models.TextField(_('Extra info'), default='', blank=True,
                                  help_text=_('Extra info about the ingredients or needed tools (e.g. "You will need a mixer for this recipe" or "Use big potatoes")'))
    instructions = models.TextField(_('Instructions'), help_text=_('Detailed instructions for preparing this recipe.'))
    
    default_image_location = 'images/no_image.jpg'
    image = ProcessedImageField(upload_to=get_image_filename, default=default_image_location, validators=[validate_image_size],
                                help_text=_('An image of this recipe. Please do not use copyrighted images, these will be removed as quick as possible.'))
    thumbnail = ImageSpecField([SmartResize(216, 216)], image_field='image', format='JPEG')
    small_image = ImageSpecField([SmartResize(310, 310)], image_field='image', format='JPEG')
    
    visible = models.BooleanField(default=True)
    
    accepted = models.BooleanField(default=False)
    
    """
    WARNING: DENORMALIZED FIELDS
    
    These fields are denormalized for the following reasons:
     - They are queried often
     - The queries where these fields are part of the filter might return large result sets
     - The calculation of the field requires one or more related models
    
    When any UsesIngredient connected to this recipe is changed, these values are updated.
    When any Ingredients or AvailableIns connected to this recipe are changed, these values are not updated
    The entire database of recipes should be updated nightly to reflect these changes, and seasonal changes
    You can update these values for every recipe in the database by issuing the 'update_recipe_aggregates'
     management command.
    
    """
    # This field is True if all required information is present to display this recipe correctly
    complete_information = models.BooleanField(default=True, editable=False)
    
    # This field gives the veganism of this recipe according to the used ingredients
    veganism = models.PositiveSmallIntegerField(choices=Ingredient.VEGANISMS, default=Ingredient.VEGAN, editable=False)
    
    # This field is True if any of this recipes ingredients is currenly available in an endangered location
    endangered = models.BooleanField(default=False, editable=False)
    
    # This field is True if the recipe currently has its lowest footprint of the year
    inseason = models.BooleanField(default=False, editable=False)
    
    # This field gives the current footprint of this recipe
    footprint = models.FloatField(default=0, editable=False)
    
    # The current rating of this recipe
    rating = models.FloatField(null=True, blank=True, editable=False)
    
    def __unicode__(self):
        return self.name
    
    def publish(self):
        return self.complete_information and self.visible and self.accepted
    
    @property
    def total_time(self):
        return self.active_time + self.passive_time
    
    def _compelete_information(self):
        for uses in self.uses.all():
            if not uses.ingredient.accepted:
                return False
        return True
    
    def _veganism(self):
        veganism = Ingredient.VEGAN
        for uses in self.uses.all():
            if uses.ingredient.veganism < veganism:
                veganism = uses.ingredient.veganism
        return veganism
    
    def _endangered(self):
        for uses in self.uses.all():
            if uses.ingredient.coming_from_endangered():
                return True
        return False
    
    def _inseason(self):
        return self.has_lowest_footprint_in_month(datetime.date.today().month)
    
    def _footprint(self):
        """
        Footprint per portion of this recipe
        
        """
        total_footprint = 0
        
        for uses in self.uses.all():
            # Add the footprint for this used ingredient to the total
            total_footprint += uses.footprint()
            
        return total_footprint / self.portions
    
    def _rating(self):
        if self.number_of_votes <= 0:
            return None
        return self.votes.all().aggregate(models.Avg('score'))['score__avg']
    
    @property
    def number_of_votes(self):
        return self.votes.all().aggregate(models.Count('score'))['score__count']        
    
    def total_footprint(self):
        return self.footprint * self.portions
    
    def normalized_footprint(self):
        """
        The footprint of this recipe for 4 portions
        
        """
        return self.footprint * 4
    
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
        
        return super(Recipe, self).save(*args, **kwargs)
    
    def recalculate_ingredient_aggregates(self):
        self.complete_information = self._compelete_information()
        self.veganism = self._veganism()
        self.endangered = self._endangered()
        self.inseason = self._inseason()
        self.footprint = self._footprint()
        self.save()
    
    def recalculate_rating_aggregates(self):
        self.rating = self._rating()
        self.save()
    
    def monthly_footprint(self):
        """
        Returns an array of 12 elements containing the footprint of this recipe
        for every month of the year
        
        """
        usess = self.uses.select_related('ingredient', 'unit__parent_unit').prefetch_related('ingredient__available_in_country', 'ingredient__available_in_sea', 'ingredient__canuseunit_set__unit__parent_unit').order_by('group', 'ingredient__name')
        # One footprint per month
        footprints = [0] * 12
        dates = [datetime.date(day=1, month=month, year=ingredients.models.AvailableIn.BASE_YEAR) for month in range(1, 13)]
        for uses in usess:
            for i in range(12):
                footprints[i] += uses.footprint(date=dates[i])
        footprints = [float('%.2f' % (4*footprint/self.portions)) for footprint in footprints]
        return footprints
    
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
        
    def has_lowest_footprint_in_month(self, month=None):
        if month is None:
            month = datetime.date.today().month
        footprints = self.monthly_footprint()
        min_footprint = min(footprints)
        if (abs(min_footprint - footprints[month-1]) < 0.000001*min_footprint) and (abs(max(footprints) - min_footprint) > 0.000001*min_footprint):
            return True
        return False

class UsesIngredient(models.Model):
    
    class Meta:
        db_table = 'usesingredient'
    
    recipe = models.ForeignKey(Recipe, related_name='uses', db_column='recipe')
    ingredient = models.ForeignKey(ingredients.models.Ingredient, related_name='used_in', db_column='ingredient')
    
    group = models.CharField(max_length=100, blank=True)
    amount = models.FloatField(default=0, validators=[MinValueValidator(0.00001)])
    unit = models.ForeignKey(ingredients.models.Unit, db_column='unit')
    
    # Set this to false if this object should not be saved (e.g. when certain fields have been 
    # overwritten for portions calculations)
    save_allowed = True
    
    def footprint(self, date=None):
        if not self.ingredient.accepted:
            return 0
        
        unit_properties = None
        
        for canuseunit in self.ingredient.canuseunit_set.all():
            if canuseunit.unit == self.unit:
                unit_properties = canuseunit
                break
        
        if unit_properties is None:
            raise Unit.DoesNotExist("This ingredient (%s) can not use the given unit (%s)" % (self.ingredient, self.unit))
        return self.amount * unit_properties.conversion_factor * self.ingredient.footprint(date)
    
    def clean(self, *args, **kwargs):
        # Validate that is ingredient is using a unit that it can use
        if self.ingredient_id is None or self.unit_id is None:
            # Something is wrong with the model, these errors will be caught elsewhere, and the
            # useable unit validation is not required 
            return self
        if not self.ingredient.accepted:
            # If the ingredient is not accepted, it might not have any useable units. To prevent
            # unwanted errors, skip the validation
            return self
        try:
            self.ingredient.useable_units.get(pk=self.unit.pk)
            return self
        except Unit.DoesNotExist:
            raise ValidationError('This unit cannot be used for measuring this Ingredient.')
        
    
    def save(self, update_recipe_aggregates=True, *args, **kwargs):
        if not self.save_allowed:
            raise PermissionDenied('Saving this object has been disallowed')
        
        ret = super(UsesIngredient, self).save(*args, **kwargs)
        
        if update_recipe_aggregates:
            self.recipe.recalculate_ingredient_aggregates()
        
        return ret

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
    time_added = models.DateTimeField(auto_now_add=True, editable=False)
    time_changed = models.DateTimeField(auto_now=True, editable=False)
    
    def save(self, *args, **kwargs):
        ret = super(Vote, self).save(*args, **kwargs)
        self.recipe.recalculate_rating_aggregates()
        return ret
    
    def delete(self, *args, **kwargs):
        ret = super(Vote, self).delete(*args, **kwargs)
        self.recipe.recalculate_rating_aggregates()
        return ret
    