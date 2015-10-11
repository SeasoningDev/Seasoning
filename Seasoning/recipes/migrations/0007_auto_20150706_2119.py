# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ingredients', '0002_auto_20150705_2355'),
        ('recipes', '0006_auto_20150706_2118'),
    ]

    operations = [
        migrations.CreateModel(
            name='ScrapedUnit',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('unit', models.ForeignKey(blank=True, to='ingredients.Unit', null=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='temporaryunit',
            name='unit',
        ),
        migrations.AlterField(
            model_name='temporaryusesingredient',
            name='unit',
            field=models.ForeignKey(to='recipes.ScrapedUnit', db_column='unit'),
        ),
        migrations.DeleteModel(
            name='TemporaryUnit',
        ),
    ]
