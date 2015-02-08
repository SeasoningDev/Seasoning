from django.shortcuts import render, redirect
from recipes.models import ExternalSite
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied

def proofread_recipes(request):
    if not request.user.is_superuser:
        raise PermissionDenied()
    
    try:
        external_site = ExternalSite.objects.get(name="Eva vzw")
    except ExternalSite.DoesNotExist:
        external_site = ExternalSite(name="Eva vzw", url='http://www.evavzw.be')
        external_site.save()
    
    ao_recipes = external_site.recipes.count() + external_site.incomplete_recipes.filter(ignore=False).count()
    ao_accepted_recipes = external_site.recipes.filter(accepted=True).count()
    ao_complete_recipes = external_site.recipes.filter(accepted=False).count()
    ao_incomplete_recipes = external_site.incomplete_recipes.filter(ignore=False).count()
    incomplete_recipes = external_site.incomplete_recipes.filter(ignore=False)
    complete_recipes = external_site.recipes.all().order_by('accepted')
    ignored_recipes = external_site.incomplete_recipes.filter(ignore=True)
    
    return render(request, 'admin/proofread_recipes.html', {'ao_recipes': ao_recipes,
                                                            'ao_accepted_recipes': ao_accepted_recipes,
                                                            'ao_complete_recipes': ao_complete_recipes,
                                                            'ao_incomplete_recipes': ao_incomplete_recipes,
                                                            'incomplete_recipes': incomplete_recipes,
                                                            'complete_recipes': complete_recipes,
                                                            'ignored_recipes': ignored_recipes})

def scrape_recipes(request):
    if not request.user.is_superuser:
        raise PermissionDenied()
    
    from recipes.scraper.evascraper import scrape_recipes
    scrape_recipes()
    
    return redirect(reverse('proofread_recipes'))