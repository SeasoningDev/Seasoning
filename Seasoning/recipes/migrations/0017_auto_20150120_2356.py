# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0016_recipeimage_visible'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipeimage',
            name='h',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='recipeimage',
            name='w',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='recipeimage',
            name='x',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='recipeimage',
            name='y',
            field=models.FloatField(null=True, blank=True),
        ),
    ]
