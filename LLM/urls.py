from django.urls import path
from .views import *

urlpatterns = [
    path("analyze_file", analyze_file),
]
