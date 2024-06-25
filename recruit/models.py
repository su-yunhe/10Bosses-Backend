from django.db import models
from django.db.models import CASCADE

from user.models import User


# Create your models here.
class Recruit(models.Model):
    id = models.AutoField(primary_key=True)  # id
    enterprise = models.ForeignKey('enterprise.Enterprise', on_delete=CASCADE, null=False)  # 归属公司
    post = models.CharField(max_length=128, default="")  # 岗位
    profile = models.TextField(default="")  # 工作简介
    number = models.IntegerField(default=0)  # 招募数量
    # user_application = models.ManyToManyField(User, related_name='application_recruit_user')
    user_material = models.ManyToManyField('Material', related_name='application_material') # 申请材料列表
    # employment = models.ManyToManyField(User, related_name='employment_recruit_user')
    release_time = models.DateField(auto_now_add=True)  # 发布时间
    education = models.CharField(max_length=30, default="")  # 最低学历要求


class Material(models.Model):
    id = models.AutoField(primary_key=True)  # id 主键
    status = models.CharField(max_length=20, default='waiting', null=False)
    Recruit = models.ForeignKey('Recruit', on_delete=CASCADE, null=False)
    user = models.ForeignKey('user.User', on_delete=CASCADE, null=False)
    name = models.CharField(max_length=128, default="")  # 真实姓名
    email = models.EmailField(default="")  # 邮箱
    phone = models.CharField(max_length=30, default="")  # 电话
    native_place = models.CharField(max_length=128, default="")  # 籍贯
    nationality = models.CharField(max_length=128, default="")  # 民族
    birthday = models.DateField(default=None, blank=True, null=True)  # 生日
    marriage = models.BooleanField(default=False)  # 婚姻状态
    gender = models.CharField(max_length=30, default="")  # 性别
    education = models.CharField(max_length=30, default="")  # 学历
    school = models.CharField(max_length=128, default="")  # 学校
    curriculum_vitae = models.FileField(upload_to='material_curriculum/')  # 电子简历
    certificate = models.FileField(upload_to='certificate/')  # 证书



