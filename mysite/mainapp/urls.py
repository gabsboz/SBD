from django.http import JsonResponse
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StudentViewSet, OcenaViewSet
from .views import lista_studentow,oceny_studenta

router = DefaultRouter()
router.register(r'studenci', StudentViewSet)
router.register(r'oceny', OcenaViewSet)

def api_root(request):
    return JsonResponse({'message': 'API działa!'})

urlpatterns = [
    path('', api_root),   # root path z prostym komunikatem
    path('api/', include(router.urls)),
    path('studenci/', lista_studentow, name='lista_studentow'),
    path('oceny/<int:student_id>/', oceny_studenta, name='oceny_studenta'),

]
