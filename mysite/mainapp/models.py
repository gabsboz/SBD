from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone
# ENUMY (czyli stałe wartości, żeby nie wpisywać stringów na sztywno)
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


# MODELE:

class konto(models.Model):
    konto_id = models.AutoField(primary_key=True)
    login = models.CharField(max_length=255, unique=True)
    haslo = models.CharField(max_length=255)
    rola = models.CharField(max_length=20, choices=Rola.choices)
    last_login = models.DateTimeField(default=timezone.now) 
    def save(self, *args, **kwargs):
        # Haszuj hasło tylko jeśli nie jest już zahashowane
        if not self.haslo.startswith('pbkdf2_'):
            self.haslo = make_password(self.haslo)
        super().save(*args, **kwargs)

    def check_password(self, raw_password):
        # Metoda do sprawdzenia hasła — użyteczne w loginie
        return check_password(raw_password, self.haslo)

    def __str__(self):
        return self.login
    
    @property
    def is_authenticated(self):
        return True
    
    @property
    def is_active(self):
        return True  # lub jakąś logikę
    
    @property
    def is_staff(self):
        return self.rola == 'admin'  # tylko admin ma dostęp do admina
    
    @property
    def is_superuser(self):
        return self.rola == 'admin'  # jeśli chcesz
    
    def has_perm(self, perm, obj=None):
        # Proste rozwiązanie: każdy admin ma wszystkie uprawnienia
        return self.is_staff

    def has_module_perms(self, app_label):
        # Podobnie, dostęp do modułu jeśli jest adminem
        return self.is_staff
    
    def get_username(self):
        return self.login
    


class nauczyciel(models.Model):
    nauczyciel_id = models.AutoField(primary_key=True)
    imie = models.CharField(max_length=255)
    nazwisko = models.CharField(max_length=255)
    tytul = models.CharField(max_length=255)
    konto = models.ForeignKey(konto, on_delete=models.CASCADE)
    # powiązanie z kontem, przy usunięciu konta idzie też nauczyciel
    def __str__(self):
            return str(self.nauczyciel_id)

class student(models.Model):
    student_id = models.AutoField(primary_key=True)
    imie = models.CharField(max_length=255)
    nazwisko = models.CharField(max_length=255)
    kierunek = models.CharField(max_length=255)
    rok_studiow = models.IntegerField()
    konto = models.ForeignKey(konto, on_delete=models.CASCADE)
    # analogicznie jak u nauczyciela
    def __str__(self):
        return str(self.student_id)


class przedmiot(models.Model):
    przedmiot_id = models.AutoField(primary_key=True)
    nazwa = models.CharField(max_length=255)
    nauczyciel = models.ForeignKey(nauczyciel, on_delete=models.CASCADE)
    kierunek = models.CharField(max_length=255)
    rok_studiow = models.IntegerField()

    def __str__(self):
        return self.nazwa


class semestr(models.Model):
    semestr_id = models.AutoField(primary_key=True)
    nazwa = models.CharField(max_length=10, choices=NazwaSemestru.choices)
    data_rozpoczecia = models.DateField()
    data_zakonczenia = models.DateField()

    def __str__(self):
        return self.nazwa


class ocena(models.Model):
    ocena_id = models.AutoField(primary_key=True)
    wartosc = models.DecimalField(max_digits=4, decimal_places=2)  # np. 4.5
    student = models.ForeignKey(student, on_delete=models.CASCADE)
    przedmiot = models.ForeignKey(przedmiot, on_delete=models.CASCADE)
    data_wprowadzenia = models.DateTimeField()
    nauczyciel = models.ForeignKey(nauczyciel, on_delete=models.CASCADE)
    semestr = models.ForeignKey(semestr, on_delete=models.CASCADE)
    # ocena powiązana z konkretnym studentem, przedmiotem, nauczycielem i semestrem
    def __str__(self):
        return str(self.ocena_id)

class historia_ocen(models.Model):
    historia_id = models.AutoField(primary_key=True)
    ocena = models.ForeignKey(ocena, on_delete=models.CASCADE)
    wartosc = models.DecimalField(max_digits=4, decimal_places=2)
    data_zmiany = models.DateTimeField()
    nauczyciel = models.ForeignKey(nauczyciel, on_delete=models.CASCADE)
    # zapis zmian oceny, kto i kiedy zmienił


class zaliczenie(models.Model):
    zaliczenie_id = models.AutoField(primary_key=True)
    przedmiot = models.ForeignKey(przedmiot, on_delete=models.CASCADE)
    typ = models.CharField(max_length=20, choices=TypZaliczenia.choices)
    data = models.DateTimeField()
    # zaliczenie z określonym typem (egzamin, projekt itp.)


class grupa_zajeciowa(models.Model):
    grupa_id = models.AutoField(primary_key=True)
    nazwa = models.CharField(max_length=255)
    przedmiot = models.ForeignKey(przedmiot, on_delete=models.CASCADE)
    # grupa powiązana z przedmiotem
    def __str__(self):
        return f"{self.grupa_id} - {self.nazwa}"



class student_grupa(models.Model):
    student = models.ForeignKey(student, on_delete=models.CASCADE)
    grupa = models.ForeignKey(grupa_zajeciowa, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('student', 'grupa')  # jeden student może być tylko raz w danej grupie
