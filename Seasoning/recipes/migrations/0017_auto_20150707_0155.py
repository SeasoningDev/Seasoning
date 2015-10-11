# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0016_auto_20150707_0154'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scrapedusesingredient',
            name='amount',
            field=models.FloatField(validators=[django.core.validators.MinValueValidator(1e-05)], blank=True, null=True, default=0),
        ),
    ]
