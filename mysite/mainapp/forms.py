from django import forms
from .models import przedmiot, semestr, grupa_zajeciowa, student_grupa
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
    przedmiot = forms.ModelChoiceField(queryset=przedmiot.objects.none())  # domyślnie puste
    semestr = forms.ModelChoiceField(queryset=semestr.objects.all())
    data_wprowadzenia = forms.DateTimeField(initial=timezone.now, widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        student_id = kwargs.pop('student_id', None)
        super().__init__(*args, **kwargs)

        if student_id is not None:
            self.fields['przedmiot'].queryset = przedmiot.objects.filter(
                przedmiot_id__in=grupa_zajeciowa.objects.filter(
                    student_grupa__student_id=student_id
                ).values_list('przedmiot_id', flat=True)
            )
