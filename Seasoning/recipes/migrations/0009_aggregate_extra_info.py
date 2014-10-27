# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0008_aggregate'),
    ]

    operations = [
        migrations.AddField(
            model_name='aggregate',
            name='extra_info',
            field=models.TextField(default=b''),
            preserve_default=True,
        ),
    ]
