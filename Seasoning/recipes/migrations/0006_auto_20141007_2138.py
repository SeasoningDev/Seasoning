# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ingredients', '0002_auto_20140926_1221'),
        ('recipes', '0005_recipe_no_of_ratings'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='external_site',
            field=models.ForeignKey(related_name=b'recipes', blank=True, to='recipes.ExternalSite', null=True),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='rating',
            field=models.FloatField(default=None, null=True, editable=False, blank=True),
        ),
    ]
