# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0020_auto_20150707_1054'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scrapedusesingredient',
            name='recipe',
            field=models.ForeignKey(blank=True, related_name='ingredients', to='recipes.ScrapedRecipe', null=True, on_delete=django.db.models.deletion.SET_NULL),
        ),
    ]
