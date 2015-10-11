# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0022_auto_20150707_1104'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipe',
            name='_footprint',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
    ]
