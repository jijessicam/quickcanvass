# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-05-01 01:27
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('qcapp', '0008_auto_20170427_1130'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='campaign',
            name='deadline',
        ),
    ]
