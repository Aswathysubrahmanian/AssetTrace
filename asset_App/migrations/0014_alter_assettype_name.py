# Generated by Django 5.0.6 on 2024-10-17 08:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('asset_App', '0013_assetdata_is_sold'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assettype',
            name='name',
            field=models.CharField(max_length=200, unique=True),
        ),
    ]
