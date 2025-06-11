from django import forms
from .models import przedmiot, semestr
from django.utils import timezone

class KontoLoginForm(forms.Form):
    konto_id = forms.IntegerField(label='ID konta')
    haslo = forms.CharField(widget=forms.PasswordInput, label='Hasło')

OCENA_CHOICES = [
    (2.0, '2'),
    (3.0, '3'),
    (3.5, '3.5'),
    (4.0, '4'),
    (4.5, '4.5'),
    (5.0, '5'),
]

class DodajOceneForm(forms.Form):
    wartosc = forms.ChoiceField(choices=OCENA_CHOICES)
    przedmiot = forms.ModelChoiceField(queryset=przedmiot.objects.all())
    semestr = forms.ModelChoiceField(queryset=semestr.objects.all())
    data_wprowadzenia = forms.DateTimeField(initial=timezone.now, widget=forms.HiddenInput())
