# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-04-27 16:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qcapp', '0005_userdata'),
    ]

    operations = [
        migrations.AddField(
            model_name='userdata',
            name='checkut_out',
            field=models.CharField(default='', max_length=2500),
            preserve_default=False,
        ),
    ]
