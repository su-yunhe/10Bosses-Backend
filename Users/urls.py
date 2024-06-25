from django.urls import path
from .views import *

urlpatterns = [
    path("applicant_register", register),
    path("applicant_login", login),
    path("user_modify_background", user_modify_background),
    path("get_single_applicant", get_single_applicant),
]
