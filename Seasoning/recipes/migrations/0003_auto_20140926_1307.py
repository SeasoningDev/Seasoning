# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_auto_20140925_2304'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='recipe',
            name='complete_information',
        ),
        migrations.RemoveField(
            model_name='recipe',
            name='endangered',
        ),
        migrations.RemoveField(
            model_name='recipe',
            name='footprint',
        ),
        migrations.RemoveField(
            model_name='recipe',
            name='inseason',
        ),
        migrations.RemoveField(
            model_name='recipe',
            name='number_of_votes',
        ),
        migrations.RemoveField(
            model_name='recipe',
            name='rating',
        ),
        migrations.RemoveField(
            model_name='recipe',
            name='veganism',
        ),
        migrations.RemoveField(
            model_name='usesingredient',
            name='footprint',
        ),
    ]
