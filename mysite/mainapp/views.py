from .models import student as Student, ocena, nauczyciel, przedmiot, semestr
from django.shortcuts import render, get_object_or_404, redirect
from django.db import connection
from django.http import JsonResponse, HttpResponse
import oracledb
from mainapp.models import konto as Konto
from .forms import KontoLoginForm, DodajOceneForm
from django.contrib import messages
from django.utils import timezone
import csv
from django.db.models import Avg, Count
from datetime import datetime, timedelta


def konto_login(request):
    # Logowanie użytkownika – obsługa formularza
    error = None

    if request.method == 'POST':
        form = KontoLoginForm(request.POST)
        if form.is_valid():
            konto_id = form.cleaned_data['konto_id']
            haslo = form.cleaned_data['haslo']
            try:
                konto = Konto.objects.get(konto_id=konto_id)
                if konto.check_password(haslo):  # Sprawdź hasło
                    # Ustaw dane sesji
                    request.session['konto_id'] = konto.konto_id
                    request.session['rola'] = konto.rola

                    if konto.rola == 'student':
                        # Zapamiętaj id studenta w sesji
                        student_obj = Student.objects.get(konto=konto)
                        request.session['student_id'] = student_obj.student_id
                        return redirect('student_dashboard')
                    else:
                        # Zapamiętaj id nauczyciela w sesji
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

    # Renderuj formularz logowania z ewentualnym błędem
    return render(request, 'mainapp/konto_login.html', {'form': form, 'error': error})


def konto_logout(request):
    # Wyczyść sesję i wyloguj użytkownika
    request.session.flush()
    return redirect('konto_login')


def tylko_dla_studentow(view_func):
    # Dekorator blokujący dostęp jeśli rola to nie student
    def wrapper(request, *args, **kwargs):
        if request.session.get('rola') != 'student':
            return redirect('konto_login')
        return view_func(request, *args, **kwargs)
    return wrapper


def tylko_dla_nauczycieli(view_func):
    # Dekorator blokujący dostęp jeśli rola to nie nauczyciel
    def wrapper(request, *args, **kwargs):
        if request.session.get('rola') != 'nauczyciel':
            return redirect('konto_login')
        return view_func(request, *args, **kwargs)
    return wrapper


@tylko_dla_nauczycieli
def lista_studentow(request):
    # Lista wszystkich studentów, dostępna tylko dla nauczycieli
    studenci = Student.objects.all()
    return render(request, 'mainapp/lista_studentow.html', {'studenci': studenci})


@tylko_dla_nauczycieli
def oceny_studenta(request, student_id):
    # Widok do dodawania i wyświetlania ocen konkretnego studenta
    student = get_object_or_404(Student, pk=student_id)

    if request.method == 'POST':
        # Formularz do dodania oceny, ograniczony do przedmiotów studenta
        form = DodajOceneForm(request.POST, student_id=student_id)  # ważne podanie student_id do formy
        if form.is_valid():
            wartosc = form.cleaned_data['wartosc']
            przedmiot_obj = form.cleaned_data['przedmiot']
            data_wprowadzenia = timezone.now().replace(tzinfo=None)
            semestr_obj = form.cleaned_data['semestr']
            nauczyciel_id = request.session.get('nauczyciel_id')

            # Wywołanie procedury PL/SQL do dodania oceny
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
        form = DodajOceneForm(student_id=student_id)  # podajemy student_id aby filtrować przedmioty

    # Pobierz oceny studenta przez procedurę bazodanową
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
    # Kokpit studenta, pobiera dane o użytkowniku z sesji i wyświetla
    konto_id = request.session.get('konto_id')

    try:
        konto_uzytkownika = Konto.objects.get(pk=konto_id)
        student_obj = Student.objects.get(konto=konto_uzytkownika)
    except (Konto.DoesNotExist, Student.DoesNotExist):
        return redirect('konto_login')

    # Pobierz statystyki studenta
    with connection.cursor() as cursor:
        # Średnia ocen studenta
        cursor.execute("""
            SELECT NVL(ROUND(AVG(wartosc), 2), 0) as srednia
            FROM MAINAPP_OCENA 
            WHERE student_id = :student_id
        """, {'student_id': student_obj.student_id})
        
        result = cursor.fetchone()
        srednia_ocen = result[0] if result else 0

        # Liczba ocen
        cursor.execute("""
            SELECT COUNT(*) as liczba_ocen
            FROM MAINAPP_OCENA 
            WHERE student_id = :student_id
        """, {'student_id': student_obj.student_id})
        
        result = cursor.fetchone()
        liczba_ocen = result[0] if result else 0

    return render(request, 'mainapp/student_dashboard.html', {
        'student': student_obj,
        'srednia_ocen': srednia_ocen,
        'liczba_ocen': liczba_ocen
    })


@tylko_dla_studentow
def moje_oceny(request):
    # Widok ocen zalogowanego studenta (pobierane przez procedurę)
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
    # Kokpit nauczyciela, pokazuje jego dane i statystyki
    konto_id = request.session.get('konto_id')

    try:
        konto_uzytkownika = Konto.objects.get(pk=konto_id)
        nauczyciel_obj = nauczyciel.objects.get(konto=konto_uzytkownika)
    except (Konto.DoesNotExist, nauczyciel.DoesNotExist):
        return redirect('konto_login')
    
    # Pobierz statystyki nauczyciela
    with connection.cursor() as cursor:
        # Liczba wystawionych ocen
        cursor.execute("""
            SELECT COUNT(*) as liczba_ocen
            FROM MAINAPP_OCENA 
            WHERE nauczyciel_id = :nauczyciel_id
        """, {'nauczyciel_id': nauczyciel_obj.nauczyciel_id})
        
        result = cursor.fetchone()
        liczba_ocen = result[0] if result else 0

        # Liczba przedmiotów prowadzonych
        cursor.execute("""
            SELECT COUNT(*) as liczba_przedmiotow
            FROM MAINAPP_PRZEDMIOT 
            WHERE nauczyciel_id = :nauczyciel_id
        """, {'nauczyciel_id': nauczyciel_obj.nauczyciel_id})
        
        result = cursor.fetchone()
        liczba_przedmiotow = result[0] if result else 0

        # Średnia wystawianych ocen
        cursor.execute("""
            SELECT NVL(ROUND(AVG(wartosc), 2), 0) as srednia
            FROM MAINAPP_OCENA 
            WHERE nauczyciel_id = :nauczyciel_id
        """, {'nauczyciel_id': nauczyciel_obj.nauczyciel_id})
        
        result = cursor.fetchone()
        srednia_ocen = result[0] if result else 0
    
    return render(request, 'mainapp/nauczyciel_dashboard.html', {
        'nauczyciel': nauczyciel_obj,
        'liczba_ocen': liczba_ocen,
        'liczba_przedmiotow': liczba_przedmiotow,
        'srednia_ocen': srednia_ocen
    })


def ranking_view(request):
    # Ranking – widok dostępny dla zalogowanych studentów i nauczycieli
    rola = request.session.get('rola')
    if rola not in ['student', 'nauczyciel']:
        return redirect('konto_login')

    # Pobierz ranking z bazy (procedura lub funkcja)
    with connection.cursor() as cursor:
        refcursor = cursor.var(oracledb.DB_TYPE_CURSOR)

        cursor.execute("""
            BEGIN
                :refcursor := ranking;
            END;
        """, {'refcursor': refcursor})

        result_cursor = refcursor.getvalue()
        ranking_data = result_cursor.fetchall()

    # Przerób wynik na listę słowników z pozycją w rankingu
    ranking_list = []
    for idx, (student_id, srednia) in enumerate(ranking_data, start=1):
        # Pobierz dane studenta
        try:
            student_obj = Student.objects.get(student_id=student_id)
            ranking_list.append({
                'pozycja': idx,
                'student_id': student_id,
                'student_name': f"{student_obj.imie} {student_obj.nazwisko}",
                'kierunek': student_obj.kierunek,
                'rok_studiow': student_obj.rok_studiow,
                'srednia': srednia,
            })
        except Student.DoesNotExist:
            ranking_list.append({
                'pozycja': idx,
                'student_id': student_id,
                'student_name': "Nieznany student",
                'kierunek': "-",
                'rok_studiow': "-",
                'srednia': srednia,
            })

    if rola == 'student':
        konto_id = request.session.get('konto_id')
        try:
            konto = Konto.objects.get(pk=konto_id)
            student = Student.objects.get(konto=konto)
        except (Konto.DoesNotExist, Student.DoesNotExist):
            return redirect('konto_login')

        # Znajdź miejsce i średnią aktualnego studenta
        for r in ranking_list:
            if r['student_id'] == student.student_id:
                return render(request, 'mainapp/student_ranking.html', {
                    'moje_miejsce': r['pozycja'],
                    'moja_srednia': r['srednia'],
                    'ranking_size': len(ranking_list)
                })

        # Jeśli brak w rankingu, pokaż zero
        return render(request, 'mainapp/student_ranking.html', {
            'moje_miejsce': None,
            'moja_srednia': 0,
            'ranking_size': len(ranking_list)
        })

    elif rola == 'nauczyciel':
        # Dla nauczyciela pokaz całą listę
        return render(request, 'mainapp/ranking_lista.html', {
            'ranking': ranking_list
        })

    return redirect('konto_login')


def moje_grupy(request):
    # Widok grup dla zalogowanego studenta (wywołanie procedury)
    konto_id = request.session.get('konto_id')

    try:
        konto_uzytkownika = Konto.objects.get(pk=konto_id)
        student_obj = Student.objects.get(konto=konto_uzytkownika)
    except (Konto.DoesNotExist, Student.DoesNotExist):
        return redirect('konto_login')

    with connection.cursor() as cursor:
        refcursor = cursor.var(oracledb.DB_TYPE_CURSOR)
        cursor.execute("""
            BEGIN
                :refcursor := get_student_groups(:student_id);
            END;
        """, {
            'refcursor': refcursor,
            'student_id': student_obj.student_id,
        })

        result_cursor = refcursor.getvalue()
        grupy = result_cursor.fetchall()

    # Zamiana wyniku na listę słowników do łatwego wyświetlania w template
    grupy_data = [{'przedmiot_nazwa': przedmiot, 'grupa_nazwa': grupa} for przedmiot, grupa in grupy]

    return render(request, 'mainapp/moje_grupy.html', {
        'student': student_obj,
        'grupy': grupy_data
    })


@tylko_dla_nauczycieli
def statystyki_przedmiotow(request):
    """Statystyki przedmiotów dla nauczyciela"""
    konto_id = request.session.get('konto_id')
    
    try:
        konto_uzytkownika = Konto.objects.get(pk=konto_id)
        nauczyciel_obj = nauczyciel.objects.get(konto=konto_uzytkownika)
    except (Konto.DoesNotExist, nauczyciel.DoesNotExist):
        return redirect('konto_login')

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                p.nazwa as przedmiot_nazwa,
                COUNT(o.ocena_id) as liczba_ocen,
                NVL(ROUND(AVG(o.wartosc), 2), 0) as srednia_ocen,
                MIN(o.wartosc) as min_ocena,
                MAX(o.wartosc) as max_ocena
            FROM MAINAPP_PRZEDMIOT p
            LEFT JOIN MAINAPP_OCENA o ON p.przedmiot_id = o.przedmiot_id
            WHERE p.nauczyciel_id = :nauczyciel_id
            GROUP BY p.przedmiot_id, p.nazwa
            ORDER BY p.nazwa
        """, {'nauczyciel_id': nauczyciel_obj.nauczyciel_id})
        
        statystyki = cursor.fetchall()

    return render(request, 'mainapp/statystyki_przedmiotow.html', {
        'nauczyciel': nauczyciel_obj,
        'statystyki': statystyki
    })


@tylko_dla_nauczycieli
def eksport_ocen_csv(request):
    """Eksport ocen do pliku CSV"""
    konto_id = request.session.get('konto_id')
    
    try:
        konto_uzytkownika = Konto.objects.get(pk=konto_id)
        nauczyciel_obj = nauczyciel.objects.get(konto=konto_uzytkownika)
    except (Konto.DoesNotExist, nauczyciel.DoesNotExist):
        return redirect('konto_login')

    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="oceny_{nauczyciel_obj.nazwisko}_{datetime.now().strftime("%Y%m%d")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Student', 'Przedmiot', 'Ocena', 'Data', 'Semestr'])
    
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                s.imie || ' ' || s.nazwisko as student_name,
                p.nazwa as przedmiot,
                o.wartosc,
                TO_CHAR(o.data_wprowadzenia, 'YYYY-MM-DD HH24:MI:SS'),
                sem.nazwa as semestr
            FROM MAINAPP_OCENA o
            JOIN MAINAPP_STUDENT s ON o.student_id = s.student_id
            JOIN MAINAPP_PRZEDMIOT p ON o.przedmiot_id = p.przedmiot_id
            JOIN MAINAPP_SEMESTR sem ON o.semestr_id = sem.semestr_id
            WHERE o.nauczyciel_id = :nauczyciel_id
            ORDER BY s.nazwisko, s.imie, p.nazwa, o.data_wprowadzenia
        """, {'nauczyciel_id': nauczyciel_obj.nauczyciel_id})
        
        for row in cursor.fetchall():
            writer.writerow(row)
    
    return response


@tylko_dla_studentow
def historia_moich_ocen(request):
    """Historia zmian ocen studenta"""
    konto_id = request.session.get('konto_id')

    try:
        konto_uzytkownika = Konto.objects.get(pk=konto_id)
        student_obj = Student.objects.get(konto=konto_uzytkownika)
    except (Konto.DoesNotExist, Student.DoesNotExist):
        return redirect('konto_login')

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                p.nazwa as przedmiot,
                o.wartosc as aktualna_ocena,
                h.wartosc as poprzednia_ocena,
                TO_CHAR(h.data_zmiany, 'YYYY-MM-DD HH24:MI:SS') as data_zmiany,
                n.imie || ' ' || n.nazwisko as nauczyciel
            FROM MAINAPP_HISTORIA_OCEN h
            JOIN MAINAPP_OCENA o ON h.ocena_id = o.ocena_id
            JOIN MAINAPP_PRZEDMIOT p ON o.przedmiot_id = p.przedmiot_id
            JOIN MAINAPP_NAUCZYCIEL n ON h.nauczyciel_id = n.nauczyciel_id
            WHERE o.student_id = :student_id
            ORDER BY h.data_zmiany DESC
        """, {'student_id': student_obj.student_id})
        
        historia = cursor.fetchall()

    return render(request, 'mainapp/historia_ocen.html', {
        'student': student_obj,
        'historia': historia
    })


def statystyki_ogolne(request):
    """Ogólne statystyki systemu - dostępne dla wszystkich zalogowanych"""
    rola = request.session.get('rola')
    if not rola:
        return redirect('konto_login')

    with connection.cursor() as cursor:
        # Podstawowe statystyki
        cursor.execute("SELECT COUNT(*) FROM MAINAPP_STUDENT")
        liczba_studentow = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM MAINAPP_NAUCZYCIEL")
        liczba_nauczycieli = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM MAINAPP_PRZEDMIOT")
        liczba_przedmiotow = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM MAINAPP_OCENA")
        liczba_ocen = cursor.fetchone()[0]
        
        # Średnia ocen w systemie
        cursor.execute("SELECT NVL(ROUND(AVG(wartosc), 2), 0) FROM MAINAPP_OCENA")
        srednia_systemowa = cursor.fetchone()[0]
        
        # Rozkład ocen
        cursor.execute("""
            SELECT wartosc, COUNT(*) as liczba
            FROM MAINAPP_OCENA
            GROUP BY wartosc
            ORDER BY wartosc
        """)
        rozklad_ocen = cursor.fetchall()

    return render(request, 'mainapp/statystyki_ogolne.html', {
        'liczba_studentow': liczba_studentow,
        'liczba_nauczycieli': liczba_nauczycieli,
        'liczba_przedmiotow': liczba_przedmiotow,
        'liczba_ocen': liczba_ocen,
        'srednia_systemowa': srednia_systemowa,
        'rozklad_ocen': rozklad_ocen
    })