# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2018-08-15 02:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0032_additional_clinvar_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='report',
            name='Synonyms_ClinVar',
            field=models.TextField(default=b'-'),
        ),
    ]
