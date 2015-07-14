# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import markitup.fields


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0037_auto_20150713_2149'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipe',
            name='_instructions_rendered',
            field=models.TextField(blank=True, editable=False),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='instructions',
            field=markitup.fields.MarkupField(help_text='Detailed instructions for preparing this recipe.', no_rendered_field=True, verbose_name='Instructions', blank=True, null=True),
        ),
    ]
