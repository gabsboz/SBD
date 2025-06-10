from rest_framework import viewsets
from .models import student as Student, ocena
from .serializers import StudentSerializer, OcenaSerializer
from django.shortcuts import render, get_object_or_404,redirect
from django.db import connection
from django.http import JsonResponse
import oracledb
from mainapp.models import konto as Konto
from .forms import KontoLoginForm
from django.contrib import messages

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





def konto_login(request):
    error = None

    if request.method == 'POST':
        form = KontoLoginForm(request.POST)
        if form.is_valid():
            konto_id = form.cleaned_data['konto_id']
            haslo = form.cleaned_data['haslo']
            try:
                konto = Konto.objects.get(konto_id=konto_id)
                if konto.check_password(haslo):
                    request.session['konto_id'] = konto.konto_id
                    request.session['rola'] = konto.rola
                    if konto.rola == 'student':
                        return redirect('student_dashboard')
                    return redirect('dashboard')  # lub inna strona dla innych ról
                else:
                    error = "Nieprawidłowe hasło"
            except Konto.DoesNotExist:
                error = "Konto nie istnieje"
    else:
        form = KontoLoginForm()

    return render(request, 'konto_login.html', {'form': form, 'error': error})


def konto_logout(request):
    request.session.flush()
    return redirect('konto_login')


def tylko_dla_studentow(view_func):
    def wrapper(request, *args, **kwargs):
        if request.session.get('rola') != 'student':
            return redirect('konto_login')
        return view_func(request, *args, **kwargs)
    return wrapper


@tylko_dla_studentow
def student_dashboard(request):
    konto_id = request.session.get('konto_id')

    try:
        konto_uzytkownika = Konto.objects.get(pk=konto_id)
        student_obj = Student.objects.get(konto=konto_uzytkownika)
    except (Konto.DoesNotExist, Student.DoesNotExist):
        return redirect('konto_login')

    return render(request, 'mainapp/student_dashboard.html', {
        'student': student_obj
    })

@tylko_dla_studentow
def moje_oceny(request):
    konto_id = request.session.get('konto_id')

    try:
        konto_uzytkownika = Konto.objects.get(pk=konto_id)
        student = Student.objects.get(konto=konto_uzytkownika)
    except (Konto.DoesNotExist, Student.DoesNotExist):
        return redirect('konto_login')

    with connection.cursor() as cursor:
        refcursor = cursor.var(oracledb.DB_TYPE_CURSOR)
        
        cursor.execute("""
            BEGIN
                :refcursor := get_student_grades(:student_id);
            END;
        """, {
            'refcursor': refcursor,
            'student_id': student.student_id,
        })

        result_cursor = refcursor.getvalue()
        grades = result_cursor.fetchall()

    return render(request, 'mainapp/oceny_studenta.html', {
        'student': student,
        'oceny': grades
    })
