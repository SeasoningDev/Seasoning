# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0012_auto_20150706_2247'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='scrapedingredient',
            name='ingredient',
        ),
        migrations.RemoveField(
            model_name='scrapedingredient',
            name='used_by',
        ),
        migrations.RemoveField(
            model_name='scrapedunit',
            name='unit',
        ),
        migrations.RemoveField(
            model_name='scrapedrecipe',
            name='ingredients',
        ),
        migrations.AddField(
            model_name='scrapedusesingredient',
            name='ingredient_proposal',
            field=models.CharField(default='a', max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='scrapedusesingredient',
            name='unit_proposal',
            field=models.CharField(default='a', max_length=50),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='scrapedrecipe',
            name='deleted',
            field=models.BooleanField(),
        ),
        migrations.AlterField(
            model_name='scrapedusesingredient',
            name='ingredient',
            field=models.ForeignKey(to='ingredients.Ingredient', blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='scrapedusesingredient',
            name='recipe',
            field=models.ForeignKey(to='recipes.ScrapedRecipe', related_name='ingredients'),
        ),
        migrations.AlterField(
            model_name='scrapedusesingredient',
            name='unit',
            field=models.ForeignKey(to='ingredients.Unit', blank=True, null=True),
        ),
        migrations.DeleteModel(
            name='ScrapedIngredient',
        ),
        migrations.DeleteModel(
            name='ScrapedUnit',
        ),
    ]
