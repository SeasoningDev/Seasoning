# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0014_auto_20150120_0003'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipeimage',
            name='h',
            field=models.FloatField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='recipeimage',
            name='w',
            field=models.FloatField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='recipeimage',
            name='x',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='recipeimage',
            name='y',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
    ]
