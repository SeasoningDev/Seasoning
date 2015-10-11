# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0023_recipe__footprint'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='description',
            field=models.TextField(blank=True, verbose_name='Description', help_text='A few sentences describing the recipe (Maximum 140 characters).', validators=[django.core.validators.MaxLengthValidator(140)], null=True),
        ),
    ]
