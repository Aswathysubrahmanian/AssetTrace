# Generated by Django 5.0.6 on 2024-07-18 09:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('asset_App', '0004_alter_depreciation_branch_alter_depreciation_office'),
    ]

    operations = [
        migrations.AddField(
            model_name='depreciation',
            name='custom_percentages',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='depreciation',
            name='depreciation_method',
            field=models.CharField(choices=[('straight_line', 'Straight Line'), ('declining_balance', 'Declining Balance'), ('sum_of_years_digits', 'Sum of the Years Digits'), ('others', 'Others')], max_length=50),
        ),
    ]
