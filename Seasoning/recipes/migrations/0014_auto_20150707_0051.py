# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0013_auto_20150707_0047'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scrapedrecipe',
            name='deleted',
            field=models.BooleanField(default=False),
        ),
    ]
