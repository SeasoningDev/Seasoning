# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0038_auto_20150714_1927'),
    ]

    operations = [
        migrations.RenameField(
            model_name='recipedistribution',
            old_name='course',
            new_name='group',
        ),
        migrations.AlterUniqueTogether(
            name='recipedistribution',
            unique_together=set([('group', 'parameter')]),
        ),
    ]
