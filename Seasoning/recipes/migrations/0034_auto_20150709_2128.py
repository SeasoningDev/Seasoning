# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0033_auto_20150709_2125'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scrapedusesingredient',
            name='amount_proposal',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
