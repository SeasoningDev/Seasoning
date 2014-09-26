# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import ingredients.models
import general
import imagekit.models.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AvailableInCountry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('production_type', models.CharField(max_length=10, blank=True)),
                ('extra_production_footprint', models.FloatField(default=0)),
                ('date_from', models.DateField()),
                ('date_until', models.DateField()),
                ('footprint', models.FloatField(editable=False)),
            ],
            options={
                'db_table': 'availableincountry',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AvailableInSea',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('production_type', models.CharField(max_length=10, blank=True)),
                ('extra_production_footprint', models.FloatField(default=0)),
                ('date_from', models.DateField()),
                ('date_until', models.DateField()),
                ('footprint', models.FloatField(editable=False)),
                ('endangered', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'availableinsea',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CanUseUnit',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_primary_unit', models.BooleanField(default=False)),
                ('conversion_factor', models.FloatField()),
            ],
            options={
                'db_table': 'canuseunit',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=50L)),
                ('distance', models.IntegerField()),
            ],
            options={
                'db_table': 'country',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=50L)),
                ('plural_name', models.CharField(max_length=50L, blank=True)),
                ('type', models.PositiveSmallIntegerField(default=0, choices=[(0, 'Basis'), (1, 'Seizoensgebonden'), (2, 'Seizoensgebonden Zee')])),
                ('category', models.PositiveSmallIntegerField(choices=[(0, 'Dranken'), (1, 'Fruit'), (2, 'Graanproducten'), (3, 'Groenten'), (4, 'Kruiden en specerijen'), (5, 'Noten en zaden'), (6, 'Oli\xebn'), (7, 'Peulvruchten'), (8, 'Schaal- en schelpdieren'), (9, 'Supplementen'), (10, 'Vis'), (11, 'Vlees'), (12, 'Vleesvervangers'), (13, 'Zuivel')])),
                ('veganism', models.PositiveSmallIntegerField(default=2, choices=[(2, 'Veganistisch'), (1, 'Vegetarisch'), (0, 'Niet-Vegetarisch')])),
                ('description', models.TextField(blank=True)),
                ('conservation_tip', models.TextField(blank=True)),
                ('preparation_tip', models.TextField(blank=True)),
                ('properties', models.TextField(blank=True)),
                ('source', models.TextField(blank=True)),
                ('preservability', models.IntegerField(default=0)),
                ('preservation_footprint', models.FloatField(default=0)),
                ('base_footprint', models.FloatField()),
                ('image', imagekit.models.fields.ProcessedImageField(default=b'images/no_image.jpg', upload_to=ingredients.models.get_image_filename, validators=[general.validate_image_size])),
                ('image_source', models.TextField(blank=True)),
                ('accepted', models.BooleanField(default=False)),
                ('bramified', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'ingredient',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Sea',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=50L)),
                ('distance', models.IntegerField()),
            ],
            options={
                'db_table': 'sea',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Synonym',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=50L)),
                ('plural_name', models.CharField(max_length=50L, blank=True)),
                ('ingredient', models.ForeignKey(related_name=b'synonyms', db_column=b'ingredient', blank=True, to='ingredients.Ingredient', null=True)),
            ],
            options={
                'db_table': 'synonym',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TransportMethod',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=20L)),
                ('emission_per_km', models.FloatField()),
            ],
            options={
                'db_table': 'transportmethod',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Unit',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=30L)),
                ('short_name', models.CharField(max_length=10L, blank=True)),
                ('ratio', models.FloatField(null=True, blank=True)),
                ('parent_unit', models.ForeignKey(related_name=b'derived_units', default=None, blank=True, to='ingredients.Unit', null=True)),
            ],
            options={
                'db_table': 'unit',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='ingredient',
            name='useable_units',
            field=models.ManyToManyField(to='ingredients.Unit', through='ingredients.CanUseUnit'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='canuseunit',
            name='ingredient',
            field=models.ForeignKey(to='ingredients.Ingredient', db_column=b'ingredient'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='canuseunit',
            name='unit',
            field=models.ForeignKey(related_name=b'useable_by', db_column=b'unit', to='ingredients.Unit'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='availableinsea',
            name='ingredient',
            field=models.ForeignKey(related_name=b'available_in_sea', db_column=b'ingredient', to='ingredients.Ingredient'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='availableinsea',
            name='location',
            field=models.ForeignKey(to='ingredients.Sea', db_column=b'sea'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='availableinsea',
            name='transport_method',
            field=models.ForeignKey(to='ingredients.TransportMethod', db_column=b'transport_method'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='availableincountry',
            name='ingredient',
            field=models.ForeignKey(related_name=b'available_in_country', db_column=b'ingredient', to='ingredients.Ingredient'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='availableincountry',
            name='location',
            field=models.ForeignKey(to='ingredients.Country', db_column=b'country'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='availableincountry',
            name='transport_method',
            field=models.ForeignKey(to='ingredients.TransportMethod', db_column=b'transport_method'),
            preserve_default=True,
        ),
    ]
