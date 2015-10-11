# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0031_auto_20150708_1224'),
    ]

    operations = [
        migrations.RenameField(
            model_name='recipe',
            old_name='_footprint',
            new_name='cached_footprint',
        ),
        migrations.RenameField(
            model_name='recipe',
            old_name='_has_endangered_ingredients',
            new_name='cached_has_endangered_ingredients',
        ),
        migrations.RenameField(
            model_name='recipe',
            old_name='_in_season',
            new_name='cached_in_season',
        ),
        migrations.RenameField(
            model_name='recipe',
            old_name='_veganism',
            new_name='cached_veganism',
        ),
    ]
