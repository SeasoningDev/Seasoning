# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import authentication.models
import django.core.validators
import imagekit.models.fields
import re
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='RegistrationProfile',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('activation_key', models.CharField(max_length=40, verbose_name='activation key')),
            ],
            options={
                'verbose_name': 'registration profile',
                'verbose_name_plural': 'registration profiles',
                'db_table': 'registrationprofile',
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('email', models.EmailField(max_length=255, verbose_name='Email', db_index=True, error_messages={'unique': 'Er bestaat al een gebruiker met dit e-mailadres. Vermoed je dat iemand tracht misbruik te maken van jouw e-mailadres, neem dan contact met ons op via <a href="/contact/form/abuse/">dit formulier</a>.'}, unique=True)),
                ('givenname', models.CharField(help_text='30 characters or fewer, only letters allowed. Your name will be used to identify you on Seasoning.', validators=[django.core.validators.RegexValidator(re.compile('[a-zA-Z -]{2,}', 32), 'Enter a valid Given Name.', 'invalid')], verbose_name='Givenname', max_length=30)),
                ('surname', models.CharField(help_text='50 characters or fewer, only letters allowed Your name will be used to identify you on Seasoning.', validators=[django.core.validators.RegexValidator(re.compile('[a-zA-Z -]{2,}', 32), 'Enter a valid Surname.', 'invalid')], verbose_name='Surname', max_length=50)),
                ('name_changed', models.BooleanField(editable=False, default=False)),
                ('password', models.CharField(max_length=128, verbose_name='Password', null=True)),
                ('avatar', imagekit.models.fields.ProcessedImageField()),
                ('date_of_birth', models.DateField()),
                ('is_active', models.BooleanField(default=False)),
                ('is_staff', models.BooleanField(default=False)),
                ('is_superuser', models.BooleanField(default=False)),
                ('date_joined', models.DateTimeField(verbose_name='date joined', default=django.utils.timezone.now)),
                ('last_login', models.DateTimeField(verbose_name='last login', default=django.utils.timezone.now)),
                ('facebook_id', models.CharField(max_length=30, editable=False, null=True)),
                ('twitter_id', models.CharField(max_length=30, editable=False, null=True)),
                ('google_id', models.CharField(max_length=30, editable=False, null=True)),
                ('openid_id', models.CharField(max_length=30, editable=False, null=True)),
            ],
            options={
                'db_table': 'user',
            },
        ),
        migrations.CreateModel(
            name='NewEmail',
            fields=[
                ('user', models.ForeignKey(to='authentication.User', serialize=False, primary_key=True, related_name='new_emails')),
                ('activation_key', models.CharField(max_length=40, verbose_name='activation key', unique=True)),
                ('email', models.EmailField(max_length=255, unique=True)),
            ],
            options={
                'db_table': 'newemail',
            },
        ),
        migrations.AddField(
            model_name='registrationprofile',
            name='user',
            field=models.OneToOneField(to='authentication.User'),
        ),
    ]
