from django.urls import path

from .views import *

urlpatterns = [
    path("publish_recruitment", publish_recruitment),  # 发布招聘信息
    path("show_recruitment", show_recruitment),  # 修改招聘信息
    path("update_recruitment", update_recruitment),  # 修改招聘信息
    path("show_enterprise_material", show_enterprise_material),  # 查看申请列表
    path("manage_apply_material", manage_apply_material),  # 管理申请列表
    path("show_material_single", show_material_single),  # 查看公司申请列表
    path("user_apply_recruit", user_apply_recruit),
    path("show_recruit_material", show_recruit_material),  # 查看某招聘下的申请列表
    path("recruitment_search", recruitment_search),  # 搜索岗位
    path("get_intended_recruitment", get_intended_recruitment),  # 获取用户感兴趣的招聘
]
