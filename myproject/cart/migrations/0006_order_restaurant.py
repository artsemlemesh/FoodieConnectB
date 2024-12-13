# Generated by Django 5.1.3 on 2024-12-13 01:53

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cart", "0005_alter_order_status"),
        ("reviews", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="restaurant",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="orders",
                to="reviews.restaurant",
            ),
        ),
    ]
