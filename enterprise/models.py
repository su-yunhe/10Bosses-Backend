import os
from datetime import datetime

from django.db import models
from django.db.models import CASCADE
from Users.models import Applicant, Information
from recruit.models import Material, Recruit


def custom_enterprise_picture_upload_to(instance, filename):
    now = datetime.now()

    base, ext = os.path.splitext(filename)

    new_filename = f'{instance.id}_enterprise_picture_{now.strftime("%Y%m%d%H%M%S")}{ext}'

    return os.path.join('enterprise/', new_filename)


# Create your models here.
class Enterprise(models.Model):
    id = models.AutoField(primary_key=True)  # id
    name = models.CharField(max_length=128, default="")  # 名称
    profile = models.TextField(default="")
    picture = models.ImageField(upload_to=custom_enterprise_picture_upload_to, max_length=225, null=False, default='enterprise/default.jpg') # 设置一个默认路径
    address = models.TextField(default="")
    member = models.ManyToManyField(Applicant, related_name='member_enterprise')
    fans = models.ManyToManyField(Applicant, related_name='user_like_enterprise')
    # fan = models.IntegerField(default=0)
    recruitment = models.ManyToManyField(Recruit, related_name='recruitment_belong_enterprise')
    recruit_material = models.ManyToManyField(Material, related_name='recruit_user_material')
    withdraw = models.ManyToManyField(Applicant, related_name='withdraw_enterprise')
    manager = models.ForeignKey(Applicant, on_delete=CASCADE, null=True)  # 公司管理人

    def __str__(self):
        return self.name

    class Meta:
        db_table = "enterprise_enterprise"


class UserInformationEnterprise(models.Model):
    id = models.AutoField(primary_key=True)
    post = models.CharField(max_length=128, default="")
    join_date = models.DateField(auto_now_add=True)
    user = models.ForeignKey('Users.Applicant', on_delete=CASCADE, null=True)
