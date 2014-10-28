# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import general
import recipes.models
import imagekit.models.fields
import datetime
from django.conf import settings
import django.core.validators

class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('ingredients', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cuisine',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
            ],
            options={
                'ordering': ['name'],
                'db_table': 'cuisine',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ExternalSite',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text='The names of the external website.', max_length=200, verbose_name='Name')),
                ('url', models.CharField(help_text='The home url of the external website', max_length=200, verbose_name='URL')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text='The names of the recipe.', max_length=100, verbose_name='Name')),
                ('time_added', models.DateTimeField(auto_now_add=True)),
                ('external', models.BooleanField(default=False)),
                ('external_url', models.CharField(max_length=1000, null=True, blank=True)),
                ('course', models.PositiveSmallIntegerField(help_text='The type of course this recipe will provide.', verbose_name='Course', choices=[(0, 'Voorgerecht'), (1, 'Brood'), (2, 'Ontbijt'), (3, 'Dessert'), (4, 'Drank'), (5, 'Hoofdgerecht'), (6, 'Salade'), (7, 'Bijgerecht'), (8, 'Soep'), (9, 'Marinades en sauzen')])),
                ('description', models.TextField(help_text='A few sentences describing the recipe (Maximum 140 characters).', verbose_name='Description', validators=[django.core.validators.MaxLengthValidator(140)])),
                ('portions', models.PositiveIntegerField(help_text='The average amount of people that can be fed by this recipe using the given amounts of ingredients.', verbose_name='Portions')),
                ('active_time', models.IntegerField(help_text='The time needed to prepare this recipe where you are actually doing something.', verbose_name='Active time')),
                ('passive_time', models.IntegerField(help_text='The time needed to prepare this recipe where you can do something else (e.g. water is boiling)', verbose_name='Passive time')),
                ('rating', models.FloatField(default=None, null=True, editable=False, blank=True)),
                ('number_of_votes', models.PositiveIntegerField(default=0, editable=False)),
                ('extra_info', models.TextField(default=b'', help_text='Extra info about the ingredients or needed tools (e.g. "You will need a mixer for this recipe" or "Use big potatoes")', verbose_name='Extra info', blank=True)),
                ('instructions', models.TextField(help_text='Detailed instructions for preparing this recipe.', verbose_name='Instructions')),
                ('image', imagekit.models.fields.ProcessedImageField(default=b'images/no_image.jpg', help_text='An image of this recipe. Please do not use copyrighted images, these will be removed as quick as possible.', upload_to=recipes.models.get_image_filename, validators=[general.validate_image_size])),
                ('footprint', models.FloatField(editable=False)),
                ('veganism', models.PositiveSmallIntegerField(editable=False, choices=[(2, 'Veganistisch'), (1, 'Vegetarisch'), (0, 'Niet-Vegetarisch')])),
                ('endangered', models.BooleanField(default=False, editable=False)),
                ('inseason', models.BooleanField(default=False, editable=False)),
                ('accepted', models.BooleanField(default=False)),
                ('author', models.ForeignKey(related_name=b'recipes', to=settings.AUTH_USER_MODEL, null=True)),
                ('cuisine', models.ForeignKey(db_column=b'cuisine', to='recipes.Cuisine', blank=True, help_text='The type of cuisine this recipe represents.', null=True, verbose_name='Cuisine')),
                ('external_site', models.ForeignKey(blank=True, to='recipes.ExternalSite', null=True)),
            ],
            options={
                'db_table': 'recipe',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UnknownIngredient',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50L)),
                ('for_recipe', models.ForeignKey(to='recipes.Recipe')),
                ('real_ingredient', models.ForeignKey(to='ingredients.Ingredient')),
                ('requested_by', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'unknown_ingredient',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UsesIngredient',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('group', models.CharField(max_length=100, blank=True)),
                ('amount', models.FloatField(default=0, validators=[django.core.validators.MinValueValidator(1e-05)])),
                ('footprint', models.FloatField(null=True, editable=False)),
                ('ingredient', models.ForeignKey(to='ingredients.Ingredient', db_column=b'ingredient')),
                ('recipe', models.ForeignKey(related_name=b'uses', db_column=b'recipe', to='recipes.Recipe')),
                ('unit', models.ForeignKey(to='ingredients.Unit', db_column=b'unit')),
            ],
            options={
                'db_table': 'usesingredient',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Vote',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('score', models.PositiveIntegerField(validators=[django.core.validators.MaxValueValidator(5)])),
                ('time_added', models.DateTimeField(default=datetime.datetime.now, editable=False)),
                ('time_changed', models.DateTimeField(default=datetime.datetime.now, editable=False)),
                ('recipe', models.ForeignKey(related_name=b'votes', to='recipes.Recipe')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='vote',
            unique_together=set([('recipe', 'user')]),
        ),
        migrations.AddField(
            model_name='recipe',
            name='ingredients',
            field=models.ManyToManyField(to='ingredients.Ingredient', editable=False, through='recipes.UsesIngredient'),
            preserve_default=True,
        ),
    ]
