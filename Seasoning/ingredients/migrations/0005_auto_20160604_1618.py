# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ingredients', '0004_auto_20150708_2025'),
    ]

    operations = [
        migrations.AddField(
            model_name='unit',
            name='plural_name',
            field=models.CharField(max_length=30, blank=True),
        ),
        migrations.AddField(
            model_name='unit',
            name='synonyms',
            field=models.CharField(max_length=100, blank=True),
        ),
    ]
