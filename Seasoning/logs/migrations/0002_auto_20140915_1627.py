# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('logs', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='requestlog',
            name='user_agent',
            field=models.CharField(max_length=200),
        ),
    ]
