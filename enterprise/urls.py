from django.urls import path

from .views import *

urlpatterns = [
    path("enterprise_search", enterprise_search),
    path("whoosh_search", whoosh_search), # 测试
    path("get_enterprise_recruitment", get_enterprise_recruitment),
    path("recommend_enterprise", recommend_enterprise),
    path("recommend_users", recommend_users),
    path("create_enterprise", create_enterprise),  # 创建企业
    path("show_enterprise", show_enterprise),  # 展示企业资料
    path("update_enterprise", update_enterprise),  # 修改企业资料
    path("change_manager", change_manager),  # 更改管理员
    path("delete_enterprise", delete_enterprise),  # 删除企业
    path("show_enterprise_member", show_enterprise_member),  # 展示企业员工名单
    path("show_recruitment_list", show_recruitment_list),  # 展示企业招聘列表
    path("normal_user_apply_enterprise", normal_user_apply_enterprise),  # 普通用户申请企业认证
    path("show_enterprise_normal_material", show_enterprise_normal_material)  # 展示企业下所有普通用户申请材料
    # path("add_enterprise_member", add_enterprise_member),
]
