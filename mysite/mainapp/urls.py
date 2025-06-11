from django.http import JsonResponse
from django.urls import path, include
from django.shortcuts import redirect
from . import views
from .views import  lista_studentow, oceny_studenta


def home_redirect(request):
    if request.session.get('konto_id'):
        # jesteś zalogowany, więc leć na dashboard według roli
        if request.session.get('rola') == 'student':
            return redirect('student_dashboard')
        else:
            return redirect('nauczyciel_dashboard')  # tu możesz mieć widok dla nauczyciela/admina
    else:
        return redirect('konto_login')

urlpatterns = [
    path('', home_redirect, name='home_redirect'),

    # API
    

    # Widoki webowe
    path('studenci/', lista_studentow, name='lista_studentow'),
    path('oceny/<int:student_id>/', oceny_studenta, name='oceny_studenta'),

    path('login/', views.konto_login, name='konto_login'),
    path('logout/', views.konto_logout, name='konto_logout'),

    path('student_dashboard/', views.student_dashboard, name='student_dashboard'),
    path('moje-oceny/', views.moje_oceny, name='moje_oceny'),
    path('nauczyciel_dashboard/', views.nauczyciel_dashboard, name='nauczyciel_dashboard'),
    path('ranking/', views.ranking_view, name='ranking_view'),
    
    # path('dashboard/', views.dashboard, name='dashboard'),  # dla innych ról, jeśli masz
]
