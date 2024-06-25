import jieba
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from .models import Enterprise
from user.models import User
from recruit.models import Recruit
from haystack.forms import ModelSearchForm
from haystack.query import EmptySearchQuerySet, SearchQuerySet


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
            results = list()
            for enterprise_id in search_results:
                enterprise = Enterprise.objects.values().get(id=enterprise_id)
                # 通过企业管理员id获取其真实姓名
                manager_id = Enterprise.objects.get(id=enterprise_id).manager_id
                manager_name = User.objects.get(id=manager_id).real_name
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
    if request.method == 'POST':
        enterprise_id = request.POST.get('enterprise_id')
        recruitment_list = list(Enterprise.objects.values(enterprise_id=enterprise_id).get(id=enterprise_id))
        return JsonResponse({"errno": 0, "msg": "获取企业招聘信息成功", "data": recruitment_list})
    return JsonResponse({"errno": 2001, "msg": "请求方式错误"})


@csrf_exempt
def hello(request):
    return JsonResponse({'message': 'Hello'})
