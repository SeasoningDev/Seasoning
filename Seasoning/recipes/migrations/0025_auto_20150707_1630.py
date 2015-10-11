# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0024_auto_20150707_1630'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='instructions',
            field=models.TextField(verbose_name='Instructions', null=True, help_text='Detailed instructions for preparing this recipe.', blank=True),
        ),
    ]
