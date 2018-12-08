# -*- coding: utf-8 -*-
# Generated by Django 1.11.17 on 2018-12-04 22:15
from __future__ import unicode_literals

import uuid

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('api', '0021_launch_new_id_part2'),
    ]

    operations = [
        migrations.AlterField(
            model_name='launch',
            name='new_id',
            field=models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='launch',
            name='launch_library_id',
            field=models.IntegerField(),
        ),
    ]
