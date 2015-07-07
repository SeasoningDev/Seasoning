# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0014_auto_20150707_0051'),
    ]

    operations = [
        migrations.AddField(
            model_name='scrapedrecipe',
            name='course_proposal',
            field=models.CharField(null=True, blank=True, max_length=50),
        ),
    ]
