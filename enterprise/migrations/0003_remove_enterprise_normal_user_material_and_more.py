# Generated by Django 4.2.4 on 2024-06-30 03:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("Users", "0001_initial"),
        ("enterprise", "0002_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="enterprise",
            name="normal_user_material",
        ),
        migrations.AddField(
            model_name="enterprise",
            name="withdraw",
            field=models.ManyToManyField(
                related_name="withdraw_enterprise", to="Users.applicant"
            ),
        ),
    ]
