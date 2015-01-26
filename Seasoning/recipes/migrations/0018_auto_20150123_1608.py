# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0017_auto_20150120_2356'),
    ]

    operations = [
        migrations.AlterField(
            model_name='incompleterecipe',
            name='active_time',
            field=models.IntegerField(default=0, help_text='The time needed to prepare this recipe where you are actually doing something.', null=True, verbose_name='Active time', blank=True),
        ),
        migrations.AlterField(
            model_name='incompleterecipe',
            name='author',
            field=models.ForeignKey(related_name=b'incomplete_recipes', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='incompleterecipe',
            name='description',
            field=models.TextField(default=b'', validators=[django.core.validators.MaxLengthValidator(300)], blank=True, help_text='A few sentences describing the recipe (Maximum 300 characters).', null=True, verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='incompleterecipe',
            name='instructions',
            field=models.TextField(default=b'', help_text='Detailed instructions for preparing this recipe.', null=True, verbose_name='Instructions', blank=True),
        ),
        migrations.AlterField(
            model_name='incompleterecipe',
            name='name',
            field=models.CharField(default=b'', max_length=100, blank=True, help_text='The names of the recipe.', null=True, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='incompleterecipe',
            name='passive_time',
            field=models.IntegerField(default=0, help_text='The time needed to prepare this recipe where you can do something else (e.g. water is boiling)', null=True, verbose_name='Passive time', blank=True),
        ),
        migrations.AlterField(
            model_name='incompleterecipe',
            name='portions',
            field=models.PositiveIntegerField(default=0, help_text='The average amount of people that can be fed by this recipe using the given amounts of ingredients.', null=True, verbose_name='Portions', blank=True),
        ),
    ]
