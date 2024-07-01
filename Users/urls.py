from django.urls import path
from .views import *

urlpatterns = [
    path("applicant_register", register),
    path("applicant_login", login),
    path("user_modify_background", user_modify_background),
    path("get_single_applicant", get_single_applicant),
    path("user_modify_info", user_modify_info),
    path("search_user", search_user),
    path("interest_add", interest_add),
    path("upload/", upload_pdf),
    path("user_logout", user_delete),
    path("user_follow", user_follow),
    path("get_all_followee", get_all_followee),
    path("get_all_follower", get_all_follower),
    path("update_user_interest", update_user_interest),
    path("download_pdf", download_pdf),
    path("user_unfollow", user_unfollow)
]
