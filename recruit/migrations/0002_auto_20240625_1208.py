# Generated by Django 3.1.3 on 2024-06-25 04:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recruit', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='recruit',
            name='employment',
        ),
        migrations.RemoveField(
            model_name='recruit',
            name='user_application',
        ),
        migrations.AddField(
            model_name='material',
            name='status',
            field=models.CharField(default='waiting', max_length=20),
        ),
        migrations.AddField(
            model_name='recruit',
            name='user_material',
            field=models.ManyToManyField(related_name='application_material', to='recruit.Material'),
        ),
    ]
