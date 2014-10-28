# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0012_auto_20141028_1522'),
    ]

    operations = [
        migrations.AlterField(
            model_name='temporaryingredient',
            name='name',
            field=models.CharField(max_length=500),
        ),
    ]
