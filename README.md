# 📚 Projekt SBD – Aplikacja Django do zarządzania ocenami studentów

## 🛠️ Funkcje SQL

W projekcie wykorzystano funkcję Oracle do pobierania ocen studenta przy użyciu `SYS_REFCURSOR`. Funkcja może być wykorzystywana np. przez Django poprzez `cursor.callproc`.

### 🔽 `get_student_grades`

```sql
CREATE OR REPLACE FUNCTION get_student_grades(p_student_id IN NUMBER) RETURN SYS_REFCURSOR IS
  grades_cursor SYS_REFCURSOR;
BEGIN
  OPEN grades_cursor FOR
    SELECT o.OCENA_ID, o.wartosc, o.DATA_WPROWADZENIA, p.nazwa AS przedmiot
    FROM MAINAPP_OCENA o
    JOIN MAINAPP_PRZEDMIOT p ON o.przedmiot_id = p.przedmiot_id
    WHERE o.student_id = p_student_id;
  RETURN grades_cursor;
END;
```
### 🔽 `ranking`
```sql
create or replace FUNCTION ranking
RETURN SYS_REFCURSOR
AS
    wynik SYS_REFCURSOR;
BEGIN
    OPEN wynik FOR 
        SELECT *
        FROM (
            SELECT s.student_id, NVL(ROUND(AVG(o.wartosc), 2), 0) AS srednia
            FROM MAINAPP_STUDENT s
            LEFT JOIN MAINAPP_OCENA o ON o.STUDENT_ID = s.STUDENT_ID
            GROUP BY s.student_id
        ) ranked
        ORDER BY ranked.srednia DESC;
    RETURN wynik;
END;
```
### 🔽 `dodawania ocen`
```sql
create or replace PROCEDURE add_ocena (
    p_wartosc NUMBER,
    p_student_id NUMBER,
    p_przedmiot_id NUMBER,
    p_data_wprowadzenia DATE,
    p_nauczyciel_id NUMBER,
    p_semestr_id NUMBER
)
IS
BEGIN
    INSERT INTO MAINAPP_OCENA (
        wartosc, student_id, przedmiot_id, data_wprowadzenia, nauczyciel_id, semestr_id
    ) VALUES (
        p_wartosc, p_student_id, p_przedmiot_id, p_data_wprowadzenia, p_nauczyciel_id, p_semestr_id
    );

    COMMIT;
END;
```
### 🔽 `gr studenta`
```sql
CREATE OR REPLACE FUNCTION get_student_groups(p_student_id IN NUMBER)
RETURN SYS_REFCURSOR
AS
    rc SYS_REFCURSOR;
BEGIN
    OPEN rc FOR
        SELECT p.nazwa AS przedmiot_nazwa,
               g.nazwa AS grupa_nazwa
        FROM student_grupa sg
        JOIN grupa_zajeciowa g ON sg.grupa_id = g.grupa_id
        JOIN przedmiot p ON g.przedmiot_id = p.przedmiot_id
        WHERE sg.student_id = p_student_id;

    RETURN rc;
END;
/

```