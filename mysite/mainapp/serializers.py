from rest_framework import serializers
from .models import student, ocena

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = student
        fields = '__all__'

class OcenaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ocena
        fields = '__all__'
