# Generated by Django 5.0.6 on 2024-07-01 06:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('notification', '0003_rename_related_enterprise_id_notification_related_recruitment_id_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='notification',
            old_name='related_recruitment_id',
            new_name='related_material_id',
        ),
    ]
