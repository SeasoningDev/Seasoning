# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0010_auto_20150706_2132'),
    ]

    operations = [
        migrations.AddField(
            model_name='scrapedrecipe',
            name='recipe',
            field=models.ForeignKey(to='recipes.Recipe', null=True, blank=True),
        ),
    ]
