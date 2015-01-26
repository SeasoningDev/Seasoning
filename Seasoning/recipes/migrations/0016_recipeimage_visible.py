# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0015_auto_20150120_1036'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipeimage',
            name='visible',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
