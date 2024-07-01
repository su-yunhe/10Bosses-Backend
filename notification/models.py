from django.db import models

from django.db import models


class Notification(models.Model):
    TYPE_CHOICES = [
        (1, '点赞通知'),  # 关联id填写related_user_id字段和related_blog_id字段，关联点赞人和动态
        (2, '评论通知'),  # 同点赞
        (3, '关注通知'),  # 同点赞
        (4, '企业通知'),  # 关联related_recruitment_id字段，关联投递简历的招聘信息
        (5, '员工退出企业通知'),  # 关联related_user_id字段，关联退出企业的用户
        (6, '员工同意/拒绝企业通知'),  # 关联related_user_id字段和related_recruitment_id字段，关联应聘人和应聘的招聘信息（岗位）
        (7, '私信通知')  # 关联related_user_id字段，关联私信来源人
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
    related_material_id = models.IntegerField(null=True, blank=True, default=0)  # 相关招聘的材料（简历）ID（企业邀请加入）
    attachment = models.CharField(max_length=255, null=True, blank=True, default="")  # 附件路径或URL（暂时为空）

    def __str__(self):
        return f"{self.title} - {self.user_id}"

    class Meta:
        db_table = 'notification'
