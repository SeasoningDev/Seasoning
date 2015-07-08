# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0028_auto_20150708_0930'),
    ]

    operations = [
        migrations.RenameField(
            model_name='recipedistribution',
            old_name='value',
            new_name='parameter_value',
        ),
        migrations.AlterField(
            model_name='recipedistribution',
            name='parameter',
            field=models.PositiveSmallIntegerField(choices=[(0, 'Mean'), (1, 'Standard Deviation')]),
        ),
    ]
