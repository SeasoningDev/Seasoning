# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0046_auto_20160605_1245'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='cached_footprint_category',
            field=models.PositiveSmallIntegerField(blank=True, null=True, choices=[(0, 'A+'), (1, 'A'), (2, 'B'), (3, 'C'), (4, 'D')]),
        ),
    ]
