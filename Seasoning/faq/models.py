from django.db import models
from django.utils.translation import ugettext_lazy as _

class Topic(models.Model):
    """
    Generic Topics for FAQ question grouping
    """
    class Meta:
        verbose_name = _("Topic")
        verbose_name_plural = _("Topics")
    
    name = models.CharField(_('name'), max_length=150)

    def __unicode__(self):
        return self.name

class Question(models.Model):
    class Meta:
        verbose_name = _("Frequent asked question")
        verbose_name_plural = _("Frequently asked questions")

    text = models.TextField(_('question'), help_text=_('The actual question itself.'))
    answer = models.TextField(_('answer'), blank=True, help_text=_('The answer text.'))
    topic = models.ForeignKey(Topic, verbose_name=_('topic'), related_name='questions')
    
    def __unicode__(self):
        return self.text