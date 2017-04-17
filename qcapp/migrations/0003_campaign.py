# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-04-16 15:32
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('qcapp', '0002_auto_20170416_1031'),
    ]

    operations = [
        migrations.CreateModel(
            name='Campaign',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('datetime_created', models.DateTimeField(default=django.utils.timezone.now)),
                ('deadline', models.DateTimeField(null=True)),
                ('contact', models.CharField(max_length=200, null=True)),
                ('volunteer_ids', models.CharField(max_length=2500, null=True)),
                ('code', models.CharField(max_length=8, null=True)),
                ('owner_id', models.IntegerField(null=True)),
                ('cvass_data', models.TextField(default='some json data')),
                ('targetted_years', models.CharField(default='any', max_length=4)),
            ],
        ),
    ]
