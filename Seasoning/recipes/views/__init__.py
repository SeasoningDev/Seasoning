from std import *
from ajax import *
from admin import *


import os
from django.core.exceptions import ValidationError
from django.contrib.formtools.wizard.views import SessionWizardView
from django.utils.decorators import method_decorator
from django.core.files.storage import FileSystemStorage
from django import forms
from django.contrib.formtools.wizard.forms import ManagementForm
from general.forms import FormContainer
from ingredients.models import CanUseUnit


"""
Ajax calls
"""


"""
Unused for now

@csrf_exempt
def get_relative_footprint(request):
    
    if request.is_ajax() and request.method == 'POST':
        recipe_id = request.POST.get('recipe', None)
    
        if recipe_id is not None:
            try:
                recipe = Recipe.objects.get(pk=recipe_id)
                bounds = Recipe.objects.aggregate(Max('footprint'), Min('footprint'))
                min_fp = 4*bounds['footprint__min']
                max_fp = 4*bounds['footprint__max']
                interval_count = 20
                interval_length = (max_fp-min_fp)/interval_count
                recipes = Recipe.objects.values('footprint', 'course', 'veganism').all().order_by('footprint')
                
                intervals = [min_fp+i*interval_length for i in range(interval_count+1)]
                all_footprints = []
                category_footprints = []
                veganism_footprints = []
                
                footprint_index = 0
                for upper_bound in intervals[1:]:
                    # Don't check the first value in the intervals, because we only need upper bounds
                    # of intervals
                    all_footprints.append(0)
                    category_footprints.append(0)
                    veganism_footprints.append(0)
                    while 4*recipes[footprint_index]['footprint'] <= upper_bound:
                        all_footprints[-1] += 1
                        if recipe.course == recipes[footprint_index]['course']:
                            category_footprints[-1] += 1
                        if recipe.veganism == recipes[footprint_index]['veganism']:
                            veganism_footprints[-1] += 1
                        footprint_index += 1
                        if footprint_index >= len(recipes):
                            break
                data = {'all_fps': all_footprints,
                        'cat_fps': category_footprints,
                        'veg_fps': veganism_footprints,
                        'min_fp': min_fp,
                        'max_fp': max_fp,
                        'interval_length': interval_length,
                        'fp': 4*recipe.footprint}
                json_data = simplejson.dumps(data)
            
                return HttpResponse(json_data)
            
            except Recipe.DoesNotExist:
                raise Http404
        
    raise PermissionDenied
"""