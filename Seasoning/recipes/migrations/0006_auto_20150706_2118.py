# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ingredients', '0002_auto_20150705_2355'),
        ('recipes', '0005_auto_20150706_1652'),
    ]

    operations = [
        migrations.CreateModel(
            name='ScrapedIngredient',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(max_length=500)),
                ('ingredient', models.ForeignKey(null=True, blank=True, to='ingredients.Ingredient')),
                ('used_by', models.OneToOneField(related_name='temporary_ingredient', on_delete=django.db.models.deletion.SET_NULL, null=True, blank=True, to='recipes.UsesIngredient')),
            ],
        ),
        migrations.RemoveField(
            model_name='temporaryingredient',
            name='ingredient',
        ),
        migrations.RemoveField(
            model_name='temporaryingredient',
            name='used_by',
        ),
        migrations.AlterField(
            model_name='incompleterecipe',
            name='ingredients',
            field=models.ManyToManyField(editable=False, to='recipes.ScrapedIngredient', through='recipes.TemporaryUsesIngredient'),
        ),
        migrations.AlterField(
            model_name='temporaryusesingredient',
            name='ingredient',
            field=models.ForeignKey(related_name='used_in', db_column='ingredient', to='recipes.ScrapedIngredient'),
        ),
        migrations.DeleteModel(
            name='TemporaryIngredient',
        ),
    ]
