

## 🛠️ Funkcje SQL



### 🔽 `student_pkg`

```sql
CREATE OR REPLACE PACKAGE student_pkg AS
  FUNCTION get_student_grades(p_student_id IN NUMBER) RETURN SYS_REFCURSOR;
  FUNCTION get_student_groups(p_student_id IN NUMBER) RETURN SYS_REFCURSOR;
  FUNCTION get_student_zaliczenia(p_student_id IN NUMBER) RETURN SYS_REFCURSOR;
  FUNCTION ranking RETURN SYS_REFCURSOR;
  PROCEDURE add_ocena (
    p_wartosc NUMBER,
    p_student_id NUMBER,
    p_przedmiot_id NUMBER,
    p_data_wprowadzenia DATE,
    p_nauczyciel_id NUMBER,
    p_semestr_id NUMBER
  );
  PROCEDURE delete_ocena(p_ocena_id IN NUMBER);
END student_pkg;
/

CREATE OR REPLACE PACKAGE student_pkg AS
  FUNCTION get_student_grades(p_student_id IN NUMBER) RETURN SYS_REFCURSOR;
  FUNCTION get_student_groups(p_student_id IN NUMBER) RETURN SYS_REFCURSOR;
  FUNCTION get_student_zaliczenia(p_student_id IN NUMBER) RETURN SYS_REFCURSOR;
  FUNCTION ranking RETURN SYS_REFCURSOR;
  PROCEDURE add_ocena (
    p_wartosc NUMBER,
    p_student_id NUMBER,
    p_przedmiot_id NUMBER,
    p_data_wprowadzenia DATE,
    p_nauczyciel_id NUMBER,
    p_semestr_id NUMBER
  );
  PROCEDURE delete_ocena(p_ocena_id IN NUMBER);
    PROCEDURE update_ocena(p_ocena_id IN NUMBER, p_nowa_wartosc IN NUMBER);
END student_pkg;
/
CREATE OR REPLACE PACKAGE BODY student_pkg AS

  FUNCTION get_student_grades(p_student_id IN NUMBER) RETURN SYS_REFCURSOR IS
    rc SYS_REFCURSOR;
  BEGIN
    OPEN rc FOR
      SELECT o.ocena_id, o.wartosc, o.data_wprowadzenia, p.nazwa
      FROM mainapp_ocena o
      JOIN mainapp_przedmiot p ON o.przedmiot_id = p.przedmiot_id
      WHERE o.student_id = p_student_id;
    RETURN rc;
  END get_student_grades;

  FUNCTION get_student_groups(p_student_id IN NUMBER) RETURN SYS_REFCURSOR IS
    rc SYS_REFCURSOR;
  BEGIN
    OPEN rc FOR
      SELECT p.nazwa AS przedmiot_nazwa, g.nazwa AS grupa_nazwa
      FROM mainapp_student_grupa sg
      JOIN mainapp_grupa_zajeciowa g ON sg.grupa_id = g.grupa_id
      JOIN mainapp_przedmiot p ON g.przedmiot_id = p.przedmiot_id
      WHERE sg.student_id = p_student_id;
    RETURN rc;
  END get_student_groups;

  FUNCTION get_student_zaliczenia(p_student_id IN NUMBER) RETURN SYS_REFCURSOR IS
    rc SYS_REFCURSOR;
  BEGIN
    OPEN rc FOR
      SELECT z.zaliczenie_id, p.nazwa AS przedmiot_nazwa, z.typ, z.data
      FROM mainapp_zaliczenie z
      JOIN mainapp_przedmiot p ON z.przedmiot_id = p.przedmiot_id
      JOIN mainapp_grupa_zajeciowa g ON g.przedmiot_id = p.przedmiot_id
      JOIN mainapp_student_grupa sg ON sg.grupa_id = g.grupa_id
      WHERE sg.student_id = p_student_id
      ORDER BY z.data DESC;
    RETURN rc;
  END get_student_zaliczenia;

  FUNCTION ranking RETURN SYS_REFCURSOR IS
    rc SYS_REFCURSOR;
  BEGIN
    OPEN rc FOR
      SELECT *
      FROM (
        SELECT s.student_id,
               NVL(ROUND(AVG(o.wartosc),2), 0) AS srednia
        FROM mainapp_student s
        LEFT JOIN mainapp_ocena o ON o.student_id = s.student_id
        GROUP BY s.student_id
      ) ranked
      ORDER BY ranked.srednia DESC;
    RETURN rc;
  END ranking;

  PROCEDURE add_ocena(
    p_wartosc NUMBER,
    p_student_id NUMBER,
    p_przedmiot_id NUMBER,
    p_data_wprowadzenia DATE,
    p_nauczyciel_id NUMBER,
    p_semestr_id NUMBER
  ) IS
  BEGIN
    INSERT INTO mainapp_ocena(
      wartosc, student_id, przedmiot_id, data_wprowadzenia, nauczyciel_id, semestr_id
    ) VALUES(
      p_wartosc, p_student_id, p_przedmiot_id, p_data_wprowadzenia, p_nauczyciel_id, p_semestr_id
    );
    COMMIT;
  END add_ocena;

  PROCEDURE delete_ocena(p_ocena_id IN NUMBER) IS
  BEGIN
    DELETE FROM mainapp_ocena
     WHERE ocena_id = p_ocena_id;
    COMMIT;
  END delete_ocena;

   PROCEDURE update_ocena(p_ocena_id IN NUMBER, p_nowa_wartosc IN NUMBER) IS
  BEGIN
    UPDATE mainapp_ocena
      SET wartosc = p_nowa_wartosc
      WHERE ocena_id = p_ocena_id;

    IF SQL%ROWCOUNT = 0 THEN
      RAISE_APPLICATION_ERROR(-20001, 'Ocena nie istnieje!');
    END IF;

    COMMIT;
  END update_ocena;

END student_pkg;

```

### 🔽 `triger`
```sql
create or replace TRIGGER trg_historia_ocen
AFTER INSERT OR UPDATE OR DELETE ON MAINAPP_OCENA
FOR EACH ROW
DECLARE
    v_operacja VARCHAR2(10);
BEGIN
    IF INSERTING THEN
        v_operacja := 'INSERT';
        INSERT INTO MAINAPP_HISTORIA_OCEN (
            ocena_id, wartosc, data_zmiany, nauczyciel_id
        ) VALUES (
            :NEW.ocena_id, :NEW.wartosc, SYSDATE, :NEW.nauczyciel_id
        );
    ELSIF UPDATING THEN
        v_operacja := 'UPDATE';
        INSERT INTO MAINAPP_HISTORIA_OCEN (
            ocena_id, wartosc, data_zmiany, nauczyciel_id
        ) VALUES (
            :NEW.ocena_id, :NEW.wartosc, SYSDATE, :NEW.nauczyciel_id
        );
    ELSIF DELETING THEN
        v_operacja := 'DELETE';
        INSERT INTO MAINAPP_HISTORIA_OCEN (
            ocena_id, wartosc, data_zmiany, nauczyciel_id
        ) VALUES (
            :OLD.ocena_id, :OLD.wartosc, SYSDATE, :OLD.nauczyciel_id
        );
    END IF;
END;
```