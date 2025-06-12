from django.contrib import admin
from .models import (
    konto, nauczyciel, student, przedmiot, semestr, ocena,
    historia_ocen, zaliczenie, grupa_zajeciowa, student_grupa
)
from django import forms
from django.contrib.auth.hashers import make_password


# FORMULARZ DO ZMIANY HASŁA W ADMINIE
class KontoAdminForm(forms.ModelForm):
    class Meta:
        model = konto
        fields = '__all__'
    
    def clean_haslo(self):
        haslo = self.cleaned_data['haslo']
        if not haslo.startswith('pbkdf2_'):  # haszuj tylko jeśli nie jest zahashowane
            return make_password(haslo)
        return haslo


@admin.register(konto)
class KontoAdmin(admin.ModelAdmin):
    form = KontoAdminForm
    list_display = ('konto_id', 'login', 'rola')
    search_fields = ('login',)
    list_filter = ('rola',)


@admin.register(nauczyciel)
class NauczycielAdmin(admin.ModelAdmin):
    list_display = ('nauczyciel_id', 'imie', 'nazwisko', 'tytul', 'konto')
    search_fields = ('nazwisko', 'imie')
    list_filter = ('tytul',)


@admin.register(student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'imie', 'nazwisko', 'kierunek', 'rok_studiow', 'konto')
    search_fields = ('nazwisko', 'imie', 'kierunek')
    list_filter = ('kierunek', 'rok_studiow')


@admin.register(przedmiot)
class PrzedmiotAdmin(admin.ModelAdmin):
    list_display = ('przedmiot_id', 'nazwa', 'nauczyciel', 'kierunek', 'rok_studiow')
    search_fields = ('nazwa', 'kierunek')
    list_filter = ('kierunek', 'rok_studiow')


@admin.register(semestr)
class SemestrAdmin(admin.ModelAdmin):
    list_display = ('semestr_id', 'nazwa', 'data_rozpoczecia', 'data_zakonczenia')
    list_filter = ('nazwa',)


@admin.register(ocena)
class OcenaAdmin(admin.ModelAdmin):
    list_display = ('ocena_id', 'wartosc', 'student', 'przedmiot', 'nauczyciel', 'semestr', 'data_wprowadzenia')
    list_filter = ('semestr', 'nauczyciel', 'przedmiot')
    search_fields = ('student__nazwisko', 'przedmiot__nazwa')


@admin.register(historia_ocen)
class HistoriaOcenAdmin(admin.ModelAdmin):
    list_display = ['historia_id', 'ocena', 'wartosc', 'data_zmiany', 'nauczyciel']
    list_filter = ('nauczyciel',)


@admin.register(zaliczenie)
class ZaliczenieAdmin(admin.ModelAdmin):
    list_display = ('zaliczenie_id', 'przedmiot', 'typ', 'data')
    list_filter = ('typ',)
    search_fields = ('przedmiot__nazwa',)


@admin.register(grupa_zajeciowa)
class GrupaZajeciowaAdmin(admin.ModelAdmin):
    list_display = ('grupa_id', 'nazwa', 'przedmiot')
    search_fields = ('nazwa',)


@admin.register(student_grupa)
class StudentGrupaAdmin(admin.ModelAdmin):
    list_display = ('student', 'grupa')
    list_filter = ('grupa',)
    search_fields = ('student__nazwisko', 'grupa__nazwa')