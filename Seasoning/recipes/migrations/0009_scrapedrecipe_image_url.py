# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0008_auto_20150706_2119'),
    ]

    operations = [
        migrations.AddField(
            model_name='scrapedrecipe',
            name='image_url',
            field=models.URLField(default=None),
            preserve_default=False,
        ),
    ]
