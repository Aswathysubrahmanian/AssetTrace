# Generated by Django 5.0.6 on 2024-10-17 06:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0005_branches_created_at_client_created_at_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='has_head_office',
            field=models.BooleanField(default=False),
        ),
    ]
