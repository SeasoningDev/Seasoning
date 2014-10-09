# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ingredients', '0002_auto_20140926_1221'),
        ('recipes', '0005_recipe_no_of_ratings'),
    ]

    operations = [
        migrations.CreateModel(
            name='UnknownUsesIngredient',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('amount', models.FloatField()),
                ('unknownunit_name', models.CharField(max_length=20)),
                ('cantuseunit', models.BooleanField(default=False)),
                ('ingredient', models.ForeignKey(to='recipes.UnknownIngredient')),
                ('recipe', models.ForeignKey(to='recipes.Recipe')),
                ('unit', models.ForeignKey(blank=True, to='ingredients.Unit', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='external_site',
            field=models.ForeignKey(related_name=b'recipes', blank=True, to='recipes.ExternalSite', null=True),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='rating',
            field=models.FloatField(default=None, null=True, editable=False, blank=True),
        ),
        migrations.AlterField(
            model_name='unknowningredient',
            name='real_ingredient',
            field=models.ForeignKey(blank=True, to='ingredients.Ingredient', null=True),
        ),
    ]
