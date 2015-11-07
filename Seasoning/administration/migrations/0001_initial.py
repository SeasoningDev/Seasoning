# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='RequestLog',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('time', models.DateTimeField()),
                ('minute', models.CharField(max_length=12, editable=False)),
                ('pid', models.PositiveIntegerField()),
                ('wid', models.PositiveSmallIntegerField()),
                ('ip', models.GenericIPAddressField()),
                ('user_agent', models.CharField(max_length=300)),
                ('method', models.CharField(max_length=10)),
                ('protocol', models.CharField(max_length=20)),
                ('uri', models.CharField(max_length=300)),
                ('uri_params', models.TextField()),
                ('status', models.PositiveSmallIntegerField()),
                ('referer', models.CharField(max_length=300)),
                ('referer_params', models.TextField()),
                ('msec', models.PositiveIntegerField()),
                ('size', models.PositiveIntegerField()),
                ('vsz', models.PositiveIntegerField()),
                ('rss', models.PositiveIntegerField()),
            ],
        ),
    ]
