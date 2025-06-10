# forms.py
from django import forms

class KontoLoginForm(forms.Form):
    konto_id = forms.IntegerField(label='ID konta')
    haslo = forms.CharField(widget=forms.PasswordInput, label='Hasło')
