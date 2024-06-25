from rest_framework import serializers
from .models import Applicant


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Applicant
        fields = ("id", "user_name", "note")
