from django.db import models
from Users.models import Applicant


class Conversation(models.Model):
    participants = models.ManyToManyField(Applicant, related_name='conversations')
    last_message = models.DateTimeField(auto_now=True)  # 时间可更新


class Message(models.Model):
    sender = models.ForeignKey(Applicant, related_name='sent_messages', on_delete=models.CASCADE)
    conversation = models.ForeignKey(Conversation, related_name='messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)  # 时间不可更改
    is_read = models.BooleanField(default=False)
