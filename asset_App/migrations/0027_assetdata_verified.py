# Generated by Django 5.0.6 on 2024-10-25 08:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('asset_App', '0026_assetdata_sold_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='assetdata',
            name='verified',
            field=models.BooleanField(default=False),
        ),
    ]
