# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0017_auto_20150707_0155'),
    ]

    operations = [
        migrations.AddField(
            model_name='scrapedusesingredient',
            name='amount_proposal',
            field=models.FloatField(default=0, null=True, validators=[django.core.validators.MinValueValidator(1e-05)], blank=True),
        ),
    ]
