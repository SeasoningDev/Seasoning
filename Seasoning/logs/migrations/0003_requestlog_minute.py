# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('logs', '0002_auto_20140915_1627'),
    ]

    operations = [
        migrations.AddField(
            model_name='requestlog',
            name='minute',
            field=models.PositiveIntegerField(default=0, editable=False),
            preserve_default=False,
        ),
    ]
