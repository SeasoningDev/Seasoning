# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0027_auto_20150707_1639'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipe',
            name='_footprint_category',
            field=models.PositiveSmallIntegerField(default=0, choices=[(0, 'A+'), (1, 'A'), (2, 'B'), (3, 'C'), (4, 'D')]),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='recipe',
            name='_has_endangered_ingredients',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='recipe',
            name='_in_season',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='recipe',
            name='_veganism',
            field=models.PositiveSmallIntegerField(default=0, choices=[(2, 'Veganistisch'), (1, 'Vegetarisch'), (0, 'Niet-Vegetarisch')]),
            preserve_default=False,
        ),
    ]
