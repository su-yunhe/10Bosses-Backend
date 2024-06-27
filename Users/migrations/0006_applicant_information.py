# Generated by Django 4.2.4 on 2024-06-27 02:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("Users", "0005_information"),
    ]

    operations = [
        migrations.AddField(
            model_name="applicant",
            name="Information",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="Users.information",
            ),
        ),
    ]
