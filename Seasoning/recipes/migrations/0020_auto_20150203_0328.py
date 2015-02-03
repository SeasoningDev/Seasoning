# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0019_temporaryingredient_used_by'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='recipe',
            name='image',
        ),
        migrations.AlterField(
            model_name='recipe',
            name='active_time',
            field=models.PositiveIntegerField(help_text='The time needed to prepare this recipe where you are actually doing something.', verbose_name='Active time', validators=[django.core.validators.MinValueValidator(1)]),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='passive_time',
            field=models.PositiveIntegerField(help_text='The time needed to prepare this recipe where you can do something else (e.g. water is boiling)', verbose_name='Passive time'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='portions',
            field=models.PositiveIntegerField(help_text='The average amount of people that can be fed by this recipe using the given amounts of ingredients.', verbose_name='Portions', validators=[django.core.validators.MinValueValidator(1)]),
        ),
        migrations.AlterField(
            model_name='recipeimage',
            name='h',
            field=models.FloatField(default=None, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='recipeimage',
            name='visible',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='recipeimage',
            name='w',
            field=models.FloatField(default=1, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='recipeimage',
            name='x',
            field=models.FloatField(default=0, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='recipeimage',
            name='y',
            field=models.FloatField(default=0, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='usesingredient',
            name='amount',
            field=models.FloatField(default=0, validators=[django.core.validators.MinValueValidator(0.001)]),
        ),
    ]
