# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2019-02-19 17:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0037_paper_variantpaper'),
    ]

    operations = [
        migrations.AddField(
            model_name='report',
            name='BX_ID_Findlay_BRCA1_Ring_Function_Scores',
            field=models.TextField(default=b''),
        ),
        migrations.AddField(
            model_name='report',
            name='Functional_Enrichment_Score_Findlay_BRCA1_Ring_Function_Scores',
            field=models.TextField(default=b'-'),
        ),
        migrations.AddField(
            model_name='report',
            name='HGVS_Nucleotide_Findlay_BRCA1_Ring_Function_Scores',
            field=models.TextField(default=b'-'),
        ),
        migrations.AddField(
            model_name='report',
            name='Log_RNA_Depletion_Findlay_BRCA1_Ring_Function_Scores',
            field=models.TextField(default=b'-'),
        ),
        migrations.AddField(
            model_name='variant',
            name='BX_ID_Findlay_BRCA1_Ring_Function_Scores',
            field=models.TextField(default=b''),
        ),
        migrations.AddField(
            model_name='variant',
            name='Functional_Enrichment_Score_Findlay_BRCA1_Ring_Function_Scores',
            field=models.TextField(default=b'-'),
        ),
        migrations.AddField(
            model_name='variant',
            name='HGVS_Nucleotide_Findlay_BRCA1_Ring_Function_Scores',
            field=models.TextField(default=b'-'),
        ),
        migrations.AddField(
            model_name='variant',
            name='Log_RNA_Depletion_Findlay_BRCA1_Ring_Function_Scores',
            field=models.TextField(default=b'-'),
        ),
        migrations.AddField(
            model_name='variant',
            name='Variant_in_Findlay_BRCA1_Ring_Function_Scores',
            field=models.BooleanField(default=False),
        ),
        migrations.RunSQL(
            """
            DROP MATERIALIZED VIEW IF EXISTS currentvariant;
            CREATE MATERIALIZED VIEW currentvariant AS (
                SELECT * FROM "variant" WHERE (
                    "id" IN ( SELECT DISTINCT ON ("Genomic_Coordinate_hg38") "id" FROM "variant" ORDER BY "Genomic_Coordinate_hg38" ASC, "Data_Release_id" DESC )
                )
            );
            """
        ),
    ]
