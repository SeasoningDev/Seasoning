# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ingredients', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='canuseunit',
            old_name='conversion_factor',
            new_name='conversion_ratio',
        ),
        migrations.RemoveField(
            model_name='availableincountry',
            name='footprint',
        ),
        migrations.RemoveField(
            model_name='availableinsea',
            name='footprint',
        ),
        migrations.RemoveField(
            model_name='canuseunit',
            name='is_primary_unit',
        ),
        migrations.AlterField(
            model_name='availableincountry',
            name='ingredient',
            field=models.ForeignKey(to='ingredients.Ingredient', related_name='available_in_country'),
        ),
        migrations.AlterField(
            model_name='availableincountry',
            name='location',
            field=models.ForeignKey(to='ingredients.Country'),
        ),
        migrations.AlterField(
            model_name='availableincountry',
            name='transport_method',
            field=models.ForeignKey(to='ingredients.TransportMethod'),
        ),
        migrations.AlterField(
            model_name='availableinsea',
            name='ingredient',
            field=models.ForeignKey(to='ingredients.Ingredient', related_name='available_in_sea'),
        ),
        migrations.AlterField(
            model_name='availableinsea',
            name='location',
            field=models.ForeignKey(to='ingredients.Sea'),
        ),
        migrations.AlterField(
            model_name='availableinsea',
            name='transport_method',
            field=models.ForeignKey(to='ingredients.TransportMethod'),
        ),
        migrations.AlterField(
            model_name='canuseunit',
            name='ingredient',
            field=models.ForeignKey(to='ingredients.Ingredient'),
        ),
        migrations.AlterField(
            model_name='canuseunit',
            name='unit',
            field=models.ForeignKey(to='ingredients.Unit', related_name='useable_by'),
        ),
        migrations.AlterField(
            model_name='synonym',
            name='ingredient',
            field=models.ForeignKey(blank=True, related_name='synonyms', null=True, to='ingredients.Ingredient'),
        ),
        migrations.AlterModelTable(
            name='availableincountry',
            table=None,
        ),
        migrations.AlterModelTable(
            name='availableinsea',
            table=None,
        ),
        migrations.AlterModelTable(
            name='canuseunit',
            table=None,
        ),
        migrations.AlterModelTable(
            name='country',
            table=None,
        ),
        migrations.AlterModelTable(
            name='ingredient',
            table=None,
        ),
        migrations.AlterModelTable(
            name='sea',
            table=None,
        ),
        migrations.AlterModelTable(
            name='synonym',
            table=None,
        ),
        migrations.AlterModelTable(
            name='transportmethod',
            table=None,
        ),
        migrations.AlterModelTable(
            name='unit',
            table=None,
        ),
    ]
