from django.views.decorators.csrf import csrf_exempt
import base64
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from enterprise.models import Enterprise
from io import BytesIO
from PIL import Image
import json
from Users.models import Applicant
from recruit.models import Recruit,Material

@csrf_exempt
def publish_recruitment(request):
    if request.method == "POST":
        # 获取请求内容
        user_id = request.data.get('user_id')
        post = request.data.get('name')
        profile = request.data.get('profile')
        number = request.data.get('number')
        education = request.data.get('education')
        # 获取实体
        if not Applicant.objects.filter(id=user_id).exists():
             return JsonResponse({'errno': 7002, 'msg': "该用户不存在"})
        user = Applicant.objects.get(id=user_id)
        # 如果用户不是管理员判断
        if user.manage_enterprise_id == 0:
            return JsonResponse({'errno': 7004, 'msg': "该用户非管理员"})
        enterprise = Enterprise.objects.get(id=user.manage_enterprise_id)
        # 创建实体
        recruit = Recruit.objects.create(enterprise=enterprise, post=post, profile=profile, number=number, education=education)
        return JsonResponse({'error': 0, 'msg': '发布成功'})

    return JsonResponse({"error": 8001, "msg": "请求方式错误"})


@csrf_exempt
def show_recruitment(request):
    if request.method == "POST":
        # 获取请求内容
        recruit_id = request.data.get('recruit_id')
        # 获取实体
        if not Recruit.objects.filter(id=recruit_id).exists():
            return JsonResponse({'errno': 8003, 'msg': "该招聘不存在"})
        recruit = Recruit.objects.get(id=recruit_id)
        # 返回信息
        data = {"enterprise_id": recruit.enterprise.id, "enterprise_name": recruit.enterprise.name,
                "enterprise_manager_id": recruit.enterprise.manager.id, "enterprise_manager_name": recruit.enterprise.manager.real_name,
                "recruit_id": recruit.id, "recruit_post": recruit.post, "recruit_profile": recruit.profile,
                "recruit_number": recruit.number, "recruit_release_time": recruit.release_time, "recruit_education": recruit.education}
        return JsonResponse({'error': 0, 'data': data})

    return JsonResponse({"error": 8001, "msg": "请求方式错误"})


@csrf_exempt
def update_recruitmrnt(request):
    if request.method == "POST":
        # 获取请求内容
        user_id = request.data.get('user_id')
        recruit_id = request.data.get('recruit_id')
        post = request.data.get('name')
        profile = request.data.get('profile')
        number = request.data.get('number')
        education = request.data.get('education')
        # 获取实体
        if not Applicant.objects.filter(id=user_id).exists():
             return JsonResponse({'errno': 7002, 'msg': "该用户不存在"})
        if not Recruit.objects.filter(id=recruit_id).exists():
            return JsonResponse({'errno': 8003, 'msg': "该招募不存在"})
        user = Applicant.objects.get(id=user_id)
        recruit = Recruit.objects.get(id=recruit_id)
        # 如果用户不是管理员判断
        if user.manage_enterprise_id != recruit.enterprise.id:
            return JsonResponse({'errno': 7004, 'msg': "该用户非该公司管理员"})
        # 修改招募
        recruit.post = post
        recruit.profile = profile
        recruit.number = number
        recruit.education = education
        recruit.save()
        return JsonResponse({'error': 0, 'msg': '修改成功'})

    return JsonResponse({"error": 8001, "msg": "请求方式错误"})


@csrf_exempt
def show_material(request):
    if request.method == "POST":
        # 获取请求内容
        user_id = request.data.get('user_id')
        recruit_id = request.data.get('recruit_id')
        type = request.data.get('type')   # 4 返回全部 3 待审核 2 已通过 1 已录用 0 未通过
        # 获取实体
        if not Applicant.objects.filter(id=user_id).exists():
             return JsonResponse({'errno': 7002, 'msg': "该用户不存在"})
        if not Recruit.objects.filter(id=recruit_id).exists():
            return JsonResponse({'errno': 8003, 'msg': "该招募不存在"})
        user = Applicant.objects.get(id=user_id)
        recruit = Recruit.objects.get(id=recruit_id)
        # 验证用户管理员身份
        if user.manage_enterprise_id != recruit.enterprise.id:
            return JsonResponse({'errno': 7004, 'msg': "该用户非该公司管理员"})
        # 返回列表
        materials = recruit.user_material.all()
        ma_info = []
        if type == '5':
            for ma in materials:
                ma_info.append(ma.to_json())
        else:
            for ma in materials:
                if ma.status == type:
                    ma_info.append(ma.to_json())
        return JsonResponse({'error': 0, 'data': ma_info})

    return JsonResponse({"error": 2001, "msg": "请求方式错误"})


def show_material_single(request):
    if request.method == "POST":
        # 获取请求内容
        user_id = request.data.get('user_id')
        material_id = request.data.get('material_id')
        # 获取实体
        if not Applicant.objects.filter(id=user_id).exists():
             return JsonResponse({'errno': 7002, 'msg': "该用户不存在"})
        if not Material.objects.filter(id=material_id).exists():
            return JsonResponse({'errno': 8003, 'msg': "该材料不存在"})
        user = Applicant.objects.get(id=user_id)
        material = Material.objects.get(id=material_id)
        # 验证管理员身份
        if user.manage_enterprise_id != material.recruit.enterprise.id:
            return JsonResponse({'errno': 7004, 'msg': "该用户非该公司管理员"})
        # 返回信息
        return JsonResponse({'error': 0, 'data': material.to_json()})

    return JsonResponse({"error": 2001, "msg": "请求方式错误"})
