# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0034_auto_20150709_2128'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='name',
            field=models.CharField(verbose_name='Name', help_text='The names of the recipe.', max_length=300),
        ),
        migrations.AlterField(
            model_name='scrapedrecipe',
            name='name',
            field=models.CharField(verbose_name='Name', null=True, max_length=300, help_text='The names of the recipe.', default='', blank=True),
        ),
    ]
