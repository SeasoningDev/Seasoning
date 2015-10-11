# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0019_auto_20150707_0209'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='active_time',
            field=models.IntegerField(verbose_name='Active time', help_text='The time needed to prepare this recipe where you are actually doing something.', blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='passive_time',
            field=models.IntegerField(verbose_name='Passive time', help_text='The time needed to prepare this recipe where you can do something else (e.g. water is boiling)', blank=True, null=True),
        ),
    ]
