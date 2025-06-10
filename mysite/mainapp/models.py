from django.db import models
from django.contrib.auth.hashers import make_password

# ENUMY
class Rola(models.TextChoices):
    STUDENT = 'student', 'student'
    NAUCZYCIEL = 'nauczyciel', 'nauczyciel'
    ADMIN = 'admin', 'admin'

class TypZaliczenia(models.TextChoices):
    EGZAMIN = 'egzamin', 'egzamin'
    KOLOKWIUM = 'kolokwium', 'kolokwium'
    PROJEKT = 'projekt', 'projekt'

class NazwaSemestru(models.TextChoices):
    LETNI = 'letni', 'letni'
    ZIMOWY = 'zimowy', 'zimowy'

# MODELE

class konto(models.Model):
    konto_id = models.AutoField(primary_key=True)
    login = models.CharField(max_length=255)
    haslo = models.CharField(max_length=255)
    rola = models.CharField(max_length=20, choices=Rola.choices)
    def save(self, *args, **kwargs):
        if not self.haslo.startswith('pbkdf2_'):
            self.haslo = make_password(self.haslo)
        super().save(*args, **kwargs)


class nauczyciel(models.Model):
    nauczyciel_id = models.AutoField(primary_key=True)
    imie = models.CharField(max_length=255)
    nazwisko = models.CharField(max_length=255)
    tytul = models.CharField(max_length=255)
    konto = models.ForeignKey(konto, on_delete=models.CASCADE)

class student(models.Model):
    student_id = models.AutoField(primary_key=True)
    imie = models.CharField(max_length=255)
    nazwisko = models.CharField(max_length=255)
    kierunek = models.CharField(max_length=255)
    rok_studiow = models.IntegerField()
    konto = models.ForeignKey(konto, on_delete=models.CASCADE)

class przedmiot(models.Model):
    przedmiot_id = models.AutoField(primary_key=True)
    nazwa = models.CharField(max_length=255)
    nauczyciel = models.ForeignKey(nauczyciel, on_delete=models.CASCADE)
    kierunek = models.CharField(max_length=255)
    rok_studiow = models.IntegerField()

class semestr(models.Model):
    semestr_id = models.AutoField(primary_key=True)
    nazwa = models.CharField(max_length=10, choices=NazwaSemestru.choices)
    data_rozpoczecia = models.DateField()
    data_zakonczenia = models.DateField()

class ocena(models.Model):
    ocena_id = models.AutoField(primary_key=True)
    wartosc = models.DecimalField(max_digits=4, decimal_places=2)
    student = models.ForeignKey(student, on_delete=models.CASCADE)
    przedmiot = models.ForeignKey(przedmiot, on_delete=models.CASCADE)
    data_wprowadzenia = models.DateTimeField()
    nauczyciel = models.ForeignKey(nauczyciel, on_delete=models.CASCADE)
    semestr = models.ForeignKey(semestr, on_delete=models.CASCADE)
    

class historia_ocen(models.Model):
    historia_id = models.AutoField(primary_key=True)
    ocena = models.ForeignKey(ocena, on_delete=models.CASCADE)
    wartosc = models.DecimalField(max_digits=4, decimal_places=2)
    data_zmiany = models.DateTimeField()
    nauczyciel = models.ForeignKey(nauczyciel, on_delete=models.CASCADE)
 

class zaliczenie(models.Model):
    zaliczenie_id = models.AutoField(primary_key=True)
    przedmiot = models.ForeignKey(przedmiot, on_delete=models.CASCADE)
    typ = models.CharField(max_length=20, choices=TypZaliczenia.choices)
    data = models.DateTimeField()

class grupa_zajeciowa(models.Model):
    grupa_id = models.AutoField(primary_key=True)
    nazwa = models.CharField(max_length=255)
    przedmiot = models.ForeignKey(przedmiot, on_delete=models.CASCADE)

class student_grupa(models.Model):
    student = models.ForeignKey(student, on_delete=models.CASCADE)
    grupa = models.ForeignKey(grupa_zajeciowa, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('student', 'grupa')
        