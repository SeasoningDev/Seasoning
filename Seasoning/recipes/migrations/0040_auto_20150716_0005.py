# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0039_auto_20150716_0005'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipedistribution',
            name='group',
            field=models.PositiveSmallIntegerField(choices=[(100, 'All Recipes'), (0, 'Voorgerecht'), (1, 'Brood'), (2, 'Ontbijt'), (3, 'Dessert'), (4, 'Drank'), (5, 'Hoofdgerecht'), (6, 'Salade'), (7, 'Bijgerecht'), (8, 'Soep'), (9, 'Marinades en sauzen')]),
        ),
    ]
