# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ingredients', '0003_auto_20150707_1624'),
    ]

    operations = [
        migrations.RenameField(
            model_name='transportmethod',
            old_name='emission_per_km',
            new_name='emissions_per_km',
        ),
    ]
