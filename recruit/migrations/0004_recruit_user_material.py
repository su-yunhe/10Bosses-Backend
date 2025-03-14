# Generated by Django 4.2.4 on 2024-07-01 03:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("recruit", "0003_remove_recruit_user_material"),
    ]

    operations = [
        migrations.AddField(
            model_name="recruit",
            name="user_material",
            field=models.ManyToManyField(
                related_name="application_material", to="recruit.material"
            ),
        ),
    ]
