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
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('line', models.PositiveIntegerField()),
                ('time', models.DateTimeField()),
                ('pid', models.PositiveIntegerField()),
                ('wid', models.PositiveSmallIntegerField()),
                ('ip', models.IPAddressField()),
                ('user_agent', models.CharField(max_length=100)),
                ('method', models.CharField(max_length=10)),
                ('protocol', models.CharField(max_length=20)),
                ('uri', models.CharField(max_length=100)),
                ('status', models.PositiveSmallIntegerField()),
                ('referer', models.CharField(max_length=200)),
                ('msec', models.PositiveIntegerField()),
                ('size', models.PositiveIntegerField()),
                ('vsz', models.PositiveIntegerField()),
                ('rss', models.PositiveIntegerField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
