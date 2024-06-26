import jieba
from django.views.decorators.csrf import csrf_exempt
import base64
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from enterprise.models import Enterprise
from io import BytesIO
from PIL import Image
import json
from Users.models import Applicant, Position
from recruit.models import Recruit, Material


@csrf_exempt
def publish_recruitment(request):
    if request.method == "POST":
        # 获取请求内容
        user_id = request.POST.get('user_id')
        post = request.POST.get('post')
        profile = request.POST.get('profile')
        number = request.POST.get('number')
        education = request.POST.get('education', None)
        salary_low = request.POST.get('salary_low', None)
        salary_high = request.POST.get('salary_high', None)
        address = request.POST.get('address', None)
        experience = request.POST.get('experience', None)
        requirement = request.POST.get('requirement', None)
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
        if int(number) <= 0:
            return JsonResponse({'error': 8007, 'msg': "需求人数设置错误"})
        if salary_high and salary_low:
            if int(salary_low) > int(salary_high) or int(salary_low) < 0:
                return JsonResponse({'error': 8005, 'msg': "薪资设置错误"})
        elif salary_low:
            if int(salary_low) < 0:
                return JsonResponse({'error': 8005, 'msg': "薪资设置错误"})
        elif salary_high:
            if int(salary_high) < 0:
                return JsonResponse({'error': 8005, 'msg': "薪资设置错误"})
        # 创建实体
        recruit = Recruit.objects.create(enterprise=enterprise, post=post, profile=profile, number=number)
        if address:
            recruit.address = address
        else:
            recruit.address = recruit.enterprise.address
        if experience:
            recruit.experience = experience
        if requirement:
            recruit.requirement = requirement
        if education:
            recruit.education = education
        if salary_high and salary_low:
            recruit.salary_low = salary_low
            recruit.salary_high = salary_high
        elif salary_low:
            recruit.salary_low = salary_low
            recruit.salary_high = salary_low
        elif salary_high:
            recruit.salary_high = salary_high
        recruit.save()
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
                "salary_low": recruit.salary_low, "salary_high": recruit.salary_high, "address": recruit.address, "experience": recruit.experience, "requirement": recruit.requirement}
        return JsonResponse({'error': 0, 'data': data})

    return JsonResponse({"error": 8001, "msg": "请求方式错误"})


@csrf_exempt
def update_recruitment(request):
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
        address = request.POST.get('address', None)
        experience = request.POST.get('experience', None)
        requirement = request.POST.get('requirement', None)

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
        if experience:
            recruit.experience = experience
        if requirement:
            recruit.requirement = requirement
        if address:
            recruit.address = address
        recruit.save()
        return JsonResponse({'error': 0, 'msg': '修改成功'})

    return JsonResponse({"error": 8001, "msg": "请求方式错误"})


@csrf_exempt
def user_apply_recruit(request):
    if request.method == "POST":
        # 获取请求内容
        user_id = request.POST.get('user_id')
        recruit_id = request.POST.get('recruit_id')
        curriculum_vitae = request.FILE.get('curriculum_vitae', None)
        certificate = request.FILE.get('certificate', None)
        # 获取实体
        if not Applicant.objects.filter(id=user_id).exists():
            return JsonResponse({'error': 7002, 'msg': "操作用户不存在"})
        if not Recruit.objects.filter(id=recruit_id).exists():
            return JsonResponse({'error': 8003, 'msg': "操作招募不存在"})
        user = Applicant.objects.get(id=user_id)
        recruit = Recruit.objects.get(id=recruit_id)
        enterprise = Enterprise.objects.get(id=recruit.enterprise.id)
        # 验证用户管理员身份
        if user.manage_enterprise_id != 0:
            return JsonResponse({'error': 7004, 'msg': "操作用户是管理员"})
        # 返回列表
        material = Material.objects.create(recruit=recruit, user=user)
        if curriculum_vitae:
            material.curriculum_vitae = curriculum_vitae
        else:
            material.curriculum_vitae = user.note
        if certificate:
            material.certificate = certificate
        # else:
        #     material.certificate = user.information.certificate
        recruit.user_material.add(material)
        enterprise.recruit_material.add(material)
        material.save()
        return JsonResponse({'error': 0, 'mag': material.id})

    return JsonResponse({"error": 2001, "msg": "请求方式错误"})


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


@csrf_exempt
def recruitment_search(request):
    if request.method == "POST":
        query = (request.POST.get('q', ''))
        if query:
            # jieba拆分搜索关键字
            search_list = jieba.cut_for_search(query)
            search_results = set()  # 使用Set防止重复
            for search_name in search_list:
                if not search_name.strip():  # 跳过空字符串
                    continue
                # 进行模糊搜索
                # 调用whoosh引擎进行搜索
                # sqs = SearchQuerySet().filter(content=search_name)
                # for result in sqs:
                #     search_results.add(result.object.id)

                # 直接使用数据库模糊匹配
                results = Recruit.objects.filter(post__icontains=search_name)
                for recruitment in results:
                    search_results.add(recruitment.id)
            recruitments = list()
            for recruitment_id in search_results:
                recruitment = Recruit.objects.values().get(id=recruitment_id)
                rec_enter_id = recruitment["enterprise_id"]
                enterprise_name = Enterprise.objects.get(id=rec_enter_id).name
                recruitment["enterprise_name"] = enterprise_name
                recruitments.append(recruitment)
            return JsonResponse({'results': recruitments}, status=200)
        else:
            # 用户没有提供关键词
            recruitments = list(Recruit.objects.values().all())
            for recruitment in recruitments:
                rec_enter_id = recruitment["enterprise_id"]
                enterprise_name = Enterprise.objects.get(id=rec_enter_id).name
                recruitment["enterprise_name"] = enterprise_name
            return JsonResponse({'results': recruitments}, status=200)
    return JsonResponse({"error": 2001, "msg": "请求方式错误"})


@csrf_exempt
def get_intended_recruitment(request):
    # 获取用户感兴趣的招聘信息
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        if not Applicant.objects.filter(id=user_id).exists():
            return JsonResponse({'errno': 7002, 'msg': "该用户不存在"})
        # 用户存在 获取意向岗位
        position_list = list(Position.objects.filter(user_id=user_id))
        if not position_list:
            # 该用户还没有填写意向岗位
            return JsonResponse({'errno': 1001, 'msg': "用户还没有填写意向岗位"})
        results = list()
        for position in position_list:
            recruitment_list = list(Recruit.objects.values().filter(post=position.recruit_name))
            for recruitment in recruitment_list:
                rec_enter_id = recruitment["enterprise_id"]
                enterprise_name = Enterprise.objects.get(id=rec_enter_id).name
                recruitment["enterprise_name"] = enterprise_name
                results.append(recruitment)
        if results:
            return JsonResponse({"errno": 0, "msg": "获取用户意向岗位的招聘信息成功", "data": results})
        else:
            # 还没有企业在这些岗位招聘
            return JsonResponse({"errno": 1002, "msg": "当前还没有这些岗位的招聘信息"})
    return JsonResponse({"errno": 2001, "msg": "请求方式错误"})
