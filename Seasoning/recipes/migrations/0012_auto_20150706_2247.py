# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from datetime import date


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0011_scrapedrecipe_recipe'),
    ]

    operations = [
        migrations.AddField(
            model_name='scrapedrecipe',
            name='deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='scrapedrecipe',
            name='first_scrape_date',
            field=models.DateField(default=date.today(), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='scrapedrecipe',
            name='last_update_date',
            field=models.DateField(default=date.today(), auto_now=True),
            preserve_default=False,
        ),
    ]
