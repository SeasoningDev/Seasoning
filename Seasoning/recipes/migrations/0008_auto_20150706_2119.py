# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0007_auto_20150706_2119'),
    ]

    operations = [
        migrations.CreateModel(
            name='ScrapedRecipe',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='The names of the recipe.', verbose_name='Name', null=True, max_length=100, blank=True, default='')),
                ('external', models.BooleanField(default=False)),
                ('external_url', models.CharField(max_length=1000, blank=True, null=True)),
                ('course', models.PositiveSmallIntegerField(verbose_name='Course', help_text='The type of course this recipe will provide.', choices=[(0, 'Voorgerecht'), (1, 'Brood'), (2, 'Ontbijt'), (3, 'Dessert'), (4, 'Drank'), (5, 'Hoofdgerecht'), (6, 'Salade'), (7, 'Bijgerecht'), (8, 'Soep'), (9, 'Marinades en sauzen')], blank=True, null=True)),
                ('cuisine_proposal', models.CharField(max_length=50, blank=True, null=True)),
                ('description', models.TextField(validators=[django.core.validators.MaxLengthValidator(300)], help_text='A few sentences describing the recipe (Maximum 300 characters).', verbose_name='Description', null=True, blank=True, default='')),
                ('portions', models.PositiveIntegerField(verbose_name='Portions', help_text='The average amount of people that can be fed by this recipe using the given amounts of ingredients.', default=0, blank=True, null=True)),
                ('active_time', models.IntegerField(verbose_name='Active time', help_text='The time needed to prepare this recipe where you are actually doing something.', default=0, blank=True, null=True)),
                ('passive_time', models.IntegerField(verbose_name='Passive time', help_text='The time needed to prepare this recipe where you can do something else (e.g. water is boiling)', default=0, blank=True, null=True)),
                ('extra_info', models.TextField(verbose_name='Extra info', help_text='Extra info about the ingredients or needed tools (e.g. "You will need a mixer for this recipe" or "Use big potatoes")', default='', blank=True, null=True)),
                ('instructions', models.TextField(verbose_name='Instructions', help_text='Detailed instructions for preparing this recipe.', default='', blank=True, null=True)),
                ('ignore', models.BooleanField(default=False)),
                ('cuisine', models.ForeignKey(help_text='The type of cuisine this recipe represents.', to='recipes.Cuisine', db_column='cuisine', verbose_name='Cuisine', null=True, blank=True)),
                ('external_site', models.ForeignKey(related_name='incomplete_recipes', to='recipes.ExternalSite', null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='ScrapedUsesIngredient',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('group', models.CharField(max_length=100, blank=True)),
                ('amount', models.FloatField(validators=[django.core.validators.MinValueValidator(1e-05)], default=0)),
                ('ingredient', models.ForeignKey(related_name='used_in', to='recipes.ScrapedIngredient', db_column='ingredient')),
                ('recipe', models.ForeignKey(related_name='uses', to='recipes.ScrapedRecipe', db_column='recipe')),
                ('unit', models.ForeignKey(to='recipes.ScrapedUnit', db_column='unit')),
            ],
        ),
        migrations.RemoveField(
            model_name='incompleterecipe',
            name='cuisine',
        ),
        migrations.RemoveField(
            model_name='incompleterecipe',
            name='external_site',
        ),
        migrations.RemoveField(
            model_name='incompleterecipe',
            name='ingredients',
        ),
        migrations.RemoveField(
            model_name='temporaryusesingredient',
            name='ingredient',
        ),
        migrations.RemoveField(
            model_name='temporaryusesingredient',
            name='recipe',
        ),
        migrations.RemoveField(
            model_name='temporaryusesingredient',
            name='unit',
        ),
        migrations.DeleteModel(
            name='IncompleteRecipe',
        ),
        migrations.DeleteModel(
            name='TemporaryUsesIngredient',
        ),
        migrations.AddField(
            model_name='scrapedrecipe',
            name='ingredients',
            field=models.ManyToManyField(editable=False, to='recipes.ScrapedIngredient', through='recipes.ScrapedUsesIngredient'),
        ),
    ]
