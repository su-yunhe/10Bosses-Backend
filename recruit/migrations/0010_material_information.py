# Generated by Django 4.2.4 on 2024-06-27 02:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("Users", "0006_applicant_information"),
        ("recruit", "0009_remove_material_birthday_remove_material_education_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="material",
            name="information",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="Users.information",
            ),
        ),
    ]
