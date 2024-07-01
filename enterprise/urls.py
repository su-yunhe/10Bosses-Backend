from django.urls import path

from .views import *

urlpatterns = [
    path("enterprise_search", enterprise_search),
    path("whoosh_search", whoosh_search),  # 测试
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
    path("show_withdraw_list", show_withdraw_list),  # 展示企业退出申请
    path("apply_withdraw", apply_withdraw),  # 用户退出企业
    path("manage_withdraw", manage_withdraw),  # 管理员同意用户退出
    path("delete_member", delete_member),  # 管理员主动删除用户
    path("user_enter_enterprise", user_enter_enterprise),  # 用户进行企业认证
    path("add_user_information_enterprise", add_user_information_enterprise),  # 用户补充企业个人信息
    path("user_follow_enterprise", user_follow_enterprise),  # 用户关注企业
    path("user_cancel_follow_enterprise", user_cancel_follow_enterprise),  # 用户取消关注
    path("show_user_follow_enterprise", show_user_follow_enterprise),  # 查看用户关注企业列表
    path("check_user_follow_enterprise", check_user_follow_enterprise),  # 检查是否用户关注企业
    path("check_user_be_member", check_user_be_member)  # 检查用户是否是企业成员

    # path("add_enterprise_member", add_enterprise_member),
]
