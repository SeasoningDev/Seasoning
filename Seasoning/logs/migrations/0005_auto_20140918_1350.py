# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('logs', '0004_auto_20140915_2008'),
    ]

    operations = [
        migrations.AlterField(
            model_name='requestlog',
            name='referer',
            field=models.CharField(max_length=300),
        ),
        migrations.AlterField(
            model_name='requestlog',
            name='uri',
            field=models.CharField(max_length=300),
        ),
        migrations.AlterField(
            model_name='requestlog',
            name='user_agent',
            field=models.CharField(max_length=300),
        ),
    ]
