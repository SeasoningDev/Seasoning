# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('logs', '0003_requestlog_minute'),
    ]

    operations = [
        migrations.AlterField(
            model_name='requestlog',
            name='minute',
            field=models.CharField(max_length=12, editable=False),
        ),
    ]
