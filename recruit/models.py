from django.db import models
from django.db.models import CASCADE, SET_NULL
from Users.models import Applicant
import json


# Create your models here.
class Recruit(models.Model):
    id = models.AutoField(primary_key=True)  # id
    enterprise = models.ForeignKey('enterprise.Enterprise', on_delete=CASCADE, null=False)  # 归属公司
    post = models.CharField(max_length=128, default="")  # 岗位
    profile = models.TextField(default="")  # 工作简介
    number = models.IntegerField(default=0)  # 招募数量
    salary_low = models.IntegerField(default=0)  # 最高薪资
    salary_high = models.IntegerField(default=0)  # 最低薪资
    status = models.BooleanField(default=True)  # 招聘状态
    # user_application = models.ManyToManyField(User, related_name='application_recruit_user')
    user_material = models.ManyToManyField('Material', related_name='application_material') # 申请材料列表
    # employment = models.ManyToManyField(User, related_name='employment_recruit_user')
    release_time = models.DateField(auto_now_add=True)  # 发布时间
    experience = models.CharField(max_length=128, default="无要求")  # 工作经验
    address = models.CharField(max_length=128, default="")  # 工作地点
    requirement = models.TextField(default="无要求")  # 工作要求
    education = models.CharField(max_length=30, default="无要求")  # 最低学历要求


class Material(models.Model):
    id = models.AutoField(primary_key=True)  # id 主键
    status = models.CharField(max_length=20, default='3', null=False)      # 3 待审核 2 已通过 1 已录用 0 未通过 5 作废 6 已拒绝
    recruit = models.ForeignKey('Recruit', on_delete=CASCADE, null=True)
    enterprise = models.ForeignKey('enterprise.Enterprise', on_delete=CASCADE, null=True)
    submit_time = models.DateField(auto_now_add=True)  # 发布时间
    information = models.ForeignKey('Users.Information', on_delete=SET_NULL, null=True)
    curriculum_vitae = models.FileField(upload_to='material_curriculum/', blank=True)  # 电子简历
    certificate = models.FileField(upload_to='certificate/', blank=True)  # 证书

    def to_json(self):
        info = {
            "material_id": self.id,
            "material_status": self.status,
            "material_user_id": self.user.id,
            "material_user_name": self.user.user_name,
            "material_curriculum_vitae": self.curriculum_vitae.url,
            "material_certificate": self.certificate.url,
            # "material_user_real_name": self.name,
            # "material_user_gender": self.gender,
            # "material_user_native_place": self.native_place,
            # "material_user_nationality": self.nationality,
            # "material_user_birthday": self.birthday,
            # "material_user_marriage": self.marriage,
            # "material_user_email": self.email,
            # "material_user_phone": self.phone,
            # "material_user_education": self.education,
            # "material_user_school": self.school,
        }
        return json.dumps(info)



