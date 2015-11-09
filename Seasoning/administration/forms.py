'''
Created on Jul 7, 2015

@author: joep
'''
from django import forms
from recipes.models import ScrapedRecipe
from django.conf import settings
from django.core.mail import send_mail

class ContactForm(forms.Form):
    
    INFO , PRESS, TECHNICAL = 0, 1, 2 
    CONTACT_TYPES = ((None, 'Wat is de reden van uw contact?'), (INFO, 'Informatie, vragen en suggesties'), (PRESS, 'Media en partnerships'), (TECHNICAL, 'Technische problemen of misbruik'))
    
    email = forms.EmailField()
    
    contact_type = forms.ChoiceField(choices=CONTACT_TYPES)
    
    message = forms.CharField(widget=forms.Textarea)
    
    def send_email(self):
        if settings.DEBUG:
            return 0
        
        try:
            return send_mail(subject='Contact met Seasoning: {}'.format(dict(self.CONTACT_TYPES)[int(self.cleaned_data['contact_type'])]),
                             message=self.cleaned_data['message'],
                             from_email=self.cleaned_data['email'],
                             recipient_list=['bram.somers@seasoning.be', 'joep.driesen@seasoning.be'],
                             fail_silently=True)
        
        except ConnectionRefusedError:
            return 0
    

class ScrapedRecipeProofreadForm(forms.ModelForm):
    
    class Meta:
        model = ScrapedRecipe
        exclude = ['scraped_name', 'external', 'external_site', 'external_url',
                   'description', 'active_time', 'passive_time',
                   'extra_info', 'instructions', 'deleted', 'recipe',
                   'image_url', 'course_proposal', 'cuisine_proposal']