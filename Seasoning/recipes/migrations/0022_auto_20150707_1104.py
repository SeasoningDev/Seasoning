# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0021_auto_20150707_1101'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scrapedrecipe',
            name='recipe',
            field=models.ForeignKey(to='recipes.Recipe', on_delete=django.db.models.deletion.SET_NULL, blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='scrapedusesingredient',
            name='recipe',
            field=models.ForeignKey(to='recipes.ScrapedRecipe', related_name='ingredients'),
        ),
    ]
