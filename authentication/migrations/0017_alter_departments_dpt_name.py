# Generated by Django 5.1.3 on 2024-11-21 11:33

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0016_alter_chairman_name_alter_commissionmembers_name_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='departments',
            name='dpt_name',
            field=models.CharField(max_length=255, unique=True, validators=[django.core.validators.RegexValidator('^[\\w\\s#$%&*+-/]*$', 'Special characters are not allowed.')]),
        ),
    ]
