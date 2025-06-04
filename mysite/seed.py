from mainapp.models import *
from mainapp.models import Rola, TypZaliczenia, NazwaSemestru

from django.utils import timezone
from datetime import timedelta, date
import random

# Czyszczenie
student_grupa.objects.all().delete()
grupa_zajeciowa.objects.all().delete()
historia_ocen.objects.all().delete()
ocena.objects.all().delete()
zaliczenie.objects.all().delete()
semestr.objects.all().delete()
przedmiot.objects.all().delete()
student.objects.all().delete()
nauczyciel.objects.all().delete()
konto.objects.all().delete()

# Konta studentów
konta_studentow = [
    konto.objects.create(login=f'student{i}', haslo='123', rola=Rola.STUDENT)
    for i in range(100)
]

# Konta nauczycieli
konta_nauczycieli = [
    konto.objects.create(login=f'nauczyciel{i}', haslo='123', rola=Rola.NAUCZYCIEL)
    for i in range(20)
]

# Konto admina
konto_admin = konto.objects.create(login='admin', haslo='admin', rola=Rola.ADMIN)

# Nauczyciele
nauczyciele = [
    nauczyciel.objects.create(imie=f'Imie{i}', nazwisko=f'Nauczyciel{i}', tytul='dr', konto=k)
    for i, k in enumerate(konta_nauczycieli)
]

# Studenci
studenci = [
    student.objects.create(imie=f'Jan{i}', nazwisko=f'Nowak{i}', kierunek='Informatyka', rok_studiow=random.randint(1, 3), konto=k)
    for i, k in enumerate(konta_studentow)
]

# Semestry
semestry = [
    semestr.objects.create(nazwa=NazwaSemestru.ZIMOWY, data_rozpoczecia=date(2023, 10, 1), data_zakonczenia=date(2024, 2, 15)),
    semestr.objects.create(nazwa=NazwaSemestru.LETNI, data_rozpoczecia=date(2024, 3, 1), data_zakonczenia=date(2024, 7, 1)),
]

# Przedmioty
przedmioty = [
    przedmiot.objects.create(nazwa=f'Przedmiot {i}', nauczyciel=random.choice(nauczyciele), kierunek='Informatyka', rok_studiow=random.randint(1, 3))
    for i in range(10)
]

# Grupy zajęciowe
grupy = [
    grupa_zajeciowa.objects.create(nazwa=f'Grupa {i}', przedmiot=random.choice(przedmioty))
    for i in range(20)
]


for s in studenci:
    grupa = random.choice(grupy)
    student_grupa.objects.create(student=s, grupa=grupa)


# Oceny
oceny = []
for _ in range(200):
    s = random.choice(studenci)
    p = random.choice(przedmioty)
    sem = random.choice(semestry)
    n = p.nauczyciel
    o = ocena.objects.create(
        wartosc=random.choice([2.0, 3.0, 3.5, 4.0, 4.5, 5.0]),
        student=s,
        przedmiot=p,
        nauczyciel=n,
        semestr=sem,
        data_wprowadzenia=timezone.now()
    )
    oceny.append(o)

# Historia ocen (dla 50 ocen)
for o in random.sample(oceny, 50):
    historia_ocen.objects.create(
        ocena=o,
        wartosc=max(2.0, o.wartosc - 0.5),
        data_zmiany=o.data_wprowadzenia - timedelta(days=random.randint(1, 30)),
        nauczyciel=o.nauczyciel
    )

# Zaliczenia (dla każdego przedmiotu 1–2)
for p in przedmioty:
    for _ in range(random.randint(1, 2)):
        zaliczenie.objects.create(
            przedmiot=p,
            typ=random.choice([t[0] for t in TypZaliczenia.choices]),
            data=timezone.now() - timedelta(days=random.randint(0, 90))
        )
