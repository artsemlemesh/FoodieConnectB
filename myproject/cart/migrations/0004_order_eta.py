# Generated by Django 5.1.3 on 2024-12-06 06:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cart", "0003_alter_order_status"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="eta",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
