from form.views import CategoryViewSet
from form import views
from rest_framework.routers import DefaultRouter
from django.urls import path, include


router = DefaultRouter()
router.register(r'processes', views.ProcessViewSet, basename='process')
#router.register(r'forms', FormViewSet, basename='form')
router.register(r'categories', CategoryViewSet, basename='category')


urlpatterns = [
    path('', include(router.urls)),
    # path('processes/<int:id>/', views.ProcessDetailView.as_view(), name='process-detail'),
    path('process/<int:id>/welcome/', views.ProcessWelcomeView.as_view(), name='process-welcome'),
    path('process/<int:id>/end/', views.ProcessEndView.as_view(), name='process-end'),
    path('process/<int:id>/submit/', views.ProcessSubmitView.as_view(), name='process-submit'),
    path('user/dashboard/', views.UserDashboardView.as_view(), name='user-dashboard'),
    path('forms/', views.FormListCreateView.as_view(), name='form-list-create'),
    path('forms/<int:id>/', views.FormDetailUpdateDeleteView.as_view(), name='form-detail-update-delete'),
]

