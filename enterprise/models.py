from django.db import models
from django.db.models import CASCADE
from Users.models import Applicant, Information
from recruit.models import Material, Recruit


# Create your models here.
class Enterprise(models.Model):
    id = models.AutoField(primary_key=True)  # id
    name = models.CharField(max_length=128, default="")  # 名称
    profile = models.TextField(default="")
    picture = models.ImageField(upload_to='enterprise/', max_length=225, null=False, default='enterprise/default.jpg') # 设置一个默认路径
    address = models.TextField(default="")
    member = models.ManyToManyField(Applicant, related_name='member_enterprise')
    fans = models.ManyToManyField(Applicant, related_name='user_like_enterprise')
    fan = models.IntegerField(default=0)
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
    join_data = models.DateField(auto_now_add=True)
    user = models.ForeignKey('Users.Applicant', on_delete=CASCADE, null=True)
