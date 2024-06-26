from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from chat.models import *


# 发送一条私信
@csrf_exempt
def send_message(request):
    if request.method == "POST":
        content = request.POST.get("content")
        sender = get_object_or_404(Applicant, user_name=request.POST.get("sender"))
        recipient = get_object_or_404(Applicant, user_name=request.POST.get("recipient"))  # 获取的是一个Applicant实例对象

        # 查找或创建一个对话
        conversation = Conversation.objects.filter(participants=sender).filter(participants=recipient).first()
        if not conversation:
            conversation = Conversation.objects.create()
            conversation.participants.add(sender, recipient)

        # 创建并保存消息
        message = Message.objects.create(sender=sender, conversation=conversation, content=content)

        # 更新最后一条消息的时间戳
        conversation.last_message = message.timestamp
        conversation.save()

        return JsonResponse({"error": 0, "msg": "消息发送成功"})

    else:
        return JsonResponse({"error": 2001, "msg": "请求方式错误"})