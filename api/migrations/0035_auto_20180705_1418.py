# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-07-05 14:18
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0034_auto_20180703_2216'),
    ]

    operations = [
        migrations.AlterField(
            model_name='events',
            name='date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
