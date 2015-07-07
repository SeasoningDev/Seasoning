# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0026_auto_20150707_1631'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipe',
            name='last_update_time',
            field=models.DateTimeField(default=datetime.datetime(2015, 7, 7, 16, 39, 48, 967856, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='recipe',
            name='time_added',
            field=models.DateTimeField(default=datetime.datetime(2015, 7, 7, 16, 39, 52, 974781, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
    ]
