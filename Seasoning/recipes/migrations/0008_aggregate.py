# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0007_recipeimage'),
    ]

    operations = [
        migrations.CreateModel(
            name='Aggregate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.PositiveSmallIntegerField(unique=True, choices=[(0, b'A+'), (1, b'A'), (2, b'B'), (3, b'C'), (4, b'D')])),
                ('value', models.FloatField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
