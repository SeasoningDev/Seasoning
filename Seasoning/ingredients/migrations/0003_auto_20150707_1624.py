# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ingredients', '0002_auto_20150705_2355'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ingredient',
            options={'ordering': ('name',)},
        ),
        migrations.AlterField(
            model_name='canuseunit',
            name='ingredient',
            field=models.ForeignKey(related_name='can_use_units', to='ingredients.Ingredient'),
        ),
    ]
