# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0041_auto_20150717_0706'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='scrapedrecipe',
            unique_together=set([('scraped_name', 'external_site')]),
        ),
    ]
