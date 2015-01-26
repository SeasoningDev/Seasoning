# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0018_auto_20150123_1608'),
    ]

    operations = [
        migrations.AddField(
            model_name='temporaryingredient',
            name='used_by',
            field=models.OneToOneField(related_name=b'temporary_ingredient', null=True, blank=True, to='recipes.UsesIngredient'),
            preserve_default=True,
        ),
    ]
