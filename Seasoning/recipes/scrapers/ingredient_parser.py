'''
Created on Jul 24, 2015

@author: joep
'''
import re

def parse_ingredient_line(ingredient_line):
    
    parts = ingredient_line.split()
    
    if len(parts) > 1:
        if re.match('^\d+(,\d+)?$', parts[0].strip()):
            amount = parts[0]
            parts.pop(0)
        elif re.match('^\D+$', parts[0].strip()):
            amount = ''
            parts.pop(0)
        elif re.match('^\d+[/-]\d+$', parts[0].strip()):
            amount = parts[0]
        elif re.match('^\d+\D+$', parts[0].strip()):
            m = re.match('(\d+)(\D+)', parts[0].strip())
            amount = m.group(1)
            parts[0] = m.group(2)
        else:
            raise Exception('Bad amount `{}` in `{}`'.format(parts[0], ingredient_line))
    
    else:
        amount = ''
    
    if len(parts) > 1:
        unit = parts[0]
        del parts[0]
    
    else:
        unit = ''
    
    ingredient = ' '.join(parts)
    
    group = ''
    
    return ingredient, amount, unit, group