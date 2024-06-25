from django.shortcuts import render
from ast import List
import json
from django import forms
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import re

from django.utils import timezone
import requests
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

        if not results:  # 如果查询结果为空
            return JsonResponse({"error": 1001, "msg": "查无此人"})

        return JsonResponse({"error": 0, "msg": "获取用户信息成功", "results": results})
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
        new_position.save()
        return JsonResponse({"error": 0, "msg": "建立项目成功"})
    else:
        return JsonResponse({"error": 2001, "msg": "请求方式错误"})
