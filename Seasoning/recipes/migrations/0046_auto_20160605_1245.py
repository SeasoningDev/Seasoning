# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0045_recipe_cached_footprint_category'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='scrapedusesingredient',
            name='amount_proposal',
        ),
        migrations.RemoveField(
            model_name='scrapedusesingredient',
            name='group',
        ),
        migrations.RemoveField(
            model_name='scrapedusesingredient',
            name='ingredient_proposal',
        ),
        migrations.RemoveField(
            model_name='scrapedusesingredient',
            name='unit_proposal',
        ),
        migrations.AddField(
            model_name='scrapedusesingredient',
            name='raw_ingredient_line',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
    ]
