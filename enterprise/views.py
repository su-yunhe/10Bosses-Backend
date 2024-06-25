import jieba
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from .models import Enterprise
from recruit.models import Recruit
from haystack.forms import ModelSearchForm
from haystack.query import EmptySearchQuerySet, SearchQuerySet

import base64
from django.shortcuts import get_object_or_404
from io import BytesIO
from PIL import Image
import json
from Users.models import Applicant


@csrf_exempt
def search_enterprise(request):
    if request.method == 'POST':
        query = (request.POST.get('q', ''))  # 从POST请求中获取查询参数
        if query:
            search_list = jieba.cut_for_search(query)
            search_results = set()
            for search_name in search_list:
                if not search_name.strip():  # 跳过空字符串
                    continue
                # 进行模糊搜索
                results = Enterprise.objects.filter(name__icontains=search_name)
                for enterprise in results:
                    search_results.add(enterprise.id)
            print(search_results)
            results = list()
            for enterprise_id in search_results:
                enterprise = Enterprise.objects.values().get(id=enterprise_id)
                # 通过企业管理员id获取其真实姓名
                manager_id = Enterprise.objects.get(id=enterprise_id).manager_id
                manager_name = Applicant.objects.get(id=manager_id).user_name
                # 修改字段
                enterprise["manager_name"] = manager_name
                del enterprise["manager_id"]
                # 获取企业招聘列表
                recruitments = list(Recruit.objects.values().filter(enterprise_id=enterprise_id))
                print(recruitments)
                results.append({"enterprise": enterprise, "recruitment": recruitments})

            return JsonResponse({'results': results}, status=200)
        else:
            # 用户没有提供关键词,只返回一些招聘
            recruitments = list(Recruit.objects.values().all())
            print(recruitments)
            return JsonResponse({'results': recruitments}, status=200)
    return JsonResponse({"errno": 2001, "msg": "请求方式错误"})


@csrf_exempt
def get_enterprise_recruitment(request):
    # 获取企业招聘信息
    if request.method == 'POST':
        enterprise_id = request.POST.get('enterprise_id')
        print(enterprise_id)
        recruitment_list = list(Recruit.objects.values().filter(enterprise_id=enterprise_id))
        return JsonResponse({"errno": 0, "msg": "获取企业招聘信息成功", "data": recruitment_list})
    return JsonResponse({"errno": 2001, "msg": "请求方式错误"})

@csrf_exempt
def get_intended_recruitment(request):
    # 获取用户感兴趣的招聘信息
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        if not Applicant.objects.filter(id=user_id).exists():
            return JsonResponse({'errno': 7002, 'msg': "该用户不存在"})
        # 用户存在 获取意向岗位
        user_intended_position = Applicant.objects.get(id=user_id).interests
        recruitment_list = list(Recruit.objects.values().filter(post=user_intended_position))
        return JsonResponse({"errno": 0, "msg": "获取用户意向岗位的招聘信息成功", "data": recruitment_list})
    return JsonResponse({"errno": 2001, "msg": "请求方式错误"})

@csrf_exempt
def creat_enterprise(request):
    if request.method == "POST":
        # 获取请求内容
        user_id = request.data.get('user_id')
        name = request.data.get('name')
        profile = request.data.get('profile')
        picture = request.FILES['picture']
        address = request.data.get('address')
        # 获取实体
        if not Applicant.objects.filter(id=user_id).exists():
            return JsonResponse({'errno': 7002, 'msg': "该用户不存在"})
        user = Applicant.objects.get(id=user_id)
        if user.manage_enterprise_id != 0 or user.enterprise_id != 0:
            return JsonResponse({'errno': 7004, 'msg': "该用户非管理员"})
        # 创建实体
        enterprise = Enterprise.objects.create(name=name, profile=profile, picture=picture, address=address)
        user.manage_enterprise_id = enterprise.id
        user.enterprise_id = enterprise.id
        user.save()
        return JsonResponse({'error': 0, 'msg': '创建成功'})

    return JsonResponse({"error": 7001, "msg": "请求方式错误"})


@csrf_exempt
def show_enterprise(request):
    if request.method == "POST":
        # 获取请求内容
        enterprise_id = request.data.get('enterprise_id')
        # 获取实体
        if not Enterprise.objects.filter(id=enterprise_id).exists():
            return JsonResponse({'errno': 7003, 'msg': "该公司不存在"})
        enterprise = Enterprise.objects.get(id=enterprise_id)
        # 返回信息
        data = {"name": enterprise.name, "profile": enterprise.profile,
                "picture": enterprise_picture_base64(enterprise.picture),
                "address": enterprise.address, "manager_id": enterprise.manager.id,
                "manager_name": enterprise.manager.user_name, "manager_email": enterprise.manager.email}
        return JsonResponse({'error': 0, 'data': data})

    return JsonResponse({"error": 7001, "msg": "请求方式错误"})


@csrf_exempt
def update_enterprise(request):
    if request.method == "POST":
        # 获取请求内容
        user_id = request.data.get('user_id')
        user_be_manager_id = request.data.get('user_be_manager_id')
        name = request.data.get('name')
        profile = request.data.get('profile')
        picture = request.FILES['picture']
        address = request.data.get('address')
        # 获取实体
        if not Applicant.objects.filter(id=user_id).exists():
            return JsonResponse({'errno': 7002, 'msg': "该用户不存在"})
        if not Applicant.objects.filter(id=user_be_manager_id).exists():
            return JsonResponse({'errno': 7005, 'msg': "目标用户不存在"})
        user = Applicant.objects.get(id=user_id)
        user_be_manager = Applicant.objects.get(id=user_be_manager_id)
        # 如果用户不是管理员判断
        if user.manage_enterprise_id == 0:
            return JsonResponse({'errno': 7004, 'msg': "该用户非管理员"})
        enterprise = Enterprise.objects.get(id=user.manage_enterprise_id)
        # 修改实体
        enterprise.name = name
        enterprise.profile = profile
        enterprise.picture = picture
        enterprise.address = address
        enterprise.manager = user_be_manager
        enterprise.save()
        return JsonResponse({'error': 0, 'msg': '修改成功'})

    return JsonResponse({"error": 7001, "msg": "请求方式错误"})


@csrf_exempt
def delete_enterprise(request):
    if request.method == "POST":
        # 获取请求内容
        user_id = request.data.get('user_id')
        # 获取实体
        if not Applicant.objects.filter(id=user_id).exists():
            return JsonResponse({'errno': 7002, 'msg': "该用户不存在"})
        user = Applicant.objects.get(id=user_id)
        # 如果用户不是管理员判断
        if user.manage_enterprise_id == 0:
            return JsonResponse({'errno': 7004, 'msg': "该用户非管理员"})
        enterprise = Enterprise.objects.get(id=user.manage_enterprise_id)
        # 执行删除
        users = enterprise.member.all()
        for u in users:
            u.enterprise_id = 0
            u.save()
        user.manage_enterprise_id = 0
        user.enterprise_id = 0
        enterprise.delete()
        user.save()
        return JsonResponse({'error': 0, 'msg': '删除成功'})

    return JsonResponse({"error": 7001, "msg": "请求方式错误"})

#
# @csrf_exempt
# def show_enterprise_member(request):
#     if request.method == "POST":
#         # 获取请求内容
#         enterprise_id = request.data.get('enterprise_id')
#         # 获取实体
#         if not Enterprise.objects.filter(id=enterprise_id).exists():
#             return JsonResponse({'errno': 7003, 'msg': "该公司不存在"})
#         members = Enterprise.objects.get(id=enterprise_id).member.all()
#
#         # 返回信息
#
#         return JsonResponse({'error': 0, 'data': data})
#
#     return JsonResponse({"error": 7001, "msg": "请求方式错误"})

#
# @csrf_exempt
# def manage_enterprise_member(request):
#     if request.method == "POST":
#         # 获取请求内容
#         enterprise_id = request.data.get('enterprise_id')
#         # 获取实体
#         if not Enterprise.objects.filter(id=enterprise_id).exists():
#             return JsonResponse({'errno': 7003, 'msg': "该公司不存在"})
#         enterprise = Enterprise.objects.get(id=enterprise_id)
#         # 返回信息
#         data = {"name": enterprise.name, "profile": enterprise.profile,
#                 "picture": enterprise_picture_base64(enterprise.picture),
#                 "address": enterprise.address}
#         return JsonResponse({'error': 0, 'data': data})
#
#     return JsonResponse({"error": 7001, "msg": "请求方式错误"})


def enterprise_picture_base64(request, picture):
    image = Image.open(picture)
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    image_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
    return image_base64


def to_json_member(member):
    info = {
        "user_id": member

    }
    return json.dumps(info)



















# def get_enterprise_picture_url(request, enterprise_id):
#     enterprise = get_object_or_404(Enterprise, id=enterprise_id)
#     picture_url = enterprise.picture.url if enterprise.picture else None
#     return JsonResponse({'picture_url': picture_url})

