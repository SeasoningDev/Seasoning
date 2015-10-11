# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0042_auto_20150717_0715'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scrapedrecipe',
            name='scraped_name',
            field=models.CharField(blank=True, default='', max_length=300, null=True, verbose_name='Scraped Name'),
        ),
    ]
