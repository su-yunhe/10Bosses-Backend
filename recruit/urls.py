from django.urls import path

from .views import *

urlpatterns = [
    path("publish_recruitment", publish_recruitment),  # 发布招聘信息
    path("show_recruitment", show_recruitment),  # 查看招聘信息
    path("update_recruitment", update_recruitment),  # 修改招聘信息
    path("manage_recruitment", manage_recruitment),  # 管理招聘通道
    path("delete_recruitment", delete_recruitment),  # 删除招聘信息
    path("user_apply_recruit", user_apply_recruit),  # 用户投递简历
    path("show_enterprise_recruit_material", show_enterprise_recruit_material),  # 查看公司所有招聘简历
    path("show_recruit_material", show_recruit_material),  # 查看某招聘下的申请列表
    path("show_user_material", show_user_material),  # 查看用户所有简历
    path("show_material_single", show_material_single),  # 查看单个申请材料
    path("manage_apply_material", manage_apply_material),  # 审批简历
    path("recruitment_search", recruitment_search),  # 搜索岗位
    path("get_intended_recruitment", get_intended_recruitment),  # 获取用户感兴趣的招聘

    path('update_test/', index, name='index'),
]
