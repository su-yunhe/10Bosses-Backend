from datetime import datetime

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from Users.models import Applicant
from enterprise.models import Enterprise
from notification.models import Notification
from recruit.models import Recruit


# 需要实现：
# 1. 企业审核通过（不通过）用户投递的简历后，系统给用户发送该企业的加入邀请（拒绝）通知
# 2. 用户同意（拒绝）加入企业后，系统给企业管理员发送通知
# 3. 企业员工退出企业，系统给企业管理员发送通知
# 4. 点赞、评论、关注通知在动态部分实现

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
        message = ""
        is_passed = True if is_passed == 1 else False
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
        notification.related_enterprise_id = enterprise_id
        notification.save()
        return JsonResponse(
            {
                "error": 0,
                "msg": "系统消息发送成功",
            }
        )
    return JsonResponse({"error": 2001, "msg": "请求方式错误"})
