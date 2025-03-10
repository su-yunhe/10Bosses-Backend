# Generated by Django 5.0.6 on 2024-06-29 13:23

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('Users', '0001_initial'),
        ('enterprise', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Material',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('status', models.CharField(default='3', max_length=20)),
                ('submit_time', models.DateField(auto_now_add=True)),
                ('curriculum_vitae', models.FileField(blank=True, upload_to='material_curriculum/')),
                ('certificate', models.FileField(blank=True, upload_to='certificate/')),
                ('enterprise', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='enterprise.enterprise')),
                ('information', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='Users.information')),
            ],
        ),
        migrations.CreateModel(
            name='Recruit',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('post', models.CharField(default='', max_length=128)),
                ('profile', models.TextField(default='')),
                ('number', models.IntegerField(default=0)),
                ('salary_low', models.IntegerField(default=0)),
                ('salary_high', models.IntegerField(default=0)),
                ('status', models.BooleanField(default=True)),
                ('release_time', models.DateField(auto_now_add=True)),
                ('experience', models.CharField(default='无要求', max_length=128)),
                ('address', models.CharField(default='', max_length=128)),
                ('requirement', models.TextField(default='无要求')),
                ('education', models.CharField(default='无要求', max_length=30)),
                ('enterprise', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='enterprise.enterprise')),
                ('user_material', models.ManyToManyField(related_name='application_material', to='recruit.material')),
            ],
        ),
        migrations.AddField(
            model_name='material',
            name='recruit',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='recruit.recruit'),
        ),
    ]
