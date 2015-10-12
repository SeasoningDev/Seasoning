# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators
import imagekit.models.fields
import recipes.models
import django.db.models.deletion
import markitup.fields


class Migration(migrations.Migration):

    dependencies = [
        ('ingredients', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cuisine',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('name', models.CharField(max_length=50)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='ExternalSite',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('name', models.CharField(help_text='The name of the external website.', max_length=200, verbose_name='Name')),
                ('url', models.CharField(help_text='The home url of the external website', max_length=200, verbose_name='URL')),
            ],
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('name', models.CharField(help_text='The names of the recipe.', max_length=300, verbose_name='Name')),
                ('external', models.BooleanField(default=False)),
                ('external_url', models.CharField(null=True, max_length=1000, blank=True)),
                ('course', models.PositiveSmallIntegerField(help_text='The type of course this recipe will provide.', choices=[(0, 'Voorgerecht'), (1, 'Brood'), (2, 'Ontbijt'), (3, 'Dessert'), (4, 'Drank'), (5, 'Hoofdgerecht'), (6, 'Salade'), (7, 'Bijgerecht'), (8, 'Soep'), (9, 'Marinades en sauzen')], verbose_name='Course')),
                ('description', models.TextField(null=True, help_text='A few sentences describing the recipe (Maximum 140 characters).', blank=True, verbose_name='Description', validators=[django.core.validators.MaxLengthValidator(140)])),
                ('portions', models.PositiveIntegerField(help_text='The average amount of people that can be fed by this recipe using the given amounts of ingredients.', verbose_name='Portions')),
                ('active_time', models.IntegerField(null=True, help_text='The time needed to prepare this recipe where you are actually doing something.', blank=True, verbose_name='Active time')),
                ('passive_time', models.IntegerField(null=True, help_text='The time needed to prepare this recipe where you can do something else (e.g. water is boiling)', blank=True, verbose_name='Passive time')),
                ('extra_info', models.TextField(default='', help_text='Extra info about the ingredients or needed tools (e.g. "You will need a mixer for this recipe" or "Use big potatoes")', blank=True, verbose_name='Extra info')),
                ('instructions', markitup.fields.MarkupField(null=True, help_text='Detailed instructions for preparing this recipe.', blank=True, verbose_name='Instructions', no_rendered_field=True)),
                ('image', imagekit.models.fields.ProcessedImageField(help_text='An image of this recipe. Please do not use copyrighted images, these will be removed as quick as possible.', upload_to=recipes.models.get_image_filename)),
                ('time_added', models.DateTimeField(auto_now_add=True)),
                ('last_update_time', models.DateTimeField(auto_now=True)),
                ('cached_veganism', models.PositiveSmallIntegerField(null=True, blank=True, choices=[(2, 'Veganistisch'), (1, 'Vegetarisch'), (0, 'Niet-Vegetarisch')])),
                ('cached_footprint', models.FloatField(null=True, blank=True)),
                ('cached_in_season', models.BooleanField(default=False)),
                ('cached_has_endangered_ingredients', models.BooleanField(default=False)),
                ('_instructions_rendered', models.TextField(blank=True, editable=False)),
                ('cuisine', models.ForeignKey(null=True, blank=True, verbose_name='Cuisine', help_text='The type of cuisine this recipe represents.', to='recipes.Cuisine')),
                ('external_site', models.ForeignKey(null=True, blank=True, to='recipes.ExternalSite')),
            ],
        ),
        migrations.CreateModel(
            name='RecipeDistribution',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('group', models.PositiveSmallIntegerField(choices=[(100, 'All Recipes'), (0, 'Voorgerecht'), (1, 'Brood'), (2, 'Ontbijt'), (3, 'Dessert'), (4, 'Drank'), (5, 'Hoofdgerecht'), (6, 'Salade'), (7, 'Bijgerecht'), (8, 'Soep'), (9, 'Marinades en sauzen')])),
                ('parameter', models.PositiveSmallIntegerField(choices=[(0, 'Mean'), (1, 'Standard Deviation')])),
                ('parameter_value', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='ScrapedRecipe',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('name', models.CharField(null=True, blank=True, verbose_name='Name', help_text='The name of the recipe.', max_length=300, default='')),
                ('scraped_name', models.CharField(null=True, max_length=300, blank=True, verbose_name='Scraped Name')),
                ('external', models.BooleanField(default=False)),
                ('external_url', models.CharField(null=True, max_length=1000, blank=True)),
                ('course', models.PositiveSmallIntegerField(null=True, help_text='The type of course this recipe will provide.', blank=True, choices=[(0, 'Voorgerecht'), (1, 'Brood'), (2, 'Ontbijt'), (3, 'Dessert'), (4, 'Drank'), (5, 'Hoofdgerecht'), (6, 'Salade'), (7, 'Bijgerecht'), (8, 'Soep'), (9, 'Marinades en sauzen')], verbose_name='Course')),
                ('course_proposal', models.CharField(null=True, max_length=100, blank=True)),
                ('cuisine_proposal', models.CharField(null=True, max_length=50, blank=True)),
                ('description', models.TextField(null=True, blank=True, verbose_name='Description', help_text='A few sentences describing the recipe (Maximum 300 characters).', validators=[django.core.validators.MaxLengthValidator(300)], default='')),
                ('portions', models.PositiveIntegerField(null=True, help_text='The average amount of people that can be fed by this recipe using the given amounts of ingredients.', blank=True, verbose_name='Portions', default=0)),
                ('active_time', models.IntegerField(null=True, help_text='The time needed to prepare this recipe where you are actually doing something.', blank=True, verbose_name='Active time', default=0)),
                ('passive_time', models.IntegerField(null=True, help_text='The time needed to prepare this recipe where you can do something else (e.g. water is boiling)', blank=True, verbose_name='Passive time', default=0)),
                ('extra_info', models.TextField(null=True, help_text='Extra info about the ingredients or needed tools (e.g. "You will need a mixer for this recipe" or "Use big potatoes")', blank=True, verbose_name='Extra info', default='')),
                ('instructions', models.TextField(null=True, help_text='Detailed instructions for preparing this recipe.', blank=True, verbose_name='Instructions', default='')),
                ('ignore', models.BooleanField(default=False)),
                ('image_url', models.URLField(null=True, max_length=400, blank=True)),
                ('first_scrape_date', models.DateField(auto_now_add=True)),
                ('last_update_date', models.DateField(auto_now=True)),
                ('deleted', models.BooleanField(default=False)),
                ('cuisine', models.ForeignKey(null=True, blank=True, verbose_name='Cuisine', db_column='cuisine', help_text='The type of cuisine this recipe represents.', to='recipes.Cuisine')),
                ('external_site', models.ForeignKey(null=True, blank=True, related_name='incomplete_recipes', to='recipes.ExternalSite')),
                ('recipe', models.ForeignKey(null=True, blank=True, on_delete=django.db.models.deletion.SET_NULL, to='recipes.Recipe')),
            ],
        ),
        migrations.CreateModel(
            name='ScrapedUsesIngredient',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('ingredient_proposal', models.CharField(max_length=500)),
                ('group', models.CharField(null=True, max_length=500, blank=True)),
                ('amount', models.FloatField(null=True, blank=True, validators=[django.core.validators.MinValueValidator(1e-05)], default=0)),
                ('amount_proposal', models.CharField(null=True, max_length=20, blank=True)),
                ('unit_proposal', models.CharField(null=True, max_length=50, blank=True)),
                ('ingredient', models.ForeignKey(null=True, blank=True, to='ingredients.Ingredient')),
                ('recipe', models.ForeignKey(related_name='ingredients', to='recipes.ScrapedRecipe')),
                ('unit', models.ForeignKey(null=True, blank=True, to='ingredients.Unit')),
            ],
        ),
        migrations.CreateModel(
            name='UsesIngredient',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('group', models.CharField(null=True, max_length=100, blank=True)),
                ('amount', models.FloatField(default=0, validators=[django.core.validators.MinValueValidator(1e-05)])),
                ('ingredient', models.ForeignKey(to='ingredients.Ingredient')),
                ('recipe', models.ForeignKey(related_name='uses_ingredients', to='recipes.Recipe')),
                ('unit', models.ForeignKey(to='ingredients.Unit')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='recipedistribution',
            unique_together=set([('group', 'parameter')]),
        ),
        migrations.AddField(
            model_name='recipe',
            name='ingredients',
            field=models.ManyToManyField(editable=False, to='ingredients.Ingredient', through='recipes.UsesIngredient'),
        ),
        migrations.AlterUniqueTogether(
            name='scrapedrecipe',
            unique_together=set([('scraped_name', 'external_site')]),
        ),
    ]
