
from .models import student as Student, ocena,nauczyciel,przedmiot

from django.shortcuts import render, get_object_or_404,redirect
from django.db import connection
from django.http import JsonResponse
import oracledb
from mainapp.models import konto as Konto
from .forms import KontoLoginForm,DodajOceneForm
from django.contrib import messages
from django.utils import timezone



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
                        # Zapamiętaj również student_id w sesji
                        student_obj = Student.objects.get(konto=konto)
                        request.session['student_id'] = student_obj.student_id
                        return redirect('student_dashboard')
                    else:
                        # Zapamiętaj nauczyciel_id
                        nauczyciel_obj = nauczyciel.objects.get(konto=konto)
                        request.session['nauczyciel_id'] = nauczyciel_obj.pk
                        return redirect('nauczyciel_dashboard')
                else:
                    error = "Nieprawidłowe hasło"
            except Konto.DoesNotExist:
                error = "Konto nie istnieje"
            except (Student.DoesNotExist, nauczyciel.DoesNotExist):
                error = "Nie znaleziono przypisanego użytkownika."
    else:
        form = KontoLoginForm()

    return render(request, 'mainapp/konto_login.html', {'form': form, 'error': error})


def konto_logout(request):
    request.session.flush()
    return redirect('konto_login')


def tylko_dla_studentow(view_func):
    def wrapper(request, *args, **kwargs):
        if request.session.get('rola') != 'student':
            return redirect('konto_login')
        return view_func(request, *args, **kwargs)
    return wrapper

def tylko_dla_nauczycieli(view_func):
    def wrapper(request, *args, **kwargs):
        if request.session.get('rola') != 'nauczyciel':
            return redirect('konto_login')
        return view_func(request, *args, **kwargs)
    return wrapper

@tylko_dla_nauczycieli
def lista_studentow(request):
    studenci = Student.objects.all()
    return render(request, 'mainapp/lista_studentow.html', {'studenci': studenci})


@tylko_dla_nauczycieli
def oceny_studenta(request, student_id):
    student = get_object_or_404(Student, pk=student_id)

    if request.method == 'POST':
        form = DodajOceneForm(request.POST)
        if form.is_valid():
            wartosc = form.cleaned_data['wartosc']
            przedmiot_obj = form.cleaned_data['przedmiot']
            data_wprowadzenia = timezone.now().replace(tzinfo=None)

            semestr_obj = form.cleaned_data['semestr']
            nauczyciel_id = request.session.get('nauczyciel_id')


            #
            with connection.cursor() as cursor:
                try:
                    cursor.execute("""
                    BEGIN add_ocena(:wartosc, :student_id, :przedmiot_id, :data_wprowadzenia, :nauczyciel_id, :semestr_id); END;
                """, {
                    'wartosc': float(wartosc),
                    'student_id': int(student_id),
                    'przedmiot_id': int(przedmiot_obj.pk),
                    'data_wprowadzenia': data_wprowadzenia,
                    'nauczyciel_id': int(nauczyciel_id),
                    'semestr_id': int(semestr_obj.pk),
                })


                    connection.commit()
                    messages.success(request, 'Ocena została dodana.')
                    return redirect('oceny_studenta', student_id=student_id)
                except Exception as e:
                    messages.error(request, f'Błąd: {e}')
        else:
            messages.error(request, 'Błąd w formularzu.')
    else:
        form = DodajOceneForm()

    # Pobranie ocen przez procedurę
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
        'oceny': grades,
        'form': form,
    })






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



@tylko_dla_nauczycieli
def nauczyciel_dashboard(request):
    konto_id = request.session.get('konto_id')

    try:
        konto_uzytkownika = Konto.objects.get(pk=konto_id)
        nauczyciel_obj = nauczyciel.objects.get(konto=konto_uzytkownika)
    except (Konto.DoesNotExist, nauczyciel.DoesNotExist):
        return redirect('konto_login')
    
    return render(request, 'mainapp/nauczyciel_dashboard.html', {
        'nauczyciel': nauczyciel_obj
    })

def ranking_view(request):
    rola = request.session.get('rola')
    if rola not in ['student', 'nauczyciel']:
        return redirect('konto_login')

    with connection.cursor() as cursor:
        refcursor = cursor.var(oracledb.DB_TYPE_CURSOR)

        cursor.execute("""
            BEGIN
                :refcursor := ranking;
            END;
        """, {'refcursor': refcursor})

        result_cursor = refcursor.getvalue()
        ranking_data = result_cursor.fetchall()

    ranking_list = []
    for idx, (student_id, srednia) in enumerate(ranking_data, start=1):
        ranking_list.append({
            'pozycja': idx,
            'student_id': student_id,
            'srednia': srednia,
        })

    if rola == 'student':
        konto_id = request.session.get('konto_id')
        try:
            konto = Konto.objects.get(pk=konto_id)
            student = Student.objects.get(konto=konto)
        except (Konto.DoesNotExist, Student.DoesNotExist):
            return redirect('konto_login')

        for r in ranking_list:
            if r['student_id'] == student.student_id:
                return render(request, 'mainapp/student_ranking.html', {
                    'moje_miejsce': r['pozycja'],
                    'moja_srednia': r['srednia']
                })

        return render(request, 'mainapp/student_ranking.html', {
            'moje_miejsce': None,
            'moja_srednia': 0
        })

    elif rola == 'nauczyciel':
        return render(request, 'mainapp/ranking_lista.html', {
            'ranking': ranking_list
        })

    return redirect('konto_login')
