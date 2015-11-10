# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import imagekit.models.fields
import recipes.models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='unknowningredient',
            name='for_recipe',
        ),
        migrations.RemoveField(
            model_name='unknowningredient',
            name='real_ingredient',
        ),
        migrations.AlterUniqueTogether(
            name='vote',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='vote',
            name='recipe',
        ),
        migrations.RemoveField(
            model_name='recipe',
            name='accepted',
        ),
        migrations.RemoveField(
            model_name='recipe',
            name='endangered',
        ),
        migrations.RemoveField(
            model_name='recipe',
            name='footprint',
        ),
        migrations.RemoveField(
            model_name='recipe',
            name='inseason',
        ),
        migrations.RemoveField(
            model_name='recipe',
            name='number_of_votes',
        ),
        migrations.RemoveField(
            model_name='recipe',
            name='rating',
        ),
        migrations.RemoveField(
            model_name='recipe',
            name='time_added',
        ),
        migrations.RemoveField(
            model_name='recipe',
            name='veganism',
        ),
        migrations.RemoveField(
            model_name='usesingredient',
            name='footprint',
        ),
        migrations.AlterField(
            model_name='externalsite',
            name='name',
            field=models.CharField(verbose_name='Name', help_text='The name of the external website.', max_length=200),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='cuisine',
            field=models.ForeignKey(blank=True, help_text='The type of cuisine this recipe represents.', null=True, verbose_name='Cuisine', to='recipes.Cuisine'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='image',
            field=imagekit.models.fields.ProcessedImageField(upload_to=recipes.models.get_image_filename, help_text='An image of this recipe. Please do not use copyrighted images, these will be removed as quick as possible.'),
        ),
        migrations.AlterField(
            model_name='usesingredient',
            name='ingredient',
            field=models.ForeignKey(to='ingredients.Ingredient'),
        ),
        migrations.AlterField(
            model_name='usesingredient',
            name='recipe',
            field=models.ForeignKey(to='recipes.Recipe', related_name='uses_ingredient'),
        ),
        migrations.AlterField(
            model_name='usesingredient',
            name='unit',
            field=models.ForeignKey(to='ingredients.Unit'),
        ),
        migrations.AlterModelTable(
            name='cuisine',
            table=None,
        ),
        migrations.AlterModelTable(
            name='recipe',
            table=None,
        ),
        migrations.AlterModelTable(
            name='usesingredient',
            table=None,
        ),
        migrations.DeleteModel(
            name='UnknownIngredient',
        ),
        migrations.DeleteModel(
            name='Vote',
        ),
    ]
