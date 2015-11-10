# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0040_auto_20150716_0005'),
    ]

    operations = [
        migrations.AddField(
            model_name='scrapedrecipe',
            name='scraped_name',
            field=models.CharField(max_length=300, verbose_name='Scraped Name', default=''),
        ),
        migrations.AlterField(
            model_name='scrapedrecipe',
            name='name',
            field=models.CharField(blank=True, max_length=300, default='', null=True, help_text='The name of the recipe.', verbose_name='Name'),
        ),
    ]
