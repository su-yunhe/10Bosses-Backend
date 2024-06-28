from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from chat.models import *
import logging

logger = logging.getLogger(__name__)


# 打开一个对话
@csrf_exempt
def open_conversation(request):
    if request.method == "POST":
        sender = Applicant.objects.get(id=request.POST.get("userId"))
        recipient = get_object_or_404(Applicant, user_name=request.POST.get("recipientName"))  # 获取的是一个Applicant实例对象
        try:
            # 查看对话是否已创建
            conversation = Conversation.objects.filter(participants=sender).filter(participants=recipient).first()

            # 创建对话
            if not conversation:
                conversation = Conversation.objects.create()
                conversation.participants.add(sender, recipient)
                conversation.save()

            conversation_id = conversation.id

            return JsonResponse({"error": 0, "msg": "打开对话成功", "conversation_id": conversation_id})

        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return JsonResponse({"error": 500, "msg": "服务器内部错误"})

    else:
        return JsonResponse({"error": 2001, "msg": "请求方式错误"})


# 发送一条私信
@csrf_exempt
def send_message(request):
    if request.method == "POST":
        userid = request.POST.get("userId")
        conversation_id = request.POST.get("conversationId")
        content = request.POST.get("content")

        try:
            sender = Applicant.objects.get(id=userid)
            conversation = Conversation.objects.get(id=conversation_id)
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
        try:
            userid = request.POST.get("userId")
            user = Applicant.objects.get(id=userid)
            conversations = Conversation.objects.filter(participants=user)
            response_data = []

            for conversation in conversations:
                participants = conversation.participants.exclude(id=userid)
                if participants.exists():
                    other_user = participants.first()
                    response_data.append({
                        'conversation_id': conversation.id,
                        'last_message': conversation.last_message,
                        'other_user_id': other_user.id,
                        'other_user_name': other_user.user_name
                    })
            return JsonResponse({"error": 0, "msg": "成功获取所有对话", "data": response_data})

        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return JsonResponse({"error": 500, "msg": "服务器内部错误"})
    else:
        return JsonResponse({"error": 2001, "msg": "请求方式错误"})


# 加载某个对话的历史消息(返回所有历史消息，可改)
@csrf_exempt
def get_history_messages(request):
    if request.method == "POST":
        try:
            conversation_id = request.POST.get("conversationId")
            messages = list(Message.objects.filter(conversation_id=conversation_id).values("content", "timestamp",
                                                                                           "sender__user_name",
                                                                                           "is_read"))
            return JsonResponse({"error": 0, "msg": "获取消息成功", "data": messages})
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return JsonResponse({"error": 500, "msg": "服务器内部错误"})
    else:
        return JsonResponse({"error": 2001, "msg": "请求方式错误"})


# 已读(在打开一个对话后，里面的消息设置为已读)
@csrf_exempt
def read_message(request):
    if request.method == "POST":
        try:
            userid = request.POST.get("userId")
            conversation_id = request.POST.get("conversationId")
            messages = Message.objects.filter(conversation_id=conversation_id).exclude(sender=userid)

            for message in messages:
                message.is_read = True
                message.save()

            return JsonResponse({"error": 0, "msg": "消息已读成功"})

        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return JsonResponse({"error": 500, "msg": "服务器内部错误"})
    else:
        return JsonResponse({"error": 2001, "msg": "请求方式错误"})
