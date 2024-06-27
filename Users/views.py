import os
from django import forms
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import re


from enterprise.models import Enterprise
from django.utils import timezone
import requests
from recruit.models import *

from utils.token import create_token
from .models import *


class RegisterForm(forms.Form):
    userName = forms.CharField(label="用户名", max_length=128, widget=forms.TextInput())
    password1 = forms.CharField(
        label="密码", max_length=128, widget=forms.PasswordInput()
    )
    password2 = forms.CharField(
        label="确认密码", max_length=128, widget=forms.PasswordInput()
    )
    email = forms.EmailField(label="个人邮箱", widget=forms.EmailInput())


class LoginForm(forms.Form):
    userName = forms.CharField(label="用户名", max_length=128, widget=forms.TextInput())
    password = forms.CharField(
        label="密码", max_length=128, widget=forms.PasswordInput()
    )


@csrf_exempt
def register(request):
    if request.method == "POST":
        register_form = RegisterForm(request.POST)
        # if register_form.is_valid():
        print(register_form)
        username = register_form.cleaned_data.get("userName")
        password1 = register_form.cleaned_data.get("password1")
        password2 = register_form.cleaned_data.get("password2")
        email = register_form.cleaned_data.get("email")

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
        print(type(password1))
        if not re.match("^(?![0-9]+$)(?![a-zA-Z]+$)[0-9A-Za-z]{8,18}$", password1):
            return JsonResponse({"error": 4004, "msg": "密码不符合规范"})

        new_user = Applicant()
        new_user.user_name = username
        new_user.password = password1
        new_user.email = email
        new_user.save()

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

        # else:
        #     return JsonResponse({'error': 3001, 'msg': '表单信息验证失败'})

    else:
        return JsonResponse({"error": 2001, "msg": "请求方式错误"})


@csrf_exempt
def login(request):
    if request.method == "POST":
        login_form = LoginForm(request.POST)
        print("111")
        print(login_form)
        if login_form.is_valid():
            username = login_form.cleaned_data.get("userName")
            password = login_form.cleaned_data.get("password")
            print(username)
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
            return JsonResponse({"error": 3001, "msg": "表单信息验证失败"})

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
                "results": results,
                "interests": interests,
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
        # 如果在某个企业中，则该企业删除该员工
        if user.enterprise_id != 0:
            # TODO
            enterprise = 0

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

        return JsonResponse({"error": 0, "msg": "查询成功", "results": results})

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

        return JsonResponse(
            {"status": "success", "message": "File uploaded successfully"}
        )
    else:
        return JsonResponse({"status": "fail", "message": "File upload failed"})


@csrf_exempt
def download_pdf(request):
    user_id = request.POST.get("userId")
    user_temp = Applicant.objects.get(id=user_id)
    if user_temp.note:
        file_path = user_temp.note.path
        print(file_path)
        if os.path.exists(file_path):
            with open(file_path, "rb") as file:
                response = HttpResponse(file.read(), content_type="application/pdf")
                response["Content-Disposition"] = (
                    f'attachment; filename="{os.path.basename(file_path)}"'
                )
                return response
        else:
            return JsonResponse({"status": "fail", "message": "File does not exist"})
    else:
        return JsonResponse(
            {"status": "fail", "message": "No file uploaded for this user"}
        )


@csrf_exempt
def update_user_interest(request):
    if request.method == "POST":
        user_id = request.POST.get("userId")
        interests = request.POST.get("interests")
        interests = json.loads(interests)
        Position.objects.filter(user_id=user_id).delete()
        for recruit_name in interests:
            Position.objects.create(user_id=user_id, recruit_name=recruit_name)
        return JsonResponse({"error": 0, "msg": "更新成功"})

    else:
        return JsonResponse({"error": 2001, "msg": "请求方式错误"})
