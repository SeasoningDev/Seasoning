# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0029_auto_20150708_1145'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='recipe',
            name='_footprint_category',
        ),
    ]
