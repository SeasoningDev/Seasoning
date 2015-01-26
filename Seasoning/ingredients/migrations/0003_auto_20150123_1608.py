# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ingredients', '0002_auto_20140926_1221'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='canuseunit',
            unique_together=set([('ingredient', 'unit')]),
        ),
    ]
