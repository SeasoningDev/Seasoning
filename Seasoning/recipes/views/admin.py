from django.shortcuts import render, redirect
from recipes.models import ExternalSite
from django.core.urlresolvers import reverse

def proofread_recipes(request):
    try:
        external_site = ExternalSite.objects.get(name="Eva vzw")
    except ExternalSite.DoesNotExist:
        external_site = ExternalSite(name="Eva vzw", url='http://www.evavzw.be')
        external_site.save()
    
    ao_recipes = external_site.recipes.count()
    ao_accepted_recipes = external_site.recipes.filter(accepted=True).count()
    ao_complete_recipes = external_site.recipes.filter(accepted=False).count()
    ao_incomplete_recipes = external_site.incomplete_recipes.all().count()
    recipes = external_site.recipes.filter(accepted=False)
    
    return render(request, 'admin/proofread_recipes.html', {'ao_recipes': ao_recipes,
                                                            'ao_accepted_recipes': ao_accepted_recipes,
                                                            'ao_complete_recipes': ao_complete_recipes,
                                                            'ao_incomplete_recipes': ao_incomplete_recipes,
                                                            'recipes': recipes})

def scrape_recipes(request):
    from recipes.scraper.evascraper import scrape_recipes
    scrape_recipes()
    
    return redirect(reverse('proofread_recipes'))