from django.views.decorators.csrf import csrf_exempt
import base64
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from enterprise.models import Enterprise
from io import BytesIO
from PIL import Image
import json
from Users.models import Applicant
from recruit.models import Recruit, Material

@csrf_exempt
def publish_recruitment(request):
    if request.method == "POST":
        # 获取请求内容
        user_id = request.POST.get('user_id')
        post = request.POST.get('post')
        profile = request.POST.get('profile')
        number = request.POST.get('number')
        education = request.POST.get('education')
        salary_low = request.POST.get('salary_low')
        salary_high = request.POST.get('salary_high')
        # 获取实体
        if not Applicant.objects.filter(id=user_id).exists():
             return JsonResponse({'error': 8002, 'msg': "操作用户不存在"})
        user = Applicant.objects.get(id=user_id)
        # 如果用户不是管理员判断
        if user.manage_enterprise_id == 0:
            return JsonResponse({'error': 8003, 'msg': "操作用户非管理员"})
        if not Enterprise.objects.filter(id=user.manage_enterprise_id).exists():
            return JsonResponse({'error': 8004, 'msg': "操作企业不存在"})
        enterprise = Enterprise.objects.get(id=user.manage_enterprise_id)
        if int(salary_low) > int(salary_high) or int(salary_low) < 0:
            return JsonResponse({'error': 8005, 'msg': "薪资设置错误"})
        if int(number) <= 0:
            return JsonResponse({'error': 8007, 'msg': "需求人数设置错误"})
        # 创建实体
        recruit = Recruit.objects.create(enterprise=enterprise, post=post, profile=profile, number=number, education=education, salary_low=salary_low, salary_high=salary_high)
        enterprise.recruitment.add(recruit)
        return JsonResponse({'error': 0, 'msg': recruit.id})

    return JsonResponse({"error": 8001, "msg": "请求方式错误"})


@csrf_exempt
def show_recruitment(request):
    if request.method == "GET":
        # 获取请求内容
        recruit_id = request.GET.get('recruit_id')
        # 获取实体
        if not Recruit.objects.filter(id=recruit_id).exists():
            return JsonResponse({'error': 8006, 'msg': "操作招聘不存在"})
        recruit = Recruit.objects.get(id=recruit_id)
        # 返回信息
        data = {"enterprise_id": recruit.enterprise.id, "enterprise_name": recruit.enterprise.name,
                "enterprise_manager_id": recruit.enterprise.manager.id, "enterprise_manager_name": recruit.enterprise.manager.user_name,
                "recruit_id": recruit.id, "recruit_post": recruit.post, "recruit_profile": recruit.profile, "recruit_status": recruit.status,
                "recruit_number": recruit.number, "recruit_release_time": recruit.release_time, "recruit_education": recruit.education,
                "salary_low": recruit.salary_low, "salary_high": recruit.salary_high, "address": recruit.enterprise.address}
        return JsonResponse({'error': 0, 'data': data})

    return JsonResponse({"error": 8001, "msg": "请求方式错误"})


@csrf_exempt
def update_recruitmrnt(request):
    if request.method == "POST":
        # 获取请求内容
        user_id = request.POST.get('user_id')
        recruit_id = request.POST.get('recruit_id')
        post = request.POST.get('post', None)
        profile = request.POST.get('profile', None)
        number = request.POST.get('number', None)
        education = request.POST.get('education', None)
        salary_low = request.POST.get('salary_low', None)
        salary_high = request.POST.get('salary_high', None)
        # 获取实体
        if not Applicant.objects.filter(id=user_id).exists():
             return JsonResponse({'error': 8002, 'msg': "操作用户不存在"})
        if not Recruit.objects.filter(id=recruit_id).exists():
            return JsonResponse({'error': 8006, 'msg': "操作招聘不存在"})
        user = Applicant.objects.get(id=user_id)
        recruit = Recruit.objects.get(id=recruit_id)
        # 如果用户不是管理员判断
        if user.manage_enterprise_id != recruit.enterprise.id:
            return JsonResponse({'error': 8003, 'msg': "操作用户非管理员"})
        # 修改招募
        if post:
            recruit.post = post
        if profile:
            recruit.profile = profile
        if number:
            if int(number) < 0:
                return JsonResponse({'error': 8007, 'msg': "需求人数设置错误"})
            recruit.number = number
            if int(number) == 0:
                recruit.status = False
        if education:
            recruit.education = education
        if salary_high and salary_low:
            if int(salary_low) > int(salary_high) or int(salary_low) < 0:
                return JsonResponse({'error': 8005, 'msg': "薪资设置错误"})
            recruit.salary_low = salary_low
            recruit.salary_high = salary_high
        elif salary_low:
            if int(salary_low) > int(recruit.salary_high) or int(salary_low) < 0:
                return JsonResponse({'error': 8005, 'msg': "薪资设置错误"})
            recruit.salary_low = salary_low
        elif salary_high:
            if int(recruit.salary_low) > int(salary_high):
                return JsonResponse({'error': 8005, 'msg': "薪资设置错误"})
            recruit.salary_high = salary_high
        recruit.save()
        return JsonResponse({'error': 0, 'msg': '修改成功'})

    return JsonResponse({"error": 8001, "msg": "请求方式错误"})


@csrf_exempt
def show_material(request):
    if request.method == "POST":
        # 获取请求内容
        user_id = request.POST.get('user_id')
        recruit_id = request.POST.get('recruit_id')
        type = request.POST.get('type')   # 4 返回全部 3 待审核 2 已通过 1 已录用 0 未通过
        # 获取实体
        if not Applicant.objects.filter(id=user_id).exists():
             return JsonResponse({'error': 7002, 'msg': "该用户不存在"})
        if not Recruit.objects.filter(id=recruit_id).exists():
            return JsonResponse({'error': 8003, 'msg': "该招募不存在"})
        user = Applicant.objects.get(id=user_id)
        recruit = Recruit.objects.get(id=recruit_id)
        # 验证用户管理员身份
        if user.manage_enterprise_id != recruit.enterprise.id:
            return JsonResponse({'error': 7004, 'msg': "该用户非该公司管理员"})
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
        user_id = request.POST.get('user_id')
        material_id = request.POST.get('material_id')
        # 获取实体
        if not Applicant.objects.filter(id=user_id).exists():
             return JsonResponse({'error': 7002, 'msg': "该用户不存在"})
        if not Material.objects.filter(id=material_id).exists():
            return JsonResponse({'error': 8003, 'msg': "该材料不存在"})
        user = Applicant.objects.get(id=user_id)
        material = Material.objects.get(id=material_id)
        # 验证管理员身份
        if user.manage_enterprise_id != material.recruit.enterprise.id:
            return JsonResponse({'error': 7004, 'msg': "该用户非该公司管理员"})
        # 返回信息
        return JsonResponse({'error': 0, 'data': material.to_json()})

    return JsonResponse({"error": 2001, "msg": "请求方式错误"})
