# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0015_scrapedrecipe_course_proposal'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scrapedusesingredient',
            name='unit_proposal',
            field=models.CharField(blank=True, null=True, max_length=50),
        ),
    ]
