# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0044_auto_20150725_1250'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipe',
            name='cached_footprint_category',
            field=models.PositiveSmallIntegerField(default=0, choices=[(0, 'A+'), (1, 'A'), (2, 'B'), (3, 'C'), (4, 'D')]),
            preserve_default=False,
        ),
    ]
