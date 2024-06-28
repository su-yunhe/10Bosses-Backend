from django.db import models
from django.db.models import CASCADE


class Applicant(models.Model):
    id = models.AutoField(primary_key=True)
    user_name = models.CharField(max_length=128, unique=True)
    password = models.CharField(max_length=128)
    email = models.EmailField(unique=True)
    interests = models.CharField(max_length=128, default="")
    background = models.CharField(max_length=128, default="")
    note = models.FileField(
        upload_to="person_note/", default="person_note/default_note.txt"
    )
    enterprise_id = models.IntegerField(default=0)
    manage_enterprise_id = models.IntegerField(default=0)
    is_upload = models.BooleanField(default=False)
    followers = models.ManyToManyField('self', symmetrical=False, related_name='following')
    only_information = models.ForeignKey('Information', on_delete=CASCADE, null=True)

    class Meta:
        db_table = "applicant_info"


class Position(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.IntegerField(default=0)
    recruit_id = models.IntegerField(default=0)
    recruit_name = models.CharField(max_length=128, default="")

    class Meta:
        db_table = "applicant_interests"


class Information(models.Model):
    id = models.AutoField(primary_key=True)
    only_user = models.ForeignKey('Applicant', on_delete=CASCADE, null=True)
    name = models.CharField(max_length=128, default="", null=True)
    phone = models.CharField(max_length=30, default="", null=True)
    native_place = models.CharField(max_length=128, default="", null=True)
    nationality = models.CharField(max_length=128, default="", null=True)
    birthday = models.DateField(null=True, blank=True, default=None)
    marriage = models.BooleanField(default=False, null=True)
    gender = models.CharField(max_length=30, default="", null=True)
    education = models.CharField(max_length=30, default="", null=True)
    school = models.CharField(max_length=128, default="", null=True)


