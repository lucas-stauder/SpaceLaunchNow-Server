# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-10-12 00:30
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0006_auto_20171011_1828'),
    ]

    operations = [
        migrations.CreateModel(
            name='VidURLs',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vid_url', models.URLField(unique=True)),
            ],
        ),
        migrations.AddField(
            model_name='launch',
            name='mission_description',
            field=models.CharField(blank=True, default=b'', max_length=2048),
        ),
        migrations.AddField(
            model_name='launch',
            name='mission_type',
            field=models.CharField(blank=True, default=b'', max_length=255),
        ),
        migrations.AddField(
            model_name='launch',
            name='net',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='launch',
            name='window_end',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='launch',
            name='window_start',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='vidurls',
            name='launch',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bot.Launch'),
        ),
    ]
