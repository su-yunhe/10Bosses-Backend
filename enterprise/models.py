from django.db import models
from django.db.models import CASCADE
from Users.models import Applicant


# Create your models here.
class Enterprise(models.Model):
    id = models.AutoField(primary_key=True)  # id
    name = models.CharField(max_length=128, default="")  # 名称
    profile = models.TextField(default="")
    picture = models.ImageField(upload_to='enterprise/', max_length=225, blank=True, null=True)
    address = models.TextField(default="")
    member = models.ManyToManyField(Applicant, related_name='member_enterprise')
    manager = models.ForeignKey('user.User', on_delete=CASCADE, null=False)  # 公司管理人

