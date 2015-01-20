# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0013_auto_20141028_1658'),
    ]

    operations = [
        migrations.AlterField(
            model_name='aggregate',
            name='extra_info',
            field=models.CharField(default=b'', max_length=100),
        ),
        migrations.AlterField(
            model_name='aggregate',
            name='name',
            field=models.PositiveSmallIntegerField(choices=[(0, b'A+'), (1, b'A'), (2, b'B'), (3, b'C'), (4, b'D'), (5, b'Mean Value'), (6, b'Standard Deviation')]),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='description',
            field=models.TextField(help_text='A few sentences describing the recipe (Maximum 300 characters).', verbose_name='Description', validators=[django.core.validators.MaxLengthValidator(300)]),
        ),
        migrations.AlterField(
            model_name='upvote',
            name='recipe',
            field=models.ForeignKey(to='recipes.Recipe'),
        ),
        migrations.AlterUniqueTogether(
            name='aggregate',
            unique_together=set([('name', 'extra_info')]),
        ),
    ]
