# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ingredients', '0002_auto_20150705_2355'),
        ('recipes', '0004_auto_20150706_0036'),
    ]

    operations = [
        migrations.CreateModel(
            name='IncompleteRecipe',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('name', models.CharField(max_length=100, verbose_name='Name', default='', null=True, blank=True, help_text='The names of the recipe.')),
                ('external', models.BooleanField(default=False)),
                ('external_url', models.CharField(blank=True, null=True, max_length=1000)),
                ('course', models.PositiveSmallIntegerField(choices=[(0, 'Voorgerecht'), (1, 'Brood'), (2, 'Ontbijt'), (3, 'Dessert'), (4, 'Drank'), (5, 'Hoofdgerecht'), (6, 'Salade'), (7, 'Bijgerecht'), (8, 'Soep'), (9, 'Marinades en sauzen')], blank=True, verbose_name='Course', null=True, help_text='The type of course this recipe will provide.')),
                ('cuisine_proposal', models.CharField(blank=True, null=True, max_length=50)),
                ('description', models.TextField(null=True, verbose_name='Description', default='', validators=[django.core.validators.MaxLengthValidator(300)], blank=True, help_text='A few sentences describing the recipe (Maximum 300 characters).')),
                ('portions', models.PositiveIntegerField(null=True, blank=True, verbose_name='Portions', default=0, help_text='The average amount of people that can be fed by this recipe using the given amounts of ingredients.')),
                ('active_time', models.IntegerField(null=True, blank=True, verbose_name='Active time', default=0, help_text='The time needed to prepare this recipe where you are actually doing something.')),
                ('passive_time', models.IntegerField(null=True, blank=True, verbose_name='Passive time', default=0, help_text='The time needed to prepare this recipe where you can do something else (e.g. water is boiling)')),
                ('extra_info', models.TextField(null=True, blank=True, verbose_name='Extra info', default='', help_text='Extra info about the ingredients or needed tools (e.g. "You will need a mixer for this recipe" or "Use big potatoes")')),
                ('instructions', models.TextField(null=True, blank=True, verbose_name='Instructions', default='', help_text='Detailed instructions for preparing this recipe.')),
                ('ignore', models.BooleanField(default=False)),
                ('cuisine', models.ForeignKey(db_column='cuisine', null=True, to='recipes.Cuisine', verbose_name='Cuisine', blank=True, help_text='The type of cuisine this recipe represents.')),
                ('external_site', models.ForeignKey(to='recipes.ExternalSite', blank=True, related_name='incomplete_recipes', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='TemporaryIngredient',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('name', models.CharField(max_length=500)),
                ('ingredient', models.ForeignKey(to='ingredients.Ingredient', blank=True, null=True)),
                ('used_by', models.OneToOneField(to='recipes.UsesIngredient', on_delete=django.db.models.deletion.SET_NULL, blank=True, related_name='temporary_ingredient', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='TemporaryUnit',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('name', models.CharField(max_length=50)),
                ('unit', models.ForeignKey(to='ingredients.Unit', blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='TemporaryUsesIngredient',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('group', models.CharField(blank=True, max_length=100)),
                ('amount', models.FloatField(validators=[django.core.validators.MinValueValidator(1e-05)], default=0)),
                ('ingredient', models.ForeignKey(db_column='ingredient', to='recipes.TemporaryIngredient', related_name='used_in')),
                ('recipe', models.ForeignKey(db_column='recipe', to='recipes.IncompleteRecipe', related_name='uses')),
                ('unit', models.ForeignKey(db_column='unit', to='recipes.TemporaryUnit')),
            ],
        ),
        migrations.AddField(
            model_name='incompleterecipe',
            name='ingredients',
            field=models.ManyToManyField(through='recipes.TemporaryUsesIngredient', to='recipes.TemporaryIngredient', editable=False),
        ),
    ]
