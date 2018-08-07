# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-08-06 20:29
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('gis_csdt', '0002_phonenumber'),
    ]

    operations = [
        migrations.CreateModel(
            name='DataPoint',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.DecimalField(decimal_places=15, max_digits=30)),
                ('point', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='points', to='gis_csdt.MapPoint')),
            ],
        ),
        migrations.RemoveField(
            model_name='sensor',
            name='sensor_type',
        ),
        migrations.AddField(
            model_name='sensor',
            name='accuracy',
            field=models.CharField(default=b'accuracy', max_length=100),
        ),
        migrations.AddField(
            model_name='sensor',
            name='metric',
            field=models.CharField(default=b'metric', max_length=100),
        ),
        migrations.AddField(
            model_name='sensor',
            name='model_number',
            field=models.CharField(default=b'model_number', max_length=100),
        ),
        migrations.AddField(
            model_name='sensor',
            name='supplier',
            field=models.CharField(default=b'supplier', max_length=100),
        ),
        migrations.AlterField(
            model_name='sensor',
            name='name',
            field=models.CharField(default=b'name', max_length=100, unique=True),
        ),
        migrations.AddField(
            model_name='datapoint',
            name='sensor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sensors', to='gis_csdt.Sensor'),
        ),
        migrations.AddField(
            model_name='datapoint',
            name='user',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]