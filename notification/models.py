from django.db import models

from django.db import models


class Notification(models.Model):
    TYPE_CHOICES = [
        (1, '点赞通知'),
        (2, '评论通知'),
        (3, '关注通知'),
        (4, '企业通知'),
        (5, '员工退出企业通知'),
    ]

    id = models.AutoField(primary_key=True)
    user_id = models.IntegerField()  # 通知接收用户的ID
    title = models.CharField(max_length=100)  # 通知标题
    type = models.IntegerField(choices=TYPE_CHOICES)  # 通知类型
    message = models.TextField()  # 通知内容
    is_read = models.BooleanField(default=False)  # 是否已读
    time = models.DateTimeField(auto_now_add=True)  # 通知时间
    related_user_id = models.IntegerField(null=True, blank=True, default=0)  # 相关用户的ID（如被谁点赞/评论、谁退出企业）
    related_blog_id = models.IntegerField(null=True, blank=True, default=0)  # 相关动态的ID（被点赞/评论动态）
    related_enterprise_id = models.IntegerField(null=True, blank=True, default=0)  # 相关企业的ID（企业邀请加入）
    attachment = models.CharField(max_length=255, null=True, blank=True, default="")  # 附件路径或URL（暂时为空）

    def __str__(self):
        return f"{self.title} - {self.user_id}"

    class Meta:
        db_table = 'notification'
