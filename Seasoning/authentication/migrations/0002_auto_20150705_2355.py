# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_auto_20150705_2355'),
        ('authentication', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='newemail',
            name='user',
        ),
        migrations.RemoveField(
            model_name='registrationprofile',
            name='user',
        ),
        migrations.DeleteModel(
            name='NewEmail',
        ),
        migrations.DeleteModel(
            name='RegistrationProfile',
        ),
        migrations.DeleteModel(
            name='User',
        ),
    ]
