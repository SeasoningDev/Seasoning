# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import recipes.models
import django.core.validators
import imagekit.models.fields
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('ingredients', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cuisine',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('name', models.CharField(max_length=50)),
            ],
            options={
                'ordering': ['name'],
                'db_table': 'cuisine',
            },
        ),
        migrations.CreateModel(
            name='ExternalSite',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('name', models.CharField(help_text='The names of the external website.', verbose_name='Name', max_length=200)),
                ('url', models.CharField(help_text='The home url of the external website', verbose_name='URL', max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('name', models.CharField(help_text='The names of the recipe.', verbose_name='Name', max_length=100)),
                ('time_added', models.DateTimeField(auto_now_add=True, null=True, blank=True)),
                ('external', models.BooleanField(default=False)),
                ('external_url', models.CharField(max_length=1000, blank=True, null=True)),
                ('course', models.PositiveSmallIntegerField(help_text='The type of course this recipe will provide.', verbose_name='Course', choices=[(0, 'Voorgerecht'), (1, 'Brood'), (2, 'Ontbijt'), (3, 'Dessert'), (4, 'Drank'), (5, 'Hoofdgerecht'), (6, 'Salade'), (7, 'Bijgerecht'), (8, 'Soep'), (9, 'Marinades en sauzen')])),
                ('description', models.TextField(help_text='A few sentences describing the recipe (Maximum 140 characters).', verbose_name='Description', validators=[django.core.validators.MaxLengthValidator(140)])),
                ('portions', models.PositiveIntegerField(help_text='The average amount of people that can be fed by this recipe using the given amounts of ingredients.', verbose_name='Portions')),
                ('active_time', models.IntegerField(help_text='The time needed to prepare this recipe where you are actually doing something.', verbose_name='Active time')),
                ('passive_time', models.IntegerField(help_text='The time needed to prepare this recipe where you can do something else (e.g. water is boiling)', verbose_name='Passive time')),
                ('rating', models.FloatField(blank=True, editable=False, null=True, default=None)),
                ('number_of_votes', models.PositiveIntegerField(editable=False, default=0)),
                ('extra_info', models.TextField(help_text='Extra info about the ingredients or needed tools (e.g. "You will need a mixer for this recipe" or "Use big potatoes")', blank=True, verbose_name='Extra info', default='')),
                ('instructions', models.TextField(help_text='Detailed instructions for preparing this recipe.', verbose_name='Instructions')),
                ('image', imagekit.models.fields.ProcessedImageField(help_text='An image of this recipe. Please do not use copyrighted images, these will be removed as quick as possible.', upload_to=recipes.models.get_image_filename, default='images/no_image.jpg')),
                ('footprint', models.FloatField(editable=False, null=True, blank=True)),
                ('veganism', models.PositiveSmallIntegerField(editable=False, choices=[(2, 'Veganistisch'), (1, 'Vegetarisch'), (0, 'Niet-Vegetarisch')], null=True, blank=True)),
                ('endangered', models.BooleanField(editable=False, default=False, null=True, blank=True)),
                ('inseason', models.BooleanField(editable=False, default=False, null=True, blank=True)),
                ('accepted', models.BooleanField(default=False, null=True, blank=True)),
                ('cuisine', models.ForeignKey(to='recipes.Cuisine', blank=True, verbose_name='Cuisine', null=True, help_text='The type of cuisine this recipe represents.', db_column='cuisine')),
                ('external_site', models.ForeignKey(to='recipes.ExternalSite', blank=True, null=True)),
            ],
            options={
                'db_table': 'recipe',
            },
        ),
        migrations.CreateModel(
            name='UnknownIngredient',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('name', models.CharField(max_length=50)),
                ('for_recipe', models.ForeignKey(to='recipes.Recipe')),
                ('real_ingredient', models.ForeignKey(to='ingredients.Ingredient')),
            ],
            options={
                'db_table': 'unknown_ingredient',
            },
        ),
        migrations.CreateModel(
            name='UsesIngredient',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('group', models.CharField(max_length=100, blank=True)),
                ('amount', models.FloatField(default=0, validators=[django.core.validators.MinValueValidator(1e-05)])),
                ('footprint', models.FloatField(editable=False, null=True, blank=True)),
                ('ingredient', models.ForeignKey(to='ingredients.Ingredient', db_column='ingredient')),
                ('recipe', models.ForeignKey(to='recipes.Recipe', db_column='recipe', related_name='uses')),
                ('unit', models.ForeignKey(to='ingredients.Unit', db_column='unit')),
            ],
            options={
                'db_table': 'usesingredient',
            },
        ),
        migrations.CreateModel(
            name='Vote',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('score', models.PositiveIntegerField(validators=[django.core.validators.MaxValueValidator(5)])),
                ('time_added', models.DateTimeField(editable=False, default=datetime.datetime.now)),
                ('time_changed', models.DateTimeField(editable=False, default=datetime.datetime.now)),
                ('recipe', models.ForeignKey(to='recipes.Recipe', related_name='votes')),
            ],
        ),
        migrations.AddField(
            model_name='recipe',
            name='ingredients',
            field=models.ManyToManyField(to='ingredients.Ingredient', editable=False, through='recipes.UsesIngredient'),
        ),
    ]
