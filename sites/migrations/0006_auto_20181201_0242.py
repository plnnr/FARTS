# Generated by Django 2.1.3 on 2018-12-01 02:42

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0005_auto_20181130_0458'),
    ]

    operations = [
        migrations.AddField(
            model_name='receivingsite',
            name='pmaps_object',
            field=django.contrib.postgres.fields.jsonb.JSONField(default={'data': 'null'}),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='sendingsite',
            name='pmaps_object',
            field=django.contrib.postgres.fields.jsonb.JSONField(default={'data': 'null'}),
            preserve_default=False,
        ),
    ]
