from django import template
register = template.Library()

@register.filter(name='addcss')
def addcss(field, css):
    attrs = {}
    i = 0
    l = css.split(',')
    try:
        while True:
            attrs[l[i]] = l[i+1]
            i += 2
    except IndexError:
        pass
    
    return field.as_widget(attrs=attrs)