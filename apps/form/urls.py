from form import views
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'processes', views.ProcessViewSet, basename='process')
urlpatterns = router.urls