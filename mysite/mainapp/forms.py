from django import forms
from .models import przedmiot, semestr, grupa_zajeciowa, student_grupa
from django.utils import timezone

# Formularz do logowania - prosto i na temat
class KontoLoginForm(forms.Form):
    konto_id = forms.IntegerField(label='ID konta')  # ID konta jako pole liczby
    haslo = forms.CharField(widget=forms.PasswordInput, label='Hasło')  # pole hasła


# Możliwe oceny - wybór gotowy
OCENA_CHOICES = [
    (2.0, '2'),
    (3.0, '3'),
    (3.5, '3.5'),
    (4.0, '4'),
    (4.5, '4.5'),
    (5.0, '5'),
]

# Formularz do dodawania oceny
class DodajOceneForm(forms.Form):
    wartosc = forms.ChoiceField(choices=OCENA_CHOICES)  # ocena z listy
    przedmiot = forms.ModelChoiceField(queryset=przedmiot.objects.none())  # na start pusta lista przedmiotów
    semestr = forms.ModelChoiceField(queryset=semestr.objects.all())  # wybór semestru
    data_wprowadzenia = forms.DateTimeField(initial=timezone.now, widget=forms.HiddenInput())
    # data jest ukryta, ale domyślnie ustawiona na teraz (zapisz czas wpisania oceny)

    def __init__(self, *args, **kwargs):
        student_id = kwargs.pop('student_id', None)  # bierzemy ID studenta z argumentów
        super().__init__(*args, **kwargs)

        if student_id is not None:
            # ustawiamy queryset przedmiotów, które student ma w swoich grupach zajęciowych
            self.fields['przedmiot'].queryset = przedmiot.objects.filter(
                przedmiot_id__in=grupa_zajeciowa.objects.filter(
                    student_grupa__student_id=student_id
                ).values_list('przedmiot_id', flat=True)
            )
