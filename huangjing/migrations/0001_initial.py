# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('order', models.CharField(max_length=255)),
            ],
            options={
                'db_table': 'group',
            },
        ),
        migrations.CreateModel(
            name='Holiday',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('year', models.CharField(max_length=255)),
                ('data', models.CharField(max_length=255)),
            ],
            options={
                'db_table': 'holiday',
            },
        ),
        migrations.CreateModel(
            name='Scheduled',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('group_id', models.CharField(max_length=255)),
                ('user_id', models.CharField(max_length=255)),
                ('day', models.IntegerField(max_length=255)),
                ('month', models.CharField(max_length=255)),
                ('week', models.CharField(max_length=255)),
                ('year', models.IntegerField(max_length=255)),
            ],
            options={
                'db_table': 'Scheduled',
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('username', models.CharField(max_length=255)),
                ('loginname', models.CharField(max_length=255)),
                ('mobile', models.CharField(max_length=255)),
                ('email', models.CharField(max_length=255)),
                ('role', models.IntegerField()),
            ],
            options={
                'db_table': 'user',
            },
        ),
    ]
