# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-07-05 20:53
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0037_auto_20180705_2024'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='launch',
            name='rocket',
        ),
        migrations.DeleteModel(
            name='Rocket',
        ),
    ]
