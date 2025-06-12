import oracledb
import random
import time
import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

def call_add_ocena():
    try:
        with connection.cursor() as cursor:
            student_id = random.randint(1, 100)
            wartosc = random.choice([2.0, 3.0, 3.5, 4.0, 4.5, 5.0])
            przedmiot_id = random.randint(1, 10)
            data_wprowadzenia = time.strftime('%Y-%m-%d')
            nauczyciel_id = random.randint(1, 10)
            semestr_id = random.randint(1, 2)

            cursor.execute("""
                BEGIN
                    student_pkg.add_ocena(:wartosc, :student_id, :przedmiot_id, TO_DATE(:data_wprowadzenia, 'YYYY-MM-DD'), :nauczyciel_id, :semestr_id);
                END;
            """, {
                "wartosc": wartosc,
                "student_id": student_id,
                "przedmiot_id": przedmiot_id,
                "data_wprowadzenia": data_wprowadzenia,
                "nauczyciel_id": nauczyciel_id,
                "semestr_id": semestr_id
            })
            connection.commit()
            print("Dodano ocenę")
    except Exception as e:
        print(f"Błąd w call_add_ocena: {e}")

def call_delete_ocena():
    try:
        with connection.cursor() as cursor:
            ocena_id = random.randint(1, 800)
            cursor.execute("""
                BEGIN
                    student_pkg.delete_ocena(:ocena_id);
                END;
            """, {"ocena_id": ocena_id})
            connection.commit()
            print(f"Usunięto ocenę o id {ocena_id}")
    except Exception as e:
        print(f"Błąd w call_delete_ocena: {e}")

def call_update_ocena():
    try:
        with connection.cursor() as cursor:
            ocena_id = random.randint(1, 1000)
            nowa_wartosc = random.choice([2.0, 3.0, 3.5, 4.0, 4.5, 5.0])
            cursor.execute("""
                BEGIN
                    student_pkg.update_ocena(:ocena_id, :nowa_wartosc);
                END;
            """, {"ocena_id": ocena_id, "nowa_wartosc": nowa_wartosc})
            connection.commit()
            print(f"Zaktualizowano ocenę id {ocena_id} na {nowa_wartosc}")
    except Exception as e:
        print(f"Błąd w call_update_ocena: {e}")

def call_get_student_grades():
    try:
        with connection.cursor() as cursor:
            student_id = random.randint(1, 100)
            refcursor = cursor.var(oracledb.DB_TYPE_CURSOR)
            cursor.execute("""
                BEGIN
                    :refcursor := student_pkg.get_student_grades(:student_id);
                END;
            """, {"refcursor": refcursor, "student_id": student_id})

            result_cursor = refcursor.getvalue()
            rows = result_cursor.fetchall()
            print(f"Ocen dla studenta {student_id}: {len(rows)} rekordów")
            result_cursor.close()
    except Exception as e:
        print(f"Błąd w call_get_student_grades: {e}")

def run_test():
    funcs = [call_add_ocena, call_delete_ocena, call_update_ocena, call_get_student_grades]
    start = time.time()

    for _ in range(1000):
        func = random.choice(funcs)
        func()

    print(f"Test wykonany w {time.time() - start:.2f} sekund")

if __name__ == "__main__":
    run_test()
