# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_auto_20150705_2355'),
    ]

    operations = [
        migrations.CreateModel(
            name='RecipeDistribution',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('course', models.PositiveSmallIntegerField(choices=[(0, 'Voorgerecht'), (1, 'Brood'), (2, 'Ontbijt'), (3, 'Dessert'), (4, 'Drank'), (5, 'Hoofdgerecht'), (6, 'Salade'), (7, 'Bijgerecht'), (8, 'Soep'), (9, 'Marinades en sauzen')])),
                ('parameter', models.PositiveSmallIntegerField(choices=[(0, 'Gemiddelde'), (1, 'Standaardafwijking')])),
                ('value', models.FloatField()),
            ],
        ),
    ]
