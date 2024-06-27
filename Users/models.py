from django.db import models
from django.db.models import CASCADE, SET_NULL


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
    Information = models.ForeignKey('Information', on_delete=SET_NULL, null=True)

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
    user = models.ForeignKey('Applicant', on_delete=CASCADE, null=False)
    name = models.CharField(max_length=128, default="")  # 真实姓名
    phone = models.CharField(max_length=30, default="")  # 电话
    native_place = models.CharField(max_length=128, default="")  # 籍贯
    nationality = models.CharField(max_length=128, default="")  # 民族
    birthday = models.DateField(default=None, blank=True, null=True)  # 生日
    marriage = models.BooleanField(default=False)  # 婚姻状态
    gender = models.CharField(max_length=30, default="")  # 性别
    education = models.CharField(max_length=30, default="")  # 学历
    school = models.CharField(max_length=128, default="")  # 学校
