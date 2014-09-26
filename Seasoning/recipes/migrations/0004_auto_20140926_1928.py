# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0003_auto_20140926_1307'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipe',
            name='complete_information',
            field=models.BooleanField(default=True, editable=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='recipe',
            name='endangered',
            field=models.BooleanField(default=False, editable=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='recipe',
            name='footprint',
            field=models.FloatField(default=0, editable=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='recipe',
            name='inseason',
            field=models.BooleanField(default=False, editable=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='recipe',
            name='rating',
            field=models.FloatField(null=True, editable=False, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='recipe',
            name='veganism',
            field=models.PositiveSmallIntegerField(default=2, editable=False, choices=[(2, 'Veganistisch'), (1, 'Vegetarisch'), (0, 'Niet-Vegetarisch')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='usesingredient',
            name='ingredient',
            field=models.ForeignKey(related_name=b'used_in', db_column=b'ingredient', to='ingredients.Ingredient'),
        ),
        migrations.AlterField(
            model_name='vote',
            name='time_added',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='vote',
            name='time_changed',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
