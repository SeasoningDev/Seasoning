# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0009_scrapedrecipe_image_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scrapedrecipe',
            name='image_url',
            field=models.URLField(blank=True, null=True),
        ),
    ]
