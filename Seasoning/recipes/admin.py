from django.contrib import admin
from recipes.models import Recipe, Cuisine, UsesIngredient, UnknownIngredient

class UsesIngredientInline(admin.TabularInline):
    model = UsesIngredient
    readonly_fields=('footprint',)

class RecipeAdmin(admin.ModelAdmin):
    inlines = [ UsesIngredientInline, ]
    search_fields = ['name']
    list_display = ('__unicode__', 'accepted')
    
    # Make sure the recipe object gets saved again after the usesingredient objects are saved
    temp_obj = None
    
    def save_model(self, request, obj, form, change):
        self.temp_obj = obj
        admin.ModelAdmin.save_model(self, request, obj, form, change)
    
    def save_related(self, request, form, formsets, change):
        admin.ModelAdmin.save_related(self, request, form, formsets, change)
        self.temp_obj.save()
    
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Cuisine)
admin.site.register(UnknownIngredient)