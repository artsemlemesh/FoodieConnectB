# Generated by Django 5.1.3 on 2024-12-13 02:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("reviews", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="restaurant",
            name="description",
            field=models.TextField(default=""),
        ),
    ]
