'''
Created on Jul 24, 2015

@author: joep
'''
import re
from django.db import models
from ingredients.models import Ingredient, Unit
from difflib import SequenceMatcher, get_close_matches
from fuzzywuzzy import fuzz

def parse_ingredient_line(ingredient_line):
    
    parts = ingredient_line.split()

    ### FIND AMOUNT
    parsed_amount = ''
    parts_i = 0
    while parts_i < len(parts):
        if re.match('.*\d.*', parts[parts_i].strip()):
            # Found a part with a number in it. Append all parts following this part with numbers in it
            # to get the amount parts
            while parts_i < len(parts):
                if re.match('.*\d.*', parts[parts_i].strip()):
                    parsed_amount += parts.pop(parts_i) + ' '
                else:
                    break
            break

        parts_i += 1

    parsed_amount = parsed_amount.strip()

    r = re.match('([\d\ ,\.]+)(\D+)$', parsed_amount)
    if r:
        parsed_amount = r.group(1)
        parts.insert(0, r.group(2))

    if '-' in parsed_amount:
        parsed_amount = parsed_amount.split('-')[-1].strip()

    ### FIND UNIT
    units = Unit.objects.all()
    amount_unit = Unit.objects.get(name='stuk')

    best_parts_i = None
    unit = None
    highest_sim = None
    for parts_i in range(len(parts)):
        for u in units:
            tests = [u.name, u.plural_name, u.short_name]
            tests.extend(u.synonyms.split(','))

            for test in tests:
                sim = SequenceMatcher(None, parts[parts_i].strip(), test).ratio()
                if highest_sim is None or sim > highest_sim:
                    highest_sim = sim
                    unit = u
                    best_parts_i = parts_i
    
    if highest_sim < 0.8:
        if parsed_amount != '':
            unit = amount_unit
        else:
            unit = None
    else:
        parsed_unit = parts.pop(best_parts_i)


    ### FIND INGREDIENT
    parsed_ingredient = ' '.join(parts)

    
    
    """
    We now have all the parts seperately, time to parse each of them

    """

    ### PARSE AMOUNT
    if parsed_amount != '':
        amount = 0
        
        for part in parsed_amount.split():
            part = part.strip()
             
            if re.match('^\d+$', part):
                amount += float(part)
                continue
            
            r = re.match('^(\d+)[/⁄](\d+)$', part)
            if r:
                amount += float(r.group(1)) / float(r.group(2))
                continue
        
            if re.match('^\d+([\.,]\d+)?$', part):
                amount += float(part.replace(',','.'))
                continue
        
            r = re.match('(\d+)(\D+)', part)
            if r:
                amount += float(m.group(1))
                parts.push(r.group(2))
                continue
        
        if amount == 0:
            raise Exception('Bad amount `{}` in `{}`'.format(parsed_amount, ingredient_line))
    
    elif unit is not None:
        amount = 1
    
    else:
        amount = None
    

    
    ### PARSE INGREDIENT
    f = models.Q()
    for ing_part in parsed_ingredient.split():
        f |= models.Q(name__icontains=ing_part)
        f |= models.Q(plural_name__icontains=ing_part)
        f |= models.Q(synonyms__name__icontains=ing_part)

    ing_matches = Ingredient.objects.filter(f).distinct().prefetch_related('synonyms')

    best_ratio = None
    best_ing_match = None

    for ing_match in ing_matches:
        ing_names = [ing_match.name]
        if ing_match.plural_name:
            ing_names.append(ing_match.plural_name)
        ing_names.extend(syn.name for syn in ing_match.synonyms.all())
        
        for ing_name in ing_names:
            ratio = (fuzz.token_sort_ratio(ing_name, parsed_ingredient) + fuzz.token_set_ratio(ing_name, parsed_ingredient)) / 200
                
            if best_ratio is None or ratio > best_ratio:
                best_ratio = ratio
                best_ing_match = ing_match

    ingredient = best_ing_match



    return ingredient_line, amount, unit, ingredient
