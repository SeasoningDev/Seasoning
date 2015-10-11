# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0030_remove_recipe__footprint_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='_footprint',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='_veganism',
            field=models.PositiveSmallIntegerField(choices=[(2, 'Veganistisch'), (1, 'Vegetarisch'), (0, 'Niet-Vegetarisch')], null=True, blank=True),
        ),
    ]
