# Generated by Django 5.0.6 on 2024-10-25 06:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('asset_App', '0025_remove_assetdata_is_auto_generated_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='assetdata',
            name='sold_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
