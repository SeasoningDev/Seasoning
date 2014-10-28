from django.db import models
from django.utils.translation import ugettext_lazy as _

class ExternalSite(models.Model):
    
    name = models.CharField(_('Name'), max_length=200,
                            help_text=_('The names of the external website.'))
    url = models.CharField(_('URL'), max_length=200,
                            help_text=_('The home url of the external website'))
    
    def __unicode__(self):
        return self.name

class AggregateManager(models.Manager):
    
    def update_fp_cat_aggregates(self, fp_cats_upper_limits):
        fp_cats_upper_limits[Aggregate.D] = 1000000
        for fp_cat, upper_limit in fp_cats_upper_limits.items():
            try:
                aggr = self.get(name=fp_cat)
                aggr.value = upper_limit
                aggr.extra_info = Aggregate.AGGREGATES_TEXT[fp_cat]
                aggr.save()
            except Aggregate.DoesNotExist:
                Aggregate(name=fp_cat, value=upper_limit, extra_info=Aggregate.AGGREGATES_TEXT[fp_cat]).save()
    
class Aggregate(models.Model):
    Ap, A, B, C, D = 0, 1, 2, 3, 4
    AGGREGATE_DICT = {Ap: 'A+', A: 'A', B: 'B', C: 'C', D: 'D'}
    AGGREGATES = [(cat, AGGREGATE_DICT[cat]) for cat in [Ap, A, B, C, D]]
    AGGREGATES_TEXT = {Ap: 'De voetafdruk van dit recept is lager dan 90% van de recepten op Seasoning.',
                       A: 'De voetadruk van dit recept is lager dan 75% van de recepten op Seasoning',
                       B: 'De voetafdruk van dit recept is lager dan 50% van de recepten op Seasoning',
                       C: 'De voetafdruk van dit recept is hoger dan 50% van de recepten op Seasoning',
                       D: 'De voetafdruk van dit recept is hoger dan 75% van de recepten op Seasoning'}
    
    
    objects = AggregateManager()
    name = models.PositiveSmallIntegerField(choices=AGGREGATES, unique=True)
    value = models.FloatField()
    extra_info = models.TextField(default='')
    
    def get_ribbon_image_name(self):
        return 'cat-ribbon-{0}.png'.format(self.get_name_display())
    