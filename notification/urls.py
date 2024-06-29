from django.urls import path

from .views import *

urlpatterns = [
    path("employee_quit", employee_quit)
]