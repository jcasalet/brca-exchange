# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2019-06-10 14:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0041_paper_crawl_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='report',
            name='Condition_DB_ID_ClinVar',
            field=models.TextField(default=b'-'),
        ),
        migrations.AddField(
            model_name='report',
            name='Condition_Type_ClinVar',
            field=models.TextField(default=b'-'),
        ),
        migrations.AddField(
            model_name='report',
            name='Condition_Value_ClinVar',
            field=models.TextField(default=b'-'),
        ),
    ]