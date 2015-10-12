# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import imagekit.models.fields
import ingredients.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AvailableInCountry',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('production_type', models.CharField(max_length=10, blank=True)),
                ('extra_production_footprint', models.FloatField(default=0)),
                ('date_from', models.DateField()),
                ('date_until', models.DateField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='AvailableInSea',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('production_type', models.CharField(max_length=10, blank=True)),
                ('extra_production_footprint', models.FloatField(default=0)),
                ('date_from', models.DateField()),
                ('date_until', models.DateField()),
                ('endangered', models.BooleanField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CanUseUnit',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('conversion_ratio', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('distance', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('name', models.CharField(max_length=50, unique=True)),
                ('plural_name', models.CharField(max_length=50, blank=True)),
                ('type', models.PositiveSmallIntegerField(default=0, choices=[(0, 'Basis'), (1, 'Seizoensgebonden'), (2, 'Seizoensgebonden Zee')])),
                ('category', models.PositiveSmallIntegerField(choices=[(0, 'Dranken'), (1, 'Fruit'), (2, 'Graanproducten'), (3, 'Groenten'), (4, 'Kruiden en specerijen'), (5, 'Noten en zaden'), (6, 'Oliën'), (7, 'Peulvruchten'), (8, 'Schaal- en schelpdieren'), (9, 'Supplementen'), (10, 'Vis'), (11, 'Vlees'), (12, 'Vleesvervangers'), (13, 'Zuivel')])),
                ('veganism', models.PositiveSmallIntegerField(default=2, choices=[(2, 'Veganistisch'), (1, 'Vegetarisch'), (0, 'Niet-Vegetarisch')])),
                ('description', models.TextField(blank=True)),
                ('conservation_tip', models.TextField(blank=True)),
                ('preparation_tip', models.TextField(blank=True)),
                ('properties', models.TextField(blank=True)),
                ('source', models.TextField(blank=True)),
                ('preservability', models.IntegerField(default=0)),
                ('preservation_footprint', models.FloatField(default=0)),
                ('base_footprint', models.FloatField()),
                ('image', imagekit.models.fields.ProcessedImageField(default='images/no_image.jpg', upload_to=ingredients.models.get_image_filename)),
                ('image_source', models.TextField(blank=True)),
                ('accepted', models.BooleanField(default=False)),
                ('bramified', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='Sea',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('distance', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Synonym',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('name', models.CharField(max_length=50, unique=True)),
                ('plural_name', models.CharField(max_length=50, blank=True)),
                ('ingredient', models.ForeignKey(null=True, blank=True, related_name='synonyms', to='ingredients.Ingredient')),
            ],
        ),
        migrations.CreateModel(
            name='TransportMethod',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=20)),
                ('emissions_per_km', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='Unit',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('name', models.CharField(max_length=30, unique=True)),
                ('short_name', models.CharField(max_length=10, blank=True)),
                ('ratio', models.FloatField(null=True, blank=True)),
                ('parent_unit', models.ForeignKey(null=True, blank=True, related_name='derived_units', to='ingredients.Unit', default=None)),
            ],
        ),
        migrations.AddField(
            model_name='ingredient',
            name='useable_units',
            field=models.ManyToManyField(to='ingredients.Unit', through='ingredients.CanUseUnit'),
        ),
        migrations.AddField(
            model_name='canuseunit',
            name='ingredient',
            field=models.ForeignKey(related_name='can_use_units', to='ingredients.Ingredient'),
        ),
        migrations.AddField(
            model_name='canuseunit',
            name='unit',
            field=models.ForeignKey(related_name='useable_by', to='ingredients.Unit'),
        ),
        migrations.AddField(
            model_name='availableinsea',
            name='ingredient',
            field=models.ForeignKey(related_name='available_in_sea', to='ingredients.Ingredient'),
        ),
        migrations.AddField(
            model_name='availableinsea',
            name='location',
            field=models.ForeignKey(to='ingredients.Sea'),
        ),
        migrations.AddField(
            model_name='availableinsea',
            name='transport_method',
            field=models.ForeignKey(to='ingredients.TransportMethod'),
        ),
        migrations.AddField(
            model_name='availableincountry',
            name='ingredient',
            field=models.ForeignKey(related_name='available_in_country', to='ingredients.Ingredient'),
        ),
        migrations.AddField(
            model_name='availableincountry',
            name='location',
            field=models.ForeignKey(to='ingredients.Country'),
        ),
        migrations.AddField(
            model_name='availableincountry',
            name='transport_method',
            field=models.ForeignKey(to='ingredients.TransportMethod'),
        ),
    ]
