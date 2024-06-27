from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from chat.models import *
import logging

logger = logging.getLogger(__name__)


# 发送一条私信
@csrf_exempt
def send_message(request):
    if request.method == "POST":
        content = request.POST.get("content")
        sender = get_object_or_404(Applicant, user_name=request.POST.get("sender"))
        recipient = get_object_or_404(Applicant, user_name=request.POST.get("recipient"))  # 获取的是一个Applicant实例对象

        try:
            # 查找或创建一个对话
            conversation = Conversation.objects.filter(participants=sender).filter(participants=recipient).first()

            if not conversation:
                logger.info("Creating a new conversation.")
                conversation = Conversation.objects.create()
                conversation.participants.add(sender, recipient)

            # 创建并保存消息
            message = Message.objects.create(sender=sender, conversation=conversation, content=content)
            # 更新最后一条消息的时间戳
            conversation.last_message = message.timestamp
            conversation.save()

            return JsonResponse({"error": 0, "msg": "消息发送成功"})

        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return JsonResponse({"error": 500, "msg": "服务器内部错误"})

    else:
        return JsonResponse({"error": 2001, "msg": "请求方式错误"})


# 获取对话列表
@csrf_exempt
def get_conversations(request):
    if request.method == "POST":
        userid = request.POST.get("userId")
        user = Applicant.objects.get(id=userid)
        conversations = Conversation.objects.filter(participants=user)
        response_data = []

        try:
            for conversation in conversations:
                participants = conversation.participants.exclude(id=userid)
                if participants.exists():
                    other_user = participants.first()
                    response_data.append({
                        'conversation_id': conversation.id,
                        'other_user_id': other_user.id,
                        'other_user_name': other_user.user_name
                    })
            return JsonResponse({"error": 0, "msg": "成功获取所有对话", "data": response_data})

        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return JsonResponse({"error": 500, "msg": "服务器内部错误"})
    else:
        return JsonResponse({"error": 2001, "msg": "请求方式错误"})


# 已读/已被查收
# 加载所有历史消息