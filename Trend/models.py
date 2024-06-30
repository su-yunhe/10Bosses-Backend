from datetime import datetime, timezone
from django.db import models


class Dynamic(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.IntegerField(default=0)
    content = models.TextField(default="")
    type = models.CharField(
        max_length=128, default=""
    )  # 类型：技术学习进展、科研成果、项目成果
    send_date = models.DateTimeField(default=datetime.now)
    transpond_id = models.IntegerField(default=0)  # 如果是转发的，则转发的动态的id
    like_count = models.IntegerField(default=0)
    comment_count = models.IntegerField(default=0)

    class Meta:
        db_table = "applicant_trends"


class Tag(models.Model):
    id = models.AutoField(primary_key=True)
    trend_id = models.IntegerField(default=0)
    recruit_name = models.CharField(max_length=128, default="")

    class Meta:
        db_table = "trend_tags"  # 动态的标签，一对多


class Like(models.Model):
    id = models.AutoField(primary_key=True)
    trend_id = models.IntegerField(default=0)
    user_id = models.IntegerField(default=0)

    class Meta:
        db_table = "trend_likes"  # 动态的点赞，一对多


class Comment(models.Model):
    id = models.AutoField(primary_key=True)
    trend_id = models.IntegerField(default=0)
    user_id = models.IntegerField(default=0)
    content = models.TextField(default="")
    send_date = models.DateTimeField(default=datetime.now)

    class Meta:
        db_table = "trend_comments"  # 动态的评论，一对多


class TrendPicture(models.Model):
    id = models.AutoField(primary_key=True)
    trend_id = models.IntegerField(default=0)
    user_id = models.IntegerField(default=0)
    picture = models.ImageField(
        upload_to="trend_pic/",
        max_length=225,
        null=False,
        default="trend_pic/default.jpg",
    )  # 设置一个默认路径

    class Meta:
        db_table = "trend_pictures"  # 动态的图片，一对多
