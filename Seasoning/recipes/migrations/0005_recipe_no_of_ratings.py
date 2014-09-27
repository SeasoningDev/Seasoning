# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0004_auto_20140926_1928'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipe',
            name='no_of_ratings',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
    ]
