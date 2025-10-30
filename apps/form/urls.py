from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FormViewSet

router = DefaultRouter()
router.register(r'forms', FormViewSet, basename='form')

urlpatterns = [
    path('', include(router.urls)),
]
