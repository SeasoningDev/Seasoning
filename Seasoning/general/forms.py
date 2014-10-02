from django import forms
from django.utils.translation import ugettext_lazy as _
from django.forms.formsets import BaseFormSet
from django.utils.datastructures import SortedDict, MultiValueDict
from django.utils.safestring import mark_safe
from captcha.fields import ReCaptchaField

class ContactForm(forms.Form):
    
    subject = forms.CharField(label=_("Subject"))
    your_email = forms.EmailField(label=_("Email"))
    message = forms.CharField(widget=forms.Textarea,
                              label=_("Message"))
                             
    captcha = ReCaptchaField(attrs={'theme': 'red'},
                             error_messages = {'required': _("You must enter the correct ReCaptcha characters")})
    
    def __init__(self, *args, **kwargs):
        logged_in = kwargs.pop('logged_in', False)
        super(ContactForm, self).__init__(*args, **kwargs)
        if logged_in:
            del self.fields['your_email']
            del self.fields['captcha']


class FormContainerMetaclass(type):
    def __new__(cls, name, bases, attrs):
        form_classes = SortedDict(
            (prefix, attrs.pop(prefix))
            for prefix, form_class in attrs.items()
            if isinstance(form_class, type) and issubclass(form_class, (forms.BaseForm, BaseFormSet))
        )

        new_class = super(FormContainerMetaclass, cls).__new__(cls, name, bases, attrs)

        new_class.form_classes = form_classes

        # Making the form container look like a form, for the
        # sake of the FormWizard.
        new_class.base_fields = {}
        for prefix, form_class in new_class.form_classes.items():
            if issubclass(form_class, BaseFormSet):
                new_class.base_fields.update(form_class.form.base_fields)
            else:
                new_class.base_fields.update(form_class.base_fields)

        return new_class


class FormContainer(unicode):
    __metaclass__ = FormContainerMetaclass

    def __init__(self, **kwargs):
        self._errors = {}
        self.forms = SortedDict()
        container_prefix = kwargs.pop('prefix', '')

        # Instantiate all the forms in the container
        for form_prefix, form_class in self.form_classes.items():
            self.forms[form_prefix] = form_class(
                prefix='-'.join(p for p in [container_prefix, form_prefix] if p),
                **self.get_form_kwargs(form_prefix, **kwargs)
            )

    def get_form_kwargs(self, prefix, **kwargs):
        """Return per-form kwargs for instantiating a specific form

        By default, just returns the kwargs provided. prefix is the
        label for the form in the container, allowing you to specify
        extra (or less) kwargs for each form in the container.
        """
        return kwargs

    def __unicode__(self):
        "Render all the forms in the container"
        return mark_safe(u''.join([f.as_table() for f in self.forms.values()]))

    def __iter__(self):
        "Return each of the forms in the container"
        for prefix in self.forms:
            yield self[prefix]

    def __getitem__(self, prefix):
        "Return a specific form in the container"
        try:
            form = self.forms[prefix]
        except KeyError:
            raise KeyError('Prefix %r not found in Form container' % prefix)
        return form

    def is_valid(self):
        return all(f.is_valid() for f in self.forms.values())
    
    @property
    def is_bound(self):
        return all(f.is_bound for f in self.forms.values())

    @property
    def data(self):
        "Return a compressed dictionary of all data from all subforms"
        all_data = MultiValueDict()
        for _, form in self.forms.items():
            for key in form.data:
                all_data.setlist(key, form.data.getlist(key))
        return all_data

    @property
    def files(self):
        "Return a compressed dictionary of all files from all subforms"
        all_files = MultiValueDict()
        for _, form in self.forms.items():
            for key in form.files:
                all_files.setlist(key, form.files.getlist(key))
        return all_files

    @property
    def errors(self):
        "Return a compressed dictionary of all errors form all subforms"
        return dict((prefix, form.errors) for prefix, form in self.forms.items())

    def save(self, *args, **kwargs):
        "Save each of the subforms"
        return [f.save(*args, **kwargs) for f in self.forms.values()]

    def save_m2m(self):
        """Save any related objects -- e.g., m2m entries or inline formsets

        This is needed if the original form collection was saved with commit=False
        """
        for _, form in self.forms.items():
            try:
                for subform in form.saved_forms:
                    # Because the related instance wasn't saved at the time the
                    # form was created, the new PK value hasn't propegated to
                    # the inline object on the formset. We need to re-set the
                    # instance to update the _id attribute, which will allow the
                    # inline form instance to save.
                    setattr(subform.instance, form.fk.name, form.instance)
                    subform.instance.save()
            except AttributeError:
                pass

            try:
                form.save_m2m()
            except AttributeError:
                pass