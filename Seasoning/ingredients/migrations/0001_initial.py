# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import ingredients.models
import imagekit.models.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AvailableInCountry',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('production_type', models.CharField(max_length=10, blank=True)),
                ('extra_production_footprint', models.FloatField(default=0)),
                ('date_from', models.DateField()),
                ('date_until', models.DateField()),
                ('footprint', models.FloatField(editable=False, null=True, blank=True)),
            ],
            options={
                'db_table': 'availableincountry',
            },
        ),
        migrations.CreateModel(
            name='AvailableInSea',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('production_type', models.CharField(max_length=10, blank=True)),
                ('extra_production_footprint', models.FloatField(default=0)),
                ('date_from', models.DateField()),
                ('date_until', models.DateField()),
                ('footprint', models.FloatField(editable=False, null=True, blank=True)),
                ('endangered', models.BooleanField()),
            ],
            options={
                'db_table': 'availableinsea',
            },
        ),
        migrations.CreateModel(
            name='CanUseUnit',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('is_primary_unit', models.BooleanField(null=True, blank=True)),
                ('conversion_factor', models.FloatField()),
            ],
            options={
                'db_table': 'canuseunit',
            },
        ),
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50)),
                ('distance', models.IntegerField()),
            ],
            options={
                'db_table': 'country',
            },
        ),
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('name', models.CharField(max_length=50, unique=True)),
                ('plural_name', models.CharField(max_length=50, blank=True)),
                ('type', models.PositiveSmallIntegerField(choices=[(0, 'Basis'), (1, 'Seizoensgebonden'), (2, 'Seizoensgebonden Zee')], default=0)),
                ('category', models.PositiveSmallIntegerField(choices=[(0, 'Dranken'), (1, 'Fruit'), (2, 'Graanproducten'), (3, 'Groenten'), (4, 'Kruiden en specerijen'), (5, 'Noten en zaden'), (6, 'Oliën'), (7, 'Peulvruchten'), (8, 'Schaal- en schelpdieren'), (9, 'Supplementen'), (10, 'Vis'), (11, 'Vlees'), (12, 'Vleesvervangers'), (13, 'Zuivel')])),
                ('veganism', models.PositiveSmallIntegerField(choices=[(2, 'Veganistisch'), (1, 'Vegetarisch'), (0, 'Niet-Vegetarisch')], default=2)),
                ('description', models.TextField(blank=True)),
                ('conservation_tip', models.TextField(blank=True)),
                ('preparation_tip', models.TextField(blank=True)),
                ('properties', models.TextField(blank=True)),
                ('source', models.TextField(blank=True)),
                ('preservability', models.IntegerField(default=0)),
                ('preservation_footprint', models.FloatField(default=0)),
                ('base_footprint', models.FloatField()),
                ('image', imagekit.models.fields.ProcessedImageField(upload_to=ingredients.models.get_image_filename, default='images/no_image.jpg')),
                ('image_source', models.TextField(blank=True)),
                ('accepted', models.BooleanField(default=False)),
                ('bramified', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'ingredient',
            },
        ),
        migrations.CreateModel(
            name='Sea',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50)),
                ('distance', models.IntegerField()),
            ],
            options={
                'db_table': 'sea',
            },
        ),
        migrations.CreateModel(
            name='Synonym',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('name', models.CharField(max_length=50, unique=True)),
                ('plural_name', models.CharField(max_length=50, blank=True)),
                ('ingredient', models.ForeignKey(to='ingredients.Ingredient', blank=True, db_column='ingredient', null=True, related_name='synonyms')),
            ],
            options={
                'db_table': 'synonym',
            },
        ),
        migrations.CreateModel(
            name='TransportMethod',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=20)),
                ('emission_per_km', models.FloatField()),
            ],
            options={
                'db_table': 'transportmethod',
            },
        ),
        migrations.CreateModel(
            name='Unit',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('name', models.CharField(max_length=30, unique=True)),
                ('short_name', models.CharField(max_length=10, blank=True)),
                ('ratio', models.FloatField(blank=True, null=True)),
                ('parent_unit', models.ForeignKey(to='ingredients.Unit', blank=True, default=None, null=True, related_name='derived_units')),
            ],
            options={
                'db_table': 'unit',
            },
        ),
        migrations.AddField(
            model_name='ingredient',
            name='useable_units',
            field=models.ManyToManyField(to='ingredients.Unit', through='ingredients.CanUseUnit'),
        ),
        migrations.AddField(
            model_name='canuseunit',
            name='ingredient',
            field=models.ForeignKey(to='ingredients.Ingredient', db_column='ingredient'),
        ),
        migrations.AddField(
            model_name='canuseunit',
            name='unit',
            field=models.ForeignKey(to='ingredients.Unit', db_column='unit', related_name='useable_by'),
        ),
        migrations.AddField(
            model_name='availableinsea',
            name='ingredient',
            field=models.ForeignKey(to='ingredients.Ingredient', db_column='ingredient', related_name='available_in_sea'),
        ),
        migrations.AddField(
            model_name='availableinsea',
            name='location',
            field=models.ForeignKey(to='ingredients.Sea', db_column='sea'),
        ),
        migrations.AddField(
            model_name='availableinsea',
            name='transport_method',
            field=models.ForeignKey(to='ingredients.TransportMethod', db_column='transport_method'),
        ),
        migrations.AddField(
            model_name='availableincountry',
            name='ingredient',
            field=models.ForeignKey(to='ingredients.Ingredient', db_column='ingredient', related_name='available_in_country'),
        ),
        migrations.AddField(
            model_name='availableincountry',
            name='location',
            field=models.ForeignKey(to='ingredients.Country', db_column='country'),
        ),
        migrations.AddField(
            model_name='availableincountry',
            name='transport_method',
            field=models.ForeignKey(to='ingredients.TransportMethod', db_column='transport_method'),
        ),
    ]
