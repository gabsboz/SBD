from django.http import JsonResponse
from django.urls import path, include
from django.shortcuts import redirect
from . import views
from .views import lista_studentow, oceny_studenta


# Funkcja przekierowująca na odpowiedni dashboard w zależności od roli użytkownika
def home_redirect(request):
    if request.session.get('konto_id'):
        # jeśli jesteś zalogowany, lecisz na swój dashboard
        if request.session.get('rola') == 'student':
            return redirect('student_dashboard')
        else:
            # tu zakładam, że rola nauczyciela lub inna — przekieruj na nauczyciela
            return redirect('nauczyciel_dashboard')
    else:
        # nie jesteś zalogowany, więc na stronę logowania
        return redirect('konto_login')


urlpatterns = [
    # Strona startowa - przekierowanie według zalogowania i roli
    path('', home_redirect, name='home_redirect'),

    # Ścieżki do widoków związanych ze studentami i ocenami
    path('studenci/', lista_studentow, name='lista_studentow'),
    path('oceny/<int:student_id>/', oceny_studenta, name='oceny_studenta'),

    # Logowanie i wylogowanie
    path('login/', views.konto_login, name='konto_login'),
    path('logout/', views.konto_logout, name='konto_logout'),

    # Dashboardy użytkowników według ról
    path('student_dashboard/', views.student_dashboard, name='student_dashboard'),
    path('moje-oceny/', views.moje_oceny, name='moje_oceny'),
    path('nauczyciel_dashboard/', views.nauczyciel_dashboard, name='nauczyciel_dashboard'),

    # Ranking uczniów
    path('ranking/', views.ranking_view, name='ranking_view'),

    # Widok grup studenta
    path('moje_grupy/', views.moje_grupy, name='moje_grupy'),

    # Tutaj możesz dodać inne endpointy, jeśli będziesz potrzebować
]
