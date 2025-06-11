from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import KontoSerializer

class LoginAPIView(APIView):
    def post(self, request):
        konto_id = request.data.get('konto_id')
        haslo = request.data.get('haslo')

        if not konto_id or not haslo:
            return Response({'error': 'konto_id i haslo wymagane'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            konto = Konto.objects.get(konto_id=konto_id)
        except Konto.DoesNotExist:
            return Response({'error': 'Konto nie istnieje'}, status=status.HTTP_404_NOT_FOUND)

        if not konto.check_password(haslo):
            return Response({'error': 'Nieprawidłowe hasło'}, status=status.HTTP_401_UNAUTHORIZED)

        # ustaw sesję (jeśli chcesz)
        request.session['konto_id'] = konto.konto_id
        request.session['rola'] = konto.rola

        serializer = KontoSerializer(konto)
        return Response({'message': 'Zalogowano', 'konto': serializer.data})

from rest_framework.permissions import BasePermission

class IsStudent(BasePermission):
    def has_permission(self, request, view):
        return request.session.get('rola') == 'student'

class IsNauczyciel(BasePermission):
    def has_permission(self, request, view):
        return request.session.get('rola') == 'nauczyciel'

class RankingAPIView(APIView):

    def get(self, request):
        rola = request.session.get('rola')
        if rola not in ['student', 'nauczyciel']:
            return Response({'error': 'Nieautoryzowany'}, status=status.HTTP_401_UNAUTHORIZED)

        with connection.cursor() as cursor:
            refcursor = cursor.var(oracledb.DB_TYPE_CURSOR)

            cursor.execute("""
                BEGIN
                    :refcursor := ranking;
                END;
            """, {'refcursor': refcursor})

            result_cursor = refcursor.getvalue()
            ranking_data = result_cursor.fetchall()

        ranking_list = []
        for idx, (student_id, srednia) in enumerate(ranking_data, start=1):
            ranking_list.append({
                'pozycja': idx,
                'student_id': student_id,
                'srednia': srednia,
            })

        if rola == 'student':
            konto_id = request.session.get('konto_id')
            try:
                konto = Konto.objects.get(pk=konto_id)
                student = Student.objects.get(konto=konto)
            except (Konto.DoesNotExist, Student.DoesNotExist):
                return Response({'error': 'Konto lub student nie znalezione'}, status=status.HTTP_401_UNAUTHORIZED)

            moje_miejsce = None
            moja_srednia = 0
            for r in ranking_list:
                if r['student_id'] == student.student_id:
                    moje_miejsce = r['pozycja']
                    moja_srednia = r['srednia']
                    break

            return Response({'moje_miejsce': moje_miejsce, 'moja_srednia': moja_srednia})

        elif rola == 'nauczyciel':
            return Response({'ranking': ranking_list})

