# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0018_scrapedusesingredient_amount_proposal'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scrapedrecipe',
            name='image_url',
            field=models.URLField(max_length=400, blank=True, null=True),
        ),
    ]
