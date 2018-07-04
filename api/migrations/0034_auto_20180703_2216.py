# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-07-04 02:16
from __future__ import unicode_literals

import api.models
import custom_storages
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0033_auto_20180601_1647'),
    ]

    operations = [
        migrations.AlterField(
            model_name='agency',
            name='logo_url',
            field=models.FileField(blank=True, default=None, null=True, storage=custom_storages.LogoStorage(), upload_to=api.models.logo_path),
        ),
        migrations.AlterField(
            model_name='agency',
            name='nation_url',
            field=models.FileField(blank=True, default=None, null=True, storage=custom_storages.AgencyNationStorage(), upload_to=api.models.nation_path),
        ),
    ]
