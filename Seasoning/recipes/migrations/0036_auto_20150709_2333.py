# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0035_auto_20150709_2314'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scrapedusesingredient',
            name='group',
            field=models.CharField(blank=True, null=True, max_length=500),
        ),
        migrations.AlterField(
            model_name='scrapedusesingredient',
            name='ingredient_proposal',
            field=models.CharField(max_length=500),
        ),
    ]
