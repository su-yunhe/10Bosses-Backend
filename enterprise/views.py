import os
import jieba
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from recruit.views import refresh_recruits
from .models import Enterprise, UserInformationEnterprise
from recruit.models import Recruit
from haystack.query import SearchQuerySet
from ScholarSHIP import settings
from datetime import date

import base64
from django.shortcuts import get_object_or_404
from io import BytesIO
from PIL import Image
import json
from Users.models import Applicant, Position
from recruit.models import Material, Recruit


@csrf_exempt
def enterprise_search(request):
    if request.method == 'POST':
        query = (request.POST.get('q', ''))  # 从POST请求中获取查询参数
        if query:
            # jieba拆分搜索关键字
            search_list = jieba.cut_for_search(query)
            search_results = set()
            for search_name in search_list:
                if not search_name.strip():  # 跳过空字符串
                    continue
                print(search_name)
                # 进行模糊搜索
                # 调用whoosh引擎进行搜索，暂时不使用
                # sqs = SearchQuerySet().filter(content=search_name)
                # for result in sqs:
                #     search_results.add(result.object.id)

                # 直接使用数据库模糊匹配
                results = Enterprise.objects.filter(name__icontains=search_name)
                for enterprise in results:
                    search_results.add(enterprise.id)
            results = list()
            for enterprise_id in search_results:
                enterprise = Enterprise.objects.values().get(id=enterprise_id)
                # 通过企业管理员id获取其真实姓名
                manager_id = Enterprise.objects.get(id=enterprise_id).manager_id
                if not manager_id:
                    manager_name = "暂无管理员"
                else:
                    manager_name = Applicant.objects.get(id=manager_id).user_name
                # 修改字段
                enterprise["manager_name"] = manager_name
                del enterprise["manager_id"]
                # 获取企业招聘列表
                recruitments = list(Recruit.objects.values().filter(enterprise_id=enterprise_id))
                for recruitment in recruitments:
                    rec_enter_id = recruitment["enterprise_id"]
                    enterprise_name = Enterprise.objects.get(id=rec_enter_id).name
                    recruitment["enterprise_name"] = enterprise_name
                results.append({"enterprise": enterprise, "recruitment": recruitments})
            return JsonResponse(
                {
                    "error": 0,
                    "msg": "企业搜索成功",
                    "data": {
                        "results": results
                    }
                })
        else:
            # 用户没有提供关键词,返回所有企业
            enterprise_list = list(Enterprise.objects.values().all())
            results = list()
            for enterprise in enterprise_list:
                # 通过企业管理员id获取其真实姓名
                manager_id = enterprise["manager_id"]
                manager_name = Applicant.objects.get(id=manager_id).user_name
                # 修改字段
                enterprise["manager_name"] = manager_name
                del enterprise["manager_id"]
                # 获取企业招聘列表
                recruitments = list(Recruit.objects.values().filter(enterprise_id=enterprise["id"]))
                for recruitment in recruitments:
                    rec_enter_id = recruitment["enterprise_id"]
                    enterprise_name = Enterprise.objects.get(id=rec_enter_id).name
                    recruitment["enterprise_name"] = enterprise_name
                # print(recruitments)
                results.append({"enterprise": enterprise, "recruitment": recruitments})
            return JsonResponse(
                {
                    "error": 0,
                    "msg": "关键词为空，返回所有企业",
                    "data": {
                        "results": results
                    }
                })
    return JsonResponse({"error": 2001, "msg": "请求方式错误"})


@csrf_exempt
def whoosh_search(request):  # 测试，实际没有被调用过
    query = request.POST.get('q', '')
    sqs = SearchQuerySet().filter(content=query)
    search_results = list()
    for result in sqs:
        search_results.append(result.object.id)
    print(search_results)
    results = [{'name': result.object.name} for result in sqs]
    return JsonResponse(results, safe=False)


@csrf_exempt
def get_enterprise_recruitment(request):
    # 获取企业招聘信息
    if request.method == 'POST':
        enterprise_id = request.POST.get('enterprise_id')
        print(enterprise_id)
        recruitment_list = list(Recruit.objects.values().filter(enterprise_id=enterprise_id))
        for recruitment in recruitment_list:
            rec_enter_id = recruitment["enterprise_id"]
            enterprise_name = Enterprise.objects.get(id=rec_enter_id).name
            recruitment["enterprise_name"] = enterprise_name
        return JsonResponse(
            {
                "error": 0,
                "msg": "获取企业招聘信息成功",
                "data": {
                    "results": recruitment_list
                }
            })
    return JsonResponse({"error": 2001, "msg": "请求方式错误"})


@csrf_exempt
def recommend_enterprise(request):
    # 根据用户意向岗位推荐企业供用户关注（只在用户填写意向后调用）
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        if not Applicant.objects.filter(id=user_id).exists():
            return JsonResponse({'error': 7002, 'msg': "该用户不存在"})
        # 用户存在 获取意向岗位
        position_list = list(Position.objects.filter(user_id=user_id))
        if not position_list:
            # 该用户还没有填写意向岗位
            return JsonResponse({'error': 1001, 'msg': "用户还没有填写意向岗位"})
        enterprise_id_set = set()
        for position in position_list:
            recruitment_list = list(Recruit.objects.values().filter(post=position.recruit_name))
            for recruitment in recruitment_list:
                rec_enter_id = recruitment["enterprise_id"]
                enterprise_id_set.add(rec_enter_id)
        results = list()
        for ent_id in enterprise_id_set:
            enterprise = Enterprise.objects.values().get(id=ent_id)
            results.append(enterprise)
        if results:
            return JsonResponse(
                {
                    "error": 0,
                    "msg": "获取用户意向岗位的企业成功",
                    "data": {
                        "results": results
                    }
                })
        return JsonResponse(
            {
                "error": 0,
                "msg": "当前还没有企业招聘这些岗位的员工",
                "data": {}
            })
    return JsonResponse({"error": 2001, "msg": "请求方式错误"})


@csrf_exempt
def recommend_users(request):
    # 根据用户意向岗位推荐关注了相似领域的用户供用户关注（只在用户填写意向后调用）
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        if not Applicant.objects.filter(id=user_id).exists():
            return JsonResponse({'error': 7002, 'msg': "该用户不存在"})
        # 用户存在 获取意向岗位列表
        position_list = list(Position.objects.filter(user_id=user_id))
        if not position_list:
            # 该用户还没有填写意向岗位
            return JsonResponse(
                {
                    'error': 0,
                    'msg': "用户还没有填写意向岗位",
                    "data": {}
                })
        user_id_set = set()
        for position in position_list:
            # 获取该岗位的所有关注条目
            position_concern_list = list(Position.objects.values().filter(recruit_name=position.recruit_name))
            for position_others in position_concern_list:
                other_user_id = position_others["user_id"]
                # 去除自己后加入set，防止重复
                if str(other_user_id) != str(user_id):
                    user_id_set.add(other_user_id)
        results = list()
        for other_user_id in user_id_set:
            user = Applicant.objects.values().get(id=other_user_id)
            user_enterprise_id = user["enterprise_id"]
            user_manage_enterprise_id = user["manage_enterprise_id"]
            if user_enterprise_id:
                enterprise_name = Enterprise.objects.get(id=user_enterprise_id).name
                user["enterprise_name"] = enterprise_name
            else:
                user["enterprise_name"] = ""
            if user_manage_enterprise_id:
                enterprise_name = Enterprise.objects.get(id=user_enterprise_id).name
                user["manage_enterprise_name"] = enterprise_name
            else:
                user["manage_enterprise_name"] = ""
            results.append(user)
        if results:
            return JsonResponse(
                {
                    "error": 0,
                    "msg": "获取相同意向岗位的用户成功",
                    "data": {
                        "results": results
                    }
                })
        return JsonResponse(
            {
                "error": 0,
                "msg": "当前还没有关注这些岗位的用户",
                "data": {}
            })
    return JsonResponse({"error": 2001, "msg": "请求方式错误"})


@csrf_exempt
def create_enterprise(request):
    if request.method == "POST":
        # 获取请求内容
        user_id = request.POST.get('user_id')  # 使用request.POST，因为如果需要传图片的话要使用form-data，不能使用原来的request.data或request.body
        name = request.POST.get('name')
        profile = request.POST.get('profile')
        picture = request.FILES.get('picture', None)
        address = request.POST.get('address')
        # 获取实体
        if Enterprise.objects.filter(name=name).exists():
            return JsonResponse({'error': 7009, 'msg': "公司名重复"})
        # if not Applicant.objects.filter(id=user_id).exists():
        #     return JsonResponse({'error': 7002, 'msg': "操作用户不存在"})
        user = Applicant.objects.get(id=user_id)
        if user.enterprise_id != 0:
            return JsonResponse({'error': 7003, 'msg': "操作用户已在公司内"})
        # 创建实体
        enterprise = Enterprise.objects.create(name=name, profile=profile, address=address, manager=user)
        enterprise.member.add(user)
        if picture:
            enterprise.picture = picture
            enterprise.save()
        user.manage_enterprise_id = enterprise.id
        user.enterprise_id = enterprise.id
        information_enterprise = UserInformationEnterprise.objects.create(post="企业管理员", user=user)
        user.user_information_enterprise = information_enterprise
        user.save()
        materials = user.user_material.all()
        for ma in materials:
            ma.delete()
        return JsonResponse({'error': 0, 'data': enterprise.id})

    return JsonResponse({"error": 7001, 'msg': "请求方式错误"})


@csrf_exempt
def show_enterprise(request):
    if request.method == "GET":
        # 获取请求内容
        enterprise_id = request.GET.get('enterprise_id')
        # 获取实体
        if not Enterprise.objects.filter(id=enterprise_id).exists():
            return JsonResponse({'error': 7004, 'msg': "该公司不存在"})
        enterprise = Enterprise.objects.get(id=enterprise_id)
        # 返回信息
        data = {"name": enterprise.name, "profile": enterprise.profile,
                "picture": enterprise.picture.url,
                "address": enterprise.address, "manager_id": enterprise.manager.id,
                "manager_name": enterprise.manager.user_name, "manager_email": enterprise.manager.email}
        return JsonResponse({'error': 0, 'data': data})

    return JsonResponse({"error": 7001, "msg": "请求方式错误"})


@csrf_exempt
def update_enterprise(request):     # mark
    if request.method == "POST":
        # 获取请求内容
        user_id = request.POST.get('user_id')
        name = request.POST.get('name', None)
        profile = request.POST.get('profile', None)
        picture = request.FILES.get('picture', None)
        address = request.POST.get('address', None)
        # 获取实体
        # if not Applicant.objects.filter(id=user_id).exists():
        #     return JsonResponse({'error': 7002, 'msg': "操作用户不存在"})
        user = Applicant.objects.get(id=user_id)
        # 如果用户不是管理员判断
        if user.manage_enterprise_id == 0:
            return JsonResponse({'error': 7005, 'msg': "操作用户非管理员"})
        enterprise = Enterprise.objects.get(id=user.manage_enterprise_id)
        # 修改实体
        if name:
            if enterprise.name == name:
                return JsonResponse({'error': 7009, 'msg': "公司名重复"})
            enterprise.name = name
        if profile:
            enterprise.profile = profile
        if picture:
            if os.path.isfile(enterprise.picture.path):  # 如果图像路径不是默认图像路径，则删除图像文件
                if enterprise.picture.path != os.path.join(settings.MEDIA_ROOT, 'enterprise\default.jpg'):
                    os.remove(enterprise.picture.path)
            enterprise.picture = picture
        if address:
            enterprise.address = address
        enterprise.save()
        return JsonResponse({'error': 0, 'msg': '修改成功'})

    return JsonResponse({'error': 7001, "msg": "请求方式错误"})


@csrf_exempt
def change_manager(request):     # mark
    if request.method == "POST":
        # 获取请求内容
        user_id = request.POST.get('user_id')
        user_be_manager_id = request.POST.get('user_be_manager_id')
        # 获取实体
        # if not Applicant.objects.filter(id=user_id).exists():
        #     return JsonResponse({'error': 7002, 'msg': "操作用户不存在"})
        user = Applicant.objects.get(id=user_id)
        # 如果用户不是管理员判断
        if user.manage_enterprise_id == 0:
            return JsonResponse({'error': 7005, 'msg': "操作用户非管理员"})
        enterprise = Enterprise.objects.get(id=user.manage_enterprise_id)
        # 修改实体
        # if not Applicant.objects.filter(id=user_be_manager_id).exists():
        #     return JsonResponse({'error': 7006, 'msg': "目标用户不存在"})
        user_be_manager = Applicant.objects.get(id=user_be_manager_id)
        if user_be_manager.enterprise_id != user.manage_enterprise_id:
            return JsonResponse({'error': 7007, 'msg': "目标用户不在公司"})
        user_be_manager.manage_enterprise_id = enterprise.id
        user_be_manager.user_information_enterprise.post = "企业管理员"
        user_be_manager.user_information_enterprise.save()
        user_be_manager.save()
        user.manage_enterprise_id = 0
        user.user_information_enterprise.post = "暂无"
        user.user_information_enterprise.save()
        user.save()
        enterprise.manager = user_be_manager
        if user_be_manager in enterprise.withdraw.all():
            enterprise.withdraw.remove(user_be_manager)
        enterprise.save()
        materials = user_be_manager.user_material.all()
        for ma in materials:
            ma.delete()
        return JsonResponse({'error': 0, 'msg': '修改成功'})

    return JsonResponse({'error': 7001, "msg": "请求方式错误"})


@csrf_exempt
def delete_enterprise(request):
    if request.method == "POST":
        # 获取请求内容
        user_id = request.POST.get('user_id')
        # 获取实体
        # if not Applicant.objects.filter(id=user_id).exists():
        #     return JsonResponse({'error': 7002, 'msg': "操作用户不存在"})
        user = Applicant.objects.get(id=user_id)
        # 如果用户不是管理员判断
        if user.manage_enterprise_id == 0:
            return JsonResponse({'error': 7005, 'msg': "操作用户非管理员"})
        enterprise = Enterprise.objects.get(id=user.manage_enterprise_id)
        if os.path.isfile(enterprise.picture.path):  # 如果图像路径不是默认图像路径，则删除图像文件
            if enterprise.picture.path != os.path.join(settings.MEDIA_ROOT, 'enterprise\default.jpg'):
                os.remove(enterprise.picture.path)
        # 执行删除
        users = enterprise.member.all()
        for u in users:
            u.enterprise_id = 0
            if u.user_information_enterprise:
                u.user_information_enterprise.delete()
            u.user_information_enterprise = None
            u.save()
        user.manage_enterprise_id = 0
        user.enterprise_id = 0
        enterprise.delete()
        user.save()
        return JsonResponse({'error': 0, 'msg': '删除成功'})

    return JsonResponse({"error": 7001, "msg": "请求方式错误"})


@csrf_exempt
def show_enterprise_member(request):
    if request.method == "GET":
        # 获取请求内容
        user_id = request.GET.get('user_id')
        # 获取实体
        # if not Applicant.objects.filter(id=user_id).exists():
        #     return JsonResponse({'error': 7002, 'msg': "操作用户不存在"})
        user = Applicant.objects.get(id=user_id)
        if user.enterprise_id == 0:
            return JsonResponse({'error': 7008, 'msg': "操作用户不在公司内"})
        enterprise = Enterprise.objects.get(id=user.enterprise_id)
        members = enterprise.member.all()
        # 返回信息
        data = []
        data.append(to_json_member(enterprise.manager))
        for member in members:
            if member.manage_enterprise_id == 0:
                data.append(to_json_member(member))
        return JsonResponse({'error': 0, 'data': data})

    return JsonResponse({"error": 7001, "msg": "请求方式错误"})


@csrf_exempt
def show_recruitment_list(request):
    if request.method == "GET":
        # 获取请求内容
        enterprise_id = request.GET.get('enterprise_id')
        type = request.GET.get('type')  # True: 正在招募， False: 结束招募
        # 获取实体
        if not Enterprise.objects.filter(id=enterprise_id).exists():
            return JsonResponse({'error': 7004, 'msg': "该公司不存在"})
        enterprise = Enterprise.objects.get(id=enterprise_id)
        recruits = enterprise.recruitment.all()
        # 返回信息
        data = []
        if type == 'All':
            for recruit in recruits:
                data.append(to_json_recruit(recruit))
        else:
            for recruit in recruits:
                if str(recruit.status) == type:
                    data.append(to_json_recruit(recruit))
        return JsonResponse({'error': 0, 'data': data})

    return JsonResponse({"error": 7001, "msg": "请求方式错误"})


def show_withdraw_list(request):
    if request.method == "GET":
        # 获取请求内容
        user_id = request.GET.get('user_id')
        # 获取实体
        # if not Applicant.objects.filter(id=user_id).exists():
        #     return JsonResponse({'error': 7002, 'msg': "操作用户不存在"})
        user = Applicant.objects.get(id=user_id)
        if user.manage_enterprise_id == 0:
            return JsonResponse({'error': 7005, 'msg': "操作用户非管理员"})
        enterprise = Enterprise.objects.get(id=user.manage_enterprise_id)
        withdraws = enterprise.withdraw.all()
        # 返回信息
        data = []
        for member in withdraws:
            if member != user:
                data.append(to_json_member(member))
        return JsonResponse({'error': 0, 'data': data})

    return JsonResponse({"error": 7001, "msg": "请求方式错误"})


@csrf_exempt
def apply_withdraw(request):
    if request.method == "POST":
        # 获取请求内容
        user_id = request.POST.get('user_id')
        # 获取实体
        # if not Applicant.objects.filter(id=user_id).exists():
        #     return JsonResponse({'error': 7002, 'msg': "操作用户不存在"})
        user = Applicant.objects.get(id=user_id)
        if user.enterprise_id == 0:
            return JsonResponse({'error': 7008, 'msg': "操作用户不在公司内"})
        enterprise = Enterprise.objects.get(id=user.enterprise_id)
        # 验证用户管理员身份
        if user.manage_enterprise_id != 0:
            return JsonResponse({'error': 7010, 'msg': "操作用户是管理员"})
        enterprise.withdraw.add(user)
        return JsonResponse({'error': 0, 'msg': "提交退出申请成功"})

    return JsonResponse({"error": 7001, "msg": "请求方式错误"})


@csrf_exempt
def manage_withdraw(request):
    if request.method == "POST":
        # 获取请求内容
        user_id = request.POST.get('user_id')
        user_out_id = request.POST.get('user_out_id')
        type = request.POST.get('type')  # accept 同意， refuse 拒绝
        # 获取实体
        # if not Applicant.objects.filter(id=user_id).exists():
        #     return JsonResponse({'error': 7002, 'msg': "操作用户不存在"})
        user = Applicant.objects.get(id=user_id)
        # 如果用户不是管理员判断
        if user.manage_enterprise_id == 0:
            return JsonResponse({'error': 7005, 'msg': "操作用户非管理员"})
        enterprise = Enterprise.objects.get(id=user.manage_enterprise_id)
        # if user_id == user_out_id:
        #     return JsonResponse({'error': 7010, 'msg': "操作用户是管理员"})
        # 修改实体
        # if not Applicant.objects.filter(id=user_out_id).exists():
        #     return JsonResponse({'error': 7006, 'msg': "目标用户不存在"})
        user_out = Applicant.objects.get(id=user_out_id)
        if user_out not in enterprise.withdraw.all():
            return JsonResponse({'error': 7007, 'msg': "目标用户不在退出列表"})
        if type == "accept":
            user_out.user_information_enterprise.delete()
            user_out.user_information_enterprise = None
            user_out.enterprise_id = 0
            user_out.save()
            enterprise.member.remove(user_out)
            enterprise.withdraw.remove(user_out)
        else:
            enterprise.withdraw.remove(user_out)
        return JsonResponse({'error': 0, 'msg': "已处理"})

    return JsonResponse({"error": 7001, "msg": "请求方式错误"})


@csrf_exempt
def user_enter_enterprise(request):
    if request.method == "POST":
        # 获取请求内容
        user_id = request.POST.get('user_id')
        material_id = request.POST.get('material_id')
        type = request.POST.get('type')  # accept 用户同意进入企业，refuse 用户拒绝企业
        # 获取实体
        # if not Applicant.objects.filter(id=user_id).exists():
        #     return JsonResponse({'error': 7002, 'msg': "操作用户不存在"})
        # if not Material.objects.filter(id=material_id).exists():
        #     return JsonResponse({'error': 8003, 'msg': "操作材料不存在"})
        user = Applicant.objects.get(id=user_id)
        material = Material.objects.get(id=material_id)
        enterprise = material.enterprise
        # 验证用户管理员身份
        if user.manage_enterprise_id != 0:
            return JsonResponse({'error': 7002, 'msg': "操作用户是管理员"})
        if int(user_id) != material.information.only_user.id:
            return JsonResponse({'error': 7012, 'msg': "操作用户不是简历拥有着"})
        if user.enterprise_id != 0:
            return JsonResponse({'error': 7003, 'msg': "操作用户已在公司内"})
        if int(material.status) != 2:
            return JsonResponse({'error': 7011, 'msg': "简历状态错误"})
        if type == 'refuse':
            material.status = 6
            recruit = material.recruit
            recruit.number = recruit.number+1
            recruit.save()
            refresh_recruits(recruit.id, recruit.number)
        if type == 'accept':
            material.status = 1
            enterprise.member.add(user)
            information_enterprise = UserInformationEnterprise.objects.create(post=material.recruit.post, user=user)
            user.user_information_enterprise = information_enterprise
            user.enterprise_id = enterprise.id
            user.save()
        material.save()
        return JsonResponse({'error': 0, 'msg': "操作成功"})

    return JsonResponse({"error": 7001, "msg": "请求方式错误"})


@csrf_exempt
def add_user_information_enterprise(request):
    if request.method == "POST":
        # 获取请求内容
        user_id = request.POST.get('user_id')
        join_date = request.POST.get('join_date', None)
        post = request.POST.get('post', None)
        # 获取实体
        # if not Applicant.objects.filter(id=user_id).exists():
        #     return JsonResponse({'error': 7002, 'msg': "操作用户不存在"})
        user = Applicant.objects.get(id=user_id)
        if user.enterprise_id == 0:
            return JsonResponse({'error': 7008, 'msg': "操作用户不在公司内"})
        user_information_enterprise = user.user_information_enterprise
        if post:
            user_information_enterprise.post = post
        if join_date:
            user_information_enterprise.join_date = join_date
        user_information_enterprise.save()
        return JsonResponse({'error': 0, 'msg': "修改成功"})

    return JsonResponse({"error": 7001, "msg": "请求方式错误"})


def to_json_member(member):
    user_information_enterprise = member.user_information_enterprise
    today = date.today()
    join_date = user_information_enterprise.join_date
    seniority = today.year - join_date.year - ((today.month, today.day) < (join_date.month, join_date.day))
    info = {
        "user_id": member.id,
        "user_name": member.user_name,
        "user_email": member.email,
        "user_interests": member.interests,
        "background": member.background,
        "post": user_information_enterprise.post,
        "join_data": join_date,
        "seniority": seniority
    }
    return info


def to_json_recruit(recruit):
    info = {
        "recruit_id": recruit.id,
        "recruit_post": recruit.post,
        "recruit_profile": recruit.profile,
        "recruit_status": recruit.status,
        "recruit_number": recruit.number,
        "recruit_release_time": recruit.release_time,
        "recruit_education": recruit.education,
        "salary_low": recruit.salary_low,
        "salary_high": recruit.salary_high,
        "address": recruit.address,
        "experience": recruit.experience,
        "requirement": recruit.requirement}
    return info

