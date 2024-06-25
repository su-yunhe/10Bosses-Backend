from django.views.decorators.csrf import csrf_exempt
import base64
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Enterprise
from io import BytesIO
from PIL import Image
import json
from Users.models import Applicant


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


