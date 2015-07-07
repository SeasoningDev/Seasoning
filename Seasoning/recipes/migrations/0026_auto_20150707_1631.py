# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0025_auto_20150707_1630'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usesingredient',
            name='recipe',
            field=models.ForeignKey(to='recipes.Recipe', related_name='uses_ingredients'),
        ),
    ]
