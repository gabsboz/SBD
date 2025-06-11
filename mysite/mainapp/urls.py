from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StudentViewSet, OcenaViewSet, LoginAPIView, RankingAPIView

router = DefaultRouter()
router.register(r'studenci', StudentViewSet)
router.register(r'oceny', OcenaViewSet)

urlpatterns = [
    path('api/login/', LoginAPIView.as_view(), name='api_login'),
    path('api/ranking/', RankingAPIView.as_view(), name='api_ranking'),
    path('api/', include(router.urls)),
]
