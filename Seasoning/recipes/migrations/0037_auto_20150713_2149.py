# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0036_auto_20150709_2333'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usesingredient',
            name='group',
            field=models.CharField(null=True, max_length=100, blank=True),
        ),
    ]
