# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0043_auto_20150720_1312'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scrapedrecipe',
            name='course_proposal',
            field=models.CharField(null=True, blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='scrapedrecipe',
            name='scraped_name',
            field=models.CharField(verbose_name='Scraped Name', null=True, blank=True, max_length=300),
        ),
    ]
