# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0003_recipedistribution'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='recipedistribution',
            unique_together=set([('course', 'parameter')]),
        ),
    ]
