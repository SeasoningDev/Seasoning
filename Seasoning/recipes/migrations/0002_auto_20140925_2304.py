# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


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
        migrations.RemoveField(
            model_name='unknowningredient',
            name='requested_by',
        ),
        migrations.DeleteModel(
            name='UnknownIngredient',
        ),
        migrations.AddField(
            model_name='recipe',
            name='complete_information',
            field=models.BooleanField(default=True, editable=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='recipe',
            name='visible',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
    ]
