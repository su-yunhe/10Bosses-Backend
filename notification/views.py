from datetime import datetime

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from Users.models import Applicant
from enterprise.models import Enterprise
from notification.models import Notification
from recruit.models import Recruit


# 需要实现：
# 发送通知部分：
# 1. 企业审核通过（不通过）用户投递的简历后，系统给用户发送该企业的加入邀请（拒绝）通知
# 2. 用户同意（拒绝）加入企业后，系统给企业管理员发送通知
# 3. 企业员工退出企业，系统给企业管理员发送通知
# 4. 点赞、评论、关注通知在动态部分实现
# 通知展示部分：
# 1. 获取用户通知列表
# 2. 获取通知详情
# 3. 通知已读标记
# 4. 用户删除通知


@csrf_exempt
def employee_quit_notification(request):
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
        # 构建消息实体
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
    return JsonResponse({"error": 2001, "msg": "请求方式错误"})


@csrf_exempt
def resume_notification(request):
    # 简历通过/不通过后系统给用户发通知
    if request.method == 'POST':
        # 需要传入：投递人user_id,招聘recruitment_id,是否通过is_passed(boolean)
        user_id = request.POST['user_id']
        recruitment_id = request.POST['recruitment_id']
        is_passed = request.POST['is_passed']
        # 获取企业名、岗位名
        enterprise_id = Recruit.objects.get(id=recruitment_id).enterprise_id
        enterprise_name = Enterprise.objects.get(id=enterprise_id).name
        position = Recruit.objects.get(id=recruitment_id).post
        is_passed = True if is_passed == "1" else False
        if is_passed:
            message = "您投递在 " + enterprise_name + " 公司 " + position + " 岗位的简历已被通过！管理员邀请您加入企业，请及时进行企业员工认证~"
        else:
            message = "您投递在 " + enterprise_name + " 公司 " + position + " 岗位的简历并未被通过。尝试使用10bosses提供的AI简历优化能提高被企业录用的概率哦~"
        # 构建消息实体
        notification = Notification()
        notification.user_id = user_id
        notification.title = "企业回复了您的投递"
        notification.type = 4
        notification.message = message
        notification.time = datetime.now()
        notification.related_recruitment_id = recruitment_id
        notification.save()
        return JsonResponse(
            {
                "error": 0,
                "msg": "系统消息发送成功",
            }
        )
    return JsonResponse({"error": 2001, "msg": "请求方式错误"})


@csrf_exempt
def user_reply_notification(request):
    # 用户回复（同意加入或拒绝）企业邀请的通知
    if request.method == "POST":
        # 需要传入：用户user_id，招聘recruitment_id，是否同意is_agreed
        user_id = request.POST.get("user_id")
        recruitment_id = request.POST.get("recruitment_id")
        is_agreed = request.POST.get("is_agreed")
        # 获取企业管理员
        enterprise_id = Recruit.objects.get(id=recruitment_id).enterprise_id
        manager_id = Enterprise.objects.get(id=enterprise_id).manager_id
        # 获取用户名
        user_name = Applicant.objects.get(id=user_id).user_name
        # 获取岗位名
        position = Recruit.objects.get(id=recruitment_id).post
        is_agreed = True if is_agreed == "1" else False
        if is_agreed:
            message = f"您发放的 {position} 岗位的offer已被用户 {user_name} 接受，用户已成为公司旗下员工，详情进入员工列表查看"
        else:
            message = f"您发放的 {position} 岗位的offer已被用户 {user_name} 拒绝"
        notification = Notification()
        notification.user_id = manager_id
        notification.title = "用户回复"
        notification.type = 4
        notification.message = message
        notification.time = datetime.now()
        notification.related_user_id = user_id
        notification.related_recruitment_id = recruitment_id
        notification.save()
        return JsonResponse(
            {
                "error": 0,
                "msg": "系统消息发送成功",
            }
        )
    return JsonResponse({"error": 2001, "msg": "请求方式错误"})


@csrf_exempt
def get_notification_list(request):
    # 获取用户消息列表
    if request.method == "POST":
        # 需要传入：用户user_id
        user_id = request.POST.get("user_id")
        if not Applicant.objects.filter(id=user_id).exists():
            return JsonResponse({'error': 2004, 'msg': "用户不存在"})
        results = list(Notification.objects.values().filter(user_id=user_id))
        return JsonResponse(
            {
                "error": 0,
                "msg": "获取用户消息列表成功",
                "data": {
                    "results": results
                }
            }
        )
    return JsonResponse({"error": 2001, "msg": "请求方式错误"})


@csrf_exempt
def get_notification_detail(request):
    # 获取通知详细信息
    if request.method == "POST":
        # 需要传入：通知notification_id
        notification_id = request.POST.get("notification_id")
        notification = Notification.objects.get(id=notification_id)
        notification.is_read = 1
        notification.save()
        results = list(Notification.objects.values().filter(id=notification_id))
        return JsonResponse(
            {
                "error": 0,
                "msg": "获取通知详情成功",
                "data": {
                    "results": results
                }
            }
        )
    return JsonResponse({"error": 2001, "msg": "请求方式错误"})


@csrf_exempt
def delete_notification(request):
    # 用户删除通知
    if request.method == "POST":
        # 需要传入的数据：通知notification_id
        notification_id = request.POST.get("notification_id")
        if not Notification.objects.filter(id=notification_id).exists():
            return JsonResponse({'error': 2005, 'msg': "通知不存在"})
        notification = Notification.objects.get(id=notification_id)
        notification.delete()
        return JsonResponse({"error": 0, "msg": "删除通知成功"})
    return JsonResponse({"error": 2001, "msg": "请求方式错误"})
