# Generated by Django 4.2.4 on 2024-06-28 03:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("Users", "0015_information"),
    ]

    operations = [
        migrations.AddField(
            model_name="applicant",
            name="only_information",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="Users.information",
            ),
        ),
    ]
