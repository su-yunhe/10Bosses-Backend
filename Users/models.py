from django.db import models


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
    name = models.CharField(max_length=128, default="")
    phone = models.CharField(max_length=30, default="")
    native_place = models.CharField(max_length=128, default="")
    nationality = models.CharField(max_length=128, default="")
    birthday = models.DateField(null=True, blank=True, default=None)
    marriage = models.BooleanField(default=False)
    gender = models.CharField(max_length=30, default="")
    education = models.CharField(max_length=30, default="")
    school = models.CharField(max_length=128, default="")


