# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ingredients', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='availableincountry',
            name='footprint',
        ),
        migrations.RemoveField(
            model_name='availableinsea',
            name='footprint',
        ),
    ]
