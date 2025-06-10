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