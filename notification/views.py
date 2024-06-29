# 需要实现：
# 1. 企业审核通过（不通过）用户投递的简历后，系统给用户发送该企业的加入邀请（拒绝）通知
# 2. 用户同意（拒绝）加入企业后，系统给企业管理员发送通知
# 3. 企业员工退出企业，系统给企业管理员发送通知
# 4. 点赞、评论、关注通知在动态部分实现
from datetime import datetime

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from Users.models import Applicant
from enterprise.models import Enterprise
from notification.models import Notification


@csrf_exempt
def employee_quit(request):
    if request.method == 'POST':
        # 需要根据用户id获取所在企业，因此需要在调用退出企业的接口之前调用
        user_id = request.POST['user_id']
        # 获取用户名
        user_name = Applicant.objects.get(id=user_id).user_name
        enterprise_id = Applicant.objects.get(id=user_id).enterprise_id
        # 获取企业管理员
        if not enterprise_id:
            return JsonResponse({'error': 2002, "msg": "用户没有加入任何企业"})
        manager_id = Enterprise.objects.get(id=enterprise_id).manager_id
        print(manager_id, user_id)
        if str(manager_id) == str(user_id):
            return JsonResponse({"error": 2003, "msg": "企业管理员不能退出企业"})
        notification = Notification()
        notification.user_id = manager_id
        notification.title = "员工退出通知"
        notification.type = 5
        notification.message = "员工 " + user_name + " 已退出企业"
        notification.is_read = 0
        notification.time = datetime.now(),
        notification.related_user_id = user_id
        notification.save()
        return JsonResponse(
            {
                "error": 0,
                "msg": "系统消息发送成功",
            }
        )
    return JsonResponse({'error': 2001, "msg": "请求方式错误"})

