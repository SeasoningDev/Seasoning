# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0011_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='incompleterecipe',
            name='ignore',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='recipeimage',
            name='incomplete_recipe',
            field=models.ForeignKey(related_name=b'images', blank=True, to='recipes.IncompleteRecipe', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='incompleterecipe',
            name='external_site',
            field=models.ForeignKey(related_name=b'incomplete_recipes', blank=True, to='recipes.ExternalSite', null=True),
        ),
        migrations.AlterField(
            model_name='recipeimage',
            name='recipe',
            field=models.ForeignKey(related_name=b'images', blank=True, to='recipes.Recipe', null=True),
        ),
    ]
