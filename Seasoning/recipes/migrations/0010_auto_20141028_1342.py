# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('ingredients', '0002_auto_20140926_1221'),
        ('recipes', '0009_aggregate_extra_info'),
    ]

    operations = [
        migrations.CreateModel(
            name='IncompleteRecipe',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text='The names of the recipe.', max_length=100, null=True, verbose_name='Name', blank=True)),
                ('external', models.BooleanField(default=False)),
                ('external_url', models.CharField(max_length=1000, null=True, blank=True)),
                ('course', models.PositiveSmallIntegerField(blank=True, help_text='The type of course this recipe will provide.', null=True, verbose_name='Course', choices=[(0, 'Voorgerecht'), (1, 'Brood'), (2, 'Ontbijt'), (3, 'Dessert'), (4, 'Drank'), (5, 'Hoofdgerecht'), (6, 'Salade'), (7, 'Bijgerecht'), (8, 'Soep'), (9, 'Marinades en sauzen')])),
                ('cuisine_proposal', models.CharField(max_length=50, null=True, blank=True)),
                ('description', models.TextField(blank=True, help_text='A few sentences describing the recipe (Maximum 300 characters).', null=True, verbose_name='Description', validators=[django.core.validators.MaxLengthValidator(300)])),
                ('portions', models.PositiveIntegerField(help_text='The average amount of people that can be fed by this recipe using the given amounts of ingredients.', null=True, verbose_name='Portions', blank=True)),
                ('active_time', models.IntegerField(help_text='The time needed to prepare this recipe where you are actually doing something.', null=True, verbose_name='Active time', blank=True)),
                ('passive_time', models.IntegerField(help_text='The time needed to prepare this recipe where you can do something else (e.g. water is boiling)', null=True, verbose_name='Passive time', blank=True)),
                ('extra_info', models.TextField(default=b'', help_text='Extra info about the ingredients or needed tools (e.g. "You will need a mixer for this recipe" or "Use big potatoes")', null=True, verbose_name='Extra info', blank=True)),
                ('instructions', models.TextField(help_text='Detailed instructions for preparing this recipe.', null=True, verbose_name='Instructions', blank=True)),
                ('author', models.ForeignKey(related_name=b'incomplete_recipes', to=settings.AUTH_USER_MODEL, null=True)),
                ('cuisine', models.ForeignKey(db_column=b'cuisine', to='recipes.Cuisine', blank=True, help_text='The type of cuisine this recipe represents.', null=True, verbose_name='Cuisine')),
                ('external_site', models.ForeignKey(blank=True, to='recipes.ExternalSite', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TemporaryIngredient',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('ingredient', models.ForeignKey(blank=True, to='ingredients.Ingredient', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TemporaryUnit',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('unit', models.ForeignKey(blank=True, to='ingredients.Unit', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TemporaryUsesIngredient',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('group', models.CharField(max_length=100, blank=True)),
                ('amount', models.FloatField(default=0, validators=[django.core.validators.MinValueValidator(1e-05)])),
                ('ingredient', models.ForeignKey(related_name=b'used_in', db_column=b'ingredient', to='recipes.TemporaryIngredient')),
                ('recipe', models.ForeignKey(related_name=b'uses', db_column=b'recipe', to='recipes.IncompleteRecipe')),
                ('unit', models.ForeignKey(to='recipes.TemporaryUnit', db_column=b'unit')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Upvote',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time', models.DateTimeField(auto_now_add=True)),
                ('recipe', models.ForeignKey(related_name=b'votes', to='recipes.Recipe')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='vote',
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name='vote',
            name='recipe',
        ),
        migrations.RemoveField(
            model_name='vote',
            name='user',
        ),
        migrations.DeleteModel(
            name='Vote',
        ),
        migrations.AlterUniqueTogether(
            name='upvote',
            unique_together=set([('recipe', 'user')]),
        ),
        migrations.AddField(
            model_name='incompleterecipe',
            name='ingredients',
            field=models.ManyToManyField(to='recipes.TemporaryIngredient', editable=False, through='recipes.TemporaryUsesIngredient'),
            preserve_default=True,
        ),
        migrations.RemoveField(
            model_name='recipe',
            name='no_of_ratings',
        ),
        migrations.RemoveField(
            model_name='recipe',
            name='rating',
        ),
    ]
