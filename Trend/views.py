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
from notification.models import *


@csrf_exempt
def trend_add(request):
    if request.method == "POST":
        userid = request.POST.get("userId")
        content = request.POST.get("content")
        type = request.POST.get(
            "type"
        )  # 类型为固定的三种：技术学习进展、科研成果、项目成果userId
        transpond_id = request.POST.get(
            "transpond_id"
        )  # 如果不是转发,传0,是的话则转对应动态的id
        tags = request.POST.getlist("tags")  # 传一个字符串数组
        images = request.FILES.getlist("pictures")
        if not images:
            new_trend = Dynamic()
            new_trend.user_id = userid
            new_trend.content = content
            new_trend.type = type
            new_trend.transpond_id = transpond_id
            try:
                new_trend.save()
            except Exception as e:
                print(f"保存失败: {e}")
            for tag in tags:
                print(tag)
                temp = Tag.objects.create(trend_id=new_trend.id, recruit_name=tag)
                print(temp)
                return JsonResponse({"error": 0, "msg": "发布动态成功"})
        new_trend = Dynamic()
        new_trend.user_id = userid
        new_trend.content = content
        new_trend.type = type
        new_trend.transpond_id = transpond_id
        try:
            new_trend.save()
        except Exception as e:
            print(f"保存失败: {e}")
        for image in images:
            temp = TrendPicture()
            temp.trend_id = new_trend.id
            temp.user_id = userid
            temp.picture = image
            temp.save()
        for tag in tags:
            print(tag)
            temp = Tag.objects.create(trend_id=new_trend.id, recruit_name=tag)
            print(temp)
        return JsonResponse({"error": 0, "msg": "发布动态成功"})
    else:
        return JsonResponse({"error": 2001, "msg": "请求方式错误"})


@csrf_exempt
def get_person_single_trend(request):
    if request.method == "POST":
        userid = request.POST.get("userId")
        trend_id = request.POST.get("trend_id")
        results = list(Dynamic.objects.filter(id=trend_id).values())
        tags = list(Tag.objects.filter(trend_id=trend_id).values())
        us_name = Applicant.objects.get(id=userid).user_name
        for result in results:
            result["user_name"] = us_name
        for result in results:
            result["tags"] = tags
        pic_list = []
        for result in results:
            pic = list(TrendPicture.objects.filter(trend_id=trend_id).values())
            pic_list.extend(pic)
            result["pics"] = pic_list
        if not results:  # 如果查询结果为空
            return JsonResponse({"error": 1001, "msg": "暂无动态"})

        return JsonResponse(
            {
                "error": 0,
                "msg": "获取动态信息成功",
                "data": results,
                # "tags": tags,
            }
        )
    else:
        return JsonResponse({"error": 2001, "msg": "请求方式错误"})


@csrf_exempt
def get_person_all_trend(request):
    if request.method == "POST":
        userid = request.POST.get("userId")
        results = list(
            Dynamic.objects.filter(user_id=userid).values().order_by("-send_date")
        )
        print(results)
        for res in results:
            trend_id = res["id"]  # 获取动态的ID
            tags = list(Tag.objects.filter(trend_id=trend_id).values())
            res["tags"] = tags  # 将标签添加到动态中
            pic_list = []
            pic = list(TrendPicture.objects.filter(trend_id=trend_id).values())
            pic_list.extend(pic)
            res["pics"] = pic_list
        if not results:  # 如果查询结果为空
            return JsonResponse({"error": 1001, "msg": "该用户暂无动态"})

        return JsonResponse(
            {
                "error": 0,
                "msg": "获取动态信息成功",
                "data": results,
            }
        )
    else:
        return JsonResponse({"error": 2001, "msg": "请求方式错误"})


@csrf_exempt
def delete_trend(request):
    if request.method == "POST":
        trend_id = request.POST.get("trend_id")
        dynamic = Dynamic.objects.get(id=trend_id)
        dynamic.delete()
        return JsonResponse({"error": 0, "msg": "删除动态成功"})
    else:
        return JsonResponse({"error": 2001, "msg": "请求方式错误"})


@csrf_exempt
def like_trend(request):
    if request.method == "POST":
        trend_id = request.POST.get("trend_id")
        user_id = request.POST.get("user_id")
        temp_like = Like.objects.filter(user_id=user_id).filter(trend_id=trend_id)
        if temp_like.exists():
            return JsonResponse({"error": 1001, "msg": "您已经赞过了"})
        dynamic = Dynamic.objects.get(id=trend_id)
        dynamic.like_count = dynamic.like_count + 1
        dynamic.save()
        Like.objects.create(trend_id=trend_id, user_id=user_id)

        temp = list(Dynamic.objects.filter(id=trend_id))
        us = 0
        for a in temp:
            us = a.user_id
        temp_note = Notification()
        temp_note.user_id = us
        temp_note.title = "您的动态收到一条点赞"
        temp_note.type = 1
        temp_note.is_read = 0
        temp_note.message = "您的 " + dynamic.content + " 动态收到一条点赞"
        temp_note.time = datetime.now()
        temp_note.related_user_id = user_id
        temp_note.related_blog_id = trend_id
        try:
            temp_note.save()
        except Exception as e:
            return JsonResponse({"error": 3001, "msg": str(e)})
        return JsonResponse({"error": 0, "msg": "点赞成功"})
    else:
        return JsonResponse({"error": 2001, "msg": "请求方式错误"})


@csrf_exempt
def get_trend_like_users(request):
    if request.method == "POST":
        trend_id = request.POST.get("trend_id")
        results = list(Dynamic.objects.filter(id=trend_id).values("id"))
        users = list(Like.objects.filter(trend_id=trend_id).values())
        print(users)
        for result in results:
            like_applicant_list = []
            for user in users:
                us = list(Applicant.objects.filter(id=user["user_id"]).values())
                like_applicant_list.extend(us)
            result["like_applicant"] = like_applicant_list

        if not results:  # 如果查询结果为空
            return JsonResponse({"error": 1001, "msg": "暂无动态"})

        return JsonResponse(
            {
                "error": 0,
                "msg": "获取点赞列表成功",
                "data": results,
                # "tags": tags,
            }
        )
    else:
        return JsonResponse({"error": 2001, "msg": "请求方式错误"})


@csrf_exempt
def delete_like(request):
    if request.method == "POST":
        trend_id = request.POST.get("trend_id")
        user_id = request.POST.get("user_id")
        simple_like = Like.objects.filter(trend_id=trend_id).filter(user_id=user_id)
        if not simple_like.exists():
            return JsonResponse({"error": 1001, "msg": "您没有点赞"})
        dynamic = Dynamic.objects.get(id=trend_id)
        dynamic.like_count = dynamic.like_count - 1
        dynamic.save()
        simple_like.delete()
        return JsonResponse({"error": 0, "msg": "取消点赞成功"})
    else:
        return JsonResponse({"error": 2001, "msg": "请求方式错误"})


@csrf_exempt
def comment_trend(request):
    if request.method == "POST":
        trend_id = request.POST.get("trend_id")
        user_id = request.POST.get("user_id")
        content = request.POST.get("content")
        dynamic = Dynamic.objects.get(id=trend_id)
        dynamic.comment_count = dynamic.comment_count + 1
        dynamic.save()
        Comment.objects.create(trend_id=trend_id, user_id=user_id, content=content)

        temp = list(Dynamic.objects.filter(id=trend_id))
        us = 0
        for a in temp:
            us = a.user_id
        temp_note = Notification()
        temp_note.user_id = us
        temp_note.title = "您的动态收到一条评论"
        temp_note.type = 2
        temp_note.is_read = 0
        temp_note.message = "您的 " + dynamic.content + " 动态收到一条评论: " + content
        temp_note.time = datetime.now()
        temp_note.related_user_id = user_id
        temp_note.related_blog_id = trend_id
        try:
            temp_note.save()
        except Exception as e:
            return JsonResponse({"error": 3001, "msg": str(e)})
        return JsonResponse({"error": 0, "msg": "评论动态成功", "data": content})
    else:
        return JsonResponse({"error": 2001, "msg": "请求方式错误"})


@csrf_exempt
def get_trend_comments(request):
    if request.method == "POST":
        trend_id = request.POST.get("trend_id")
        results = list(Dynamic.objects.filter(id=trend_id).values("id"))
        comments = list(Comment.objects.filter(trend_id=trend_id).values())
        for comment in comments:
            temp_id = comment["user_id"]
            comment["user_id"] = list(Applicant.objects.filter(id=temp_id).values())
        for result in results:
            result["comments"] = comments

        if not results:  # 如果查询结果为空
            return JsonResponse({"error": 1001, "msg": "暂无动态"})

        return JsonResponse(
            {
                "error": 0,
                "msg": "获取评论列表成功",
                "data": results,
                # "tags": tags,
            }
        )
    else:
        return JsonResponse({"error": 2001, "msg": "请求方式错误"})


@csrf_exempt
def transport_trend(request):
    if request.method == "POST":
        userid = request.POST.get("userId")
        content = request.POST.get("content")
        # type = request.POST.get("type")
        transpond_id = request.POST.get(
            "transpond_id"
        )  # 如果不是转发,传0,是的话则转对应动态的id
        old_trend = list(Dynamic.objects.filter(id=transpond_id).values())
        print(old_trend)
        new_trend = Dynamic()
        new_trend.user_id = userid
        new_trend.content = content
        new_trend.type = type
        new_trend.transpond_id = transpond_id
        new_trend.save()
        return JsonResponse({"error": 0, "msg": "转发动态成功", "data": old_trend})
    else:
        return JsonResponse({"error": 2001, "msg": "请求方式错误"})


@csrf_exempt
def upload_picture(request):
    if request.method == "POST":
        user_id = request.POST.get("user_id")
        trend_id = request.POST.get("trend_id")
        pic = request.FILES.get("picture", None)
        print(pic)
        trend = Dynamic.objects.get(id=trend_id)
        if pic:
            temp = TrendPicture()
            temp.trend_id = trend_id
            temp.user_id = user_id
            temp.picture = pic
            temp.save()

        return JsonResponse({"error": 0, "msg": "图片上传成功"})
    else:
        return JsonResponse({"error": 2001, "msg": "请求方式错误"})


@csrf_exempt
def get_enterprise_trends(request):
    # 获取企业所有动态
    if request.method == "POST":
        # 需要传入：企业enterprise_id
        enterprise_id = request.POST.get("enterprise_id")
        # 获取企业员工
        enterprise_member_list = list(
            Enterprise.objects.get(id=enterprise_id).member.all()
        )
        # 根据粉丝数降序排列
        enterprise_member_list.sort(
            key=lambda employee: employee.followers.count(), reverse=True
        )
        # 选出前五
        top_five_members = enterprise_member_list[:5]
        enterprise_trend_list = list()
        for member in top_five_members:
            member_trend_list = list(Dynamic.objects.values().filter(user_id=member.id))
            enterprise_trend_list = enterprise_trend_list + member_trend_list
        # 根据时间排序
        enterprise_trend_list.sort(key=lambda entry: entry["send_date"], reverse=True)
        for trend in enterprise_trend_list:
            trend_id = trend["id"]  # 获取动态的ID
            tags = list(Tag.objects.filter(trend_id=trend_id).values())
            trend["tags"] = tags  # 将标签添加到动态中
            pic_list = []
            pic = list(TrendPicture.objects.filter(trend_id=trend_id).values())
            pic_list.extend(pic)
            trend["pics"] = pic_list
        if not enterprise_trend_list:  # 如果查询结果为空
            return JsonResponse({"error": 3001, "msg": "该企业暂无动态"})
        return JsonResponse(
            {
                "error": 0,
                "msg": "获取企业动态成功",
                "data": enterprise_trend_list,
            }
        )
    return JsonResponse({"error": 2001, "msg": "请求方式错误"})


@csrf_exempt
def push_enterprise_trends(request):
    # 系统推送用户关注的企业的动态
    if request.method == "POST":
        # 需要传入：用户user_id
        user_id = request.POST.get("user_id")
        # 获取用户关注的全部企业
        user_follow_enterprise_list = list(
            Applicant.objects.get(id=user_id).user_follow_enterprise.all()
        )
        follow_enterprise_trend_list = list()
        for enterprise in user_follow_enterprise_list:
            enterprise_member_list = list(
                Enterprise.objects.get(id=enterprise.id).member.all()
            )
            # 根据粉丝数降序排列
            enterprise_member_list.sort(
                key=lambda employee: employee.followers.count(), reverse=True
            )
            # 选出前五
            top_five_members = enterprise_member_list[:5]
            enterprise_trend_list = list()
            for member in top_five_members:
                member_trend_list = list(
                    Dynamic.objects.values().filter(user_id=member.id)
                )
                enterprise_trend_list = enterprise_trend_list + member_trend_list
            follow_enterprise_trend_list = (
                follow_enterprise_trend_list + enterprise_trend_list
            )
        for trend in follow_enterprise_trend_list:
            # 添加动态所属企业
            trend_owner_id = trend["user_id"]
            owner_enterprise_id = Applicant.objects.get(id=trend_owner_id).enterprise_id
            owner_enterprise_name = Enterprise.objects.get(id=owner_enterprise_id).name
            trend["owner_enterprise_name"] = owner_enterprise_name
        follow_enterprise_trend_list.sort(
            key=lambda entry: entry["send_date"], reverse=True
        )
        for trend in follow_enterprise_trend_list:
            owner_id = trend["user_id"]
            trend["owner_name"] = Applicant.objects.get(id=owner_id).user_name
            trend_id = trend["id"]  # 获取动态的ID
            tags = list(Tag.objects.filter(trend_id=trend_id).values())
            trend["tags"] = tags  # 将标签添加到动态中
            pic_list = []
            pic = list(TrendPicture.objects.filter(trend_id=trend_id).values())
            pic_list.extend(pic)
            trend["pics"] = pic_list
        return JsonResponse(
            {
                "error": 0,
                "msg": "推送企业动态成功",
                "data": follow_enterprise_trend_list,
            }
        )
    return JsonResponse({"error": 2001, "msg": "请求方式错误"})


@csrf_exempt
def push_user_trends(request):
    # 系统推送用户关注的企业的动态
    if request.method == "POST":
        # 需要传入：用户user_id
        user_id = request.POST.get("user_id")
        # 获取用户关注列表
        user_follow_user_list = list(Applicant.objects.get(id=user_id).following.all())
        follow_user_trend_list = list()
        for user in user_follow_user_list:
            user_trend_list = list(Dynamic.objects.values().filter(user_id=user.id))
            follow_user_trend_list = follow_user_trend_list + user_trend_list
        follow_user_trend_list.sort(key=lambda entry: entry["send_date"], reverse=True)
        for trend in follow_user_trend_list:
            owner_id = trend["user_id"]
            trend["owner_name"] = Applicant.objects.get(id=owner_id).user_name
            trend_id = trend["id"]  # 获取动态的ID
            tags = list(Tag.objects.filter(trend_id=trend_id).values())
            trend["tags"] = tags  # 将标签添加到动态中
            pic_list = []
            pic = list(TrendPicture.objects.filter(trend_id=trend_id).values())
            pic_list.extend(pic)
            trend["pics"] = pic_list
        return JsonResponse(
            {
                "error": 0,
                "msg": "推送用户动态成功",
                "data": follow_user_trend_list,
            }
        )
    return JsonResponse({"error": 2001, "msg": "请求方式错误"})
