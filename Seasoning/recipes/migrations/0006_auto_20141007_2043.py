# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0005_recipe_no_of_ratings'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='description',
            field=models.TextField(help_text='A few sentences describing the recipe (Maximum 300 characters).', verbose_name='Description', validators=[django.core.validators.MaxLengthValidator(300)]),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='rating',
            field=models.FloatField(default=None, null=True, editable=False, blank=True),
        ),
    ]
