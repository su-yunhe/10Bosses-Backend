from datetime import datetime
import os
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import re
from enterprise.models import Enterprise
from recruit.models import *
from utils.token import create_token
from .models import *
import logging
from notification.models import *

logger = logging.getLogger(__name__)


@csrf_exempt
def register(request):
    if request.method == "POST":
        try:
            username = request.POST.get("userName")
            password1 = request.POST.get("password1")
            password2 = request.POST.get("password2")
            email = request.POST.get("email")

            repeated_name = Applicant.objects.filter(user_name=username)
            if repeated_name.exists():
                return JsonResponse({"error": 4001, "msg": "用户名已存在"})

            repeated_email = Applicant.objects.filter(email=email)
            if repeated_email.exists():
                return JsonResponse({"error": 4002, "msg": "邮箱已存在"})
            # 检测两次密码是否一致
            if password1 != password2:
                return JsonResponse({"error": 4003, "msg": "两次输入的密码不一致"})
            # 检测密码不符合规范：8-18，英文字母+数字
            if not re.match("^(?![0-9]+$)(?![a-zA-Z]+$)[0-9A-Za-z]{8,18}$", password1):
                return JsonResponse({"error": 4004, "msg": "密码不符合规范"})

            new_user = Applicant()
            new_user.user_name = username
            new_user.password = password1
            new_user.email = email
            information = Information.objects.create()
            new_user.only_information = information
            new_user.save()
            information.only_user = new_user
            information.save()
            token = create_token(username)
            return JsonResponse(
                {
                    "error": 0,
                    "msg": "注册成功!",
                    "data": {
                        "userid": new_user.id,
                        "username": new_user.user_name,
                        "authorization": token,
                        "email": new_user.email,
                    },
                }
            )
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return JsonResponse({"error": 500, "msg": "服务器内部错误"})
    else:
        return JsonResponse({"error": 2001, "msg": "请求方式错误"})


@csrf_exempt
def login(request):
    if request.method == "POST":
        username = request.POST.get("userName")
        password = request.POST.get("password")
        try:
            user = Applicant.objects.get(user_name=username)
        except:
            return JsonResponse({"error": 4001, "msg": "用户名不存在"})
        if user.password != password:
            return JsonResponse({"error": 4002, "msg": "密码错误"})
        token = create_token(username)
        return JsonResponse(
            {
                "error": 0,
                "msg": "登录成功!",
                "data": {
                    "userid": user.id,
                    "username": user.user_name,
                    "authorization": token,
                    "email": user.email,
                },
            }
        )

    else:
        return JsonResponse({"error": 2001, "msg": "请求方式错误"})


@csrf_exempt
def user_modify_background(request):
    if request.method == "POST":
        userid = request.POST.get("userId")
        background = request.POST.get("background")
        results = Applicant.objects.get(id=userid)
        results.background = background
        results.save()
        return JsonResponse({"error": 0, "msg": "修改学历成功"})
    else:
        return JsonResponse({"error": 2001, "msg": "请求方式错误"})


@csrf_exempt
def get_single_applicant(request):
    if request.method == "POST":
        userid = request.POST.get("userId")
        results = list(Applicant.objects.filter(id=userid).values())
        interests = list(Position.objects.filter(user_id=userid).values())
        if not results:  # 如果查询结果为空
            return JsonResponse({"error": 1001, "msg": "查无此人"})

        return JsonResponse(
            {
                "error": 0,
                "msg": "获取用户信息成功",
                "data": {
                    "results": results,
                    "interests": interests,
                },
            }
        )
    else:
        return JsonResponse({"error": 2001, "msg": "请求方式错误"})


@csrf_exempt
def interest_add(request):
    if request.method == "POST":
        userid = request.POST.get("userId")
        recruitid = request.POST.get("recruitId")
        new_position = Position()
        new_position.user_id = userid
        new_position.recruit_id = recruitid
        temp = Recruit()
        temp = Recruit.objects.get(id=recruitid)
        new_position.recruit_name = temp.post
        new_position.save()
        return JsonResponse({"error": 0, "msg": "添加意向岗位成功"})
    else:
        return JsonResponse({"error": 2001, "msg": "请求方式错误"})


# 用户修改个人信息
@csrf_exempt
def user_modify_info(request):
    if request.method == "POST":
        userid = request.POST.get("userId")
        user = Applicant.objects.get(id=userid)
        new_name = request.POST.get("name")
        if new_name:
            user.user_name = new_name
        new_password = request.POST.get("password")
        if new_password:
            user.password = new_password
        new_email = request.POST.get("email")
        if new_email:
            user.email = new_email
        new_background = request.POST.get("background")
        if new_background:
            user.background = new_background
        user.save()
        return JsonResponse({"error": 0, "msg": "修改信息成功"})
    else:
        return JsonResponse({"error": 2001, "msg": "请求方式错误"})


# 用户注销
@csrf_exempt
def user_delete(request):
    if request.method == "POST":
        userid = request.POST.get("userId")
        # 先在applicant表中直接删除
        user = Applicant.objects.get(id=userid)
        user.delete()
        # 如果管理了某个企业，则该企业自动解散
        if user.manage_enterprise_id != 0:
            manage_enterprise = Enterprise.objects.get(id=user.manage_enterprise_id)
            manage_enterprise.delete()

        return JsonResponse({"error": 0, "msg": "用户注销成功"})
    else:
        return JsonResponse({"error": 2001, "msg": "请求方式错误"})


# 游客查询用户(精准查询）
@csrf_exempt
def search_user(request):
    if request.method == "POST":
        name = request.POST.get("name")
        applicants = Applicant.objects.filter(user_name__icontains=name)
        results = []
        for applicant in applicants:
            if applicant.manage_enterprise_id != 0:
                manage_enterprise_name = Enterprise.objects.get(
                    id=applicant.manage_enterprise_id
                ).name
            else:
                manage_enterprise_name = None
            if applicant.enterprise_id != 0:
                enterprise_name = Enterprise.objects.get(
                    id=applicant.enterprise_id
                ).name
            else:
                enterprise_name = None
            # 构建结果字典
            result = {
                "user_id": applicant.id,
                "user_name": applicant.user_name,
                "email": applicant.email,
                "background": applicant.background,
                "manage_enterprise_name": manage_enterprise_name,
                "enterprise_name": enterprise_name,
            }
            results.append(result)

        return JsonResponse({"error": 0, "msg": "查询成功", "data": results})

    else:
        return JsonResponse({"error": 2001, "msg": "请求方式错误"})


@csrf_exempt  # 可以用于简化 CSRF 保护
def upload_pdf(request):
    if request.method == "POST":
        user_id = request.POST.get("user_id")
        # name = request.POST.get('user_name')
        pdf = request.FILES.get("note", None)
        print(pdf)
        user_temp = Applicant.objects.get(id=user_id)
        if pdf:
            user_temp.note = pdf
            user_temp.is_upload = True
            user_temp.save()

        return JsonResponse({"error": 0, "msg": "文件上传成功"})
    else:
        return JsonResponse({"error": 2001, "msg": "请求方式错误"})


@csrf_exempt
def user_follow(request):
    if request.method == "POST":
        follower_id = request.POST.get("userId")
        followee_id = request.POST.get("followeeId")

        follower = Applicant.objects.get(id=follower_id)
        followee = Applicant.objects.get(id=followee_id)

        # if followee in follower.following.all():
        #     return JsonResponse({"error": 1003, "msg": "已关注"})
        us_name = Applicant.objects.get(id=follower_id).user_name
        follower.following.add(followee)
        temp_note = Notification()
        temp_note.user_id = followee_id
        temp_note.title = "新增一位关注者"
        temp_note.type = 3
        temp_note.is_read = 0
        temp_note.message = "您多了一位关注者：" + us_name
        temp_note.time = datetime.now()
        temp_note.related_user_id = follower_id
        try:
            temp_note.save()
        except Exception as e:
            return JsonResponse({"error": 3001, "msg": str(e)})
        return JsonResponse({"error": 0, "msg": "关注成功"})

    else:
        return JsonResponse({"error": 2001, "msg": "请求方式错误"})


# 获取所有关注的人信息
@csrf_exempt
def get_all_followee(request):
    if request.method == "POST":
        try:
            userid = request.POST.get("userId")
            user = Applicant.objects.get(id=userid)
            followee = list(user.following.values("id", "user_name"))
            cnt = user.following.count()
            return JsonResponse(
                {
                    "error": 0,
                    "msg": "获取成功",
                    "data": {"followee": followee, "cnt": cnt},
                }
            )
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return JsonResponse({"error": 500, "msg": "服务器内部错误"})
    else:
        return JsonResponse({"error": 2001, "msg": "请求方式错误"})


# 获取所有粉丝
@csrf_exempt
def get_all_follower(request):
    if request.method == "POST":
        try:
            userid = request.POST.get("userId")
            user = Applicant.objects.get(id=userid)
            follower = list(user.followers.values("id", "user_name"))
            cnt = user.followers.count()
            return JsonResponse(
                {
                    "error": 0,
                    "msg": "获取成功",
                    "data": {"follower": follower, "cnt": cnt},
                }
            )
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return JsonResponse({"error": 500, "msg": "服务器内部错误"})
    else:
        return JsonResponse({"error": 2001, "msg": "请求方式错误"})


@csrf_exempt
def download_pdf(request):
    user_id = request.POST.get("userId")
    user_temp = Applicant.objects.get(id=user_id)
    if user_temp.note:
        file_path = user_temp.note.path
        print(file_path)
        if os.path.exists(file_path):
            download_url = f"/media/person_note/{os.path.basename(file_path)}"  # 假设文件存储在 media 目录下
            return JsonResponse(
                {"error": 0, "msg": "更新成功", "data": {"download_url": download_url}}
            )
        else:
            return JsonResponse({"error": 3001, "msg": "文件不存在"})
    else:
        return JsonResponse({"error": 2001, "msg": "请求方式错误"})


@csrf_exempt
def update_user_interest(request):
    if request.method == "POST":
        user_id = request.POST.get("userId")
        interests = request.POST.getlist("interests[]")
        Position.objects.filter(user_id=user_id).delete()
        for recruit_name in interests:
            Position.objects.create(user_id=user_id, recruit_name=recruit_name)
        return JsonResponse({"error": 0, "msg": "更新成功"})

    else:
        return JsonResponse({"error": 2001, "msg": "请求方式错误"})


# 取消关注用户
@csrf_exempt
def user_unfollow(request):
    if request.method == "POST":
        try:
            follower_id = request.POST.get("userId")
            followee_id = request.POST.get("followeeId")
            follower = Applicant.objects.get(id=follower_id)
            followee = Applicant.objects.get(id=followee_id)
            follower.following.remove(followee)
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return JsonResponse({"error": 500, "msg": "服务器内部错误"})

        return JsonResponse({"error": 0, "msg": "取消关注成功"})

    else:
        return JsonResponse({"error": 2001, "msg": "请求方式错误"})


@csrf_exempt
def update_information(request):
    if request.method == "POST":
        # 获取请求内容
        user_id = request.POST.get("user_id")
        name = request.POST.get("post", None)
        phone = request.POST.get("profile", None)
        native_place = request.POST.get("number", None)
        nationality = request.POST.get("education", None)
        birthday = request.POST.get("salary_low", None)
        marriage = request.POST.get("salary_high", None)
        gender = request.POST.get("address", None)
        education = request.POST.get("experience", None)
        school = request.POST.get("requirement", None)

        user = Applicant.objects.get(id=user_id)
        information = user.only_information
        if name:
            information.name = name
        if phone:
            information.phone = phone
        if native_place:
            information.native_place = native_place
        if nationality:
            information.nationality = nationality
        if birthday:
            today = datetime.now().date()
            if datetime.strptime(birthday, "%Y-%m-%d").date() > today:
                return JsonResponse({"error": 2002, "msg": "时间设置错误"})
            information.birthday = birthday
        if marriage:
            information.marriage = marriage
        if gender:
            information.gender = gender
        if education:
            information.education = education
        if school:
            information.school = school
        return JsonResponse({"error": 0, "msg": "修改成功"})

    return JsonResponse({"error": 8001, "msg": "请求方式错误"})
