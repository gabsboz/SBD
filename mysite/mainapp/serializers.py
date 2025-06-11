from rest_framework import serializers
from .models import Student, ocena, Konto, nauczyciel

class KontoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Konto
        fields = ['konto_id', 'login', 'rola']

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = '__all__'

class OcenaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ocena
        fields = '__all__'

class NauczycielSerializer(serializers.ModelSerializer):
    class Meta:
        model = nauczyciel
        fields = '__all__'
