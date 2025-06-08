from rest_framework import viewsets
from .models import student as Student, ocena
from .serializers import StudentSerializer, OcenaSerializer
from django.shortcuts import render, get_object_or_404
from django.db import connection
from django.http import JsonResponse
import oracledb

class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer

class OcenaViewSet(viewsets.ModelViewSet):
    queryset = ocena.objects.all()
    serializer_class = OcenaSerializer


def lista_studentow(request):
    studenci = Student.objects.all()
    return render(request, 'mainapp/lista_studentow.html', {'studenci': studenci})



def oceny_studenta(request, student_id):
    student = get_object_or_404(Student, pk=student_id)

    with connection.cursor() as cursor:
        refcursor = cursor.var(oracledb.DB_TYPE_CURSOR)
        
        cursor.execute("""
            BEGIN
                :refcursor := get_student_grades(:student_id);
            END;
        """, {
            'refcursor': refcursor,
            'student_id': student_id,
        })

        result_cursor = refcursor.getvalue()
        grades = result_cursor.fetchall()

    return render(request, 'mainapp/oceny_studenta.html', {
        'student': student,
        'oceny': grades
    })