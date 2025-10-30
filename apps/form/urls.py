from django.urls import path
from .views import ProcessSettingsUpdateView, ProcessDeleteView, UserDashboardView

urlpatterns = [
    path('processes/<int:pk>/settings/', ProcessSettingsUpdateView.as_view(), name='process-settings-update'),
    path('processes/<int:pk>/delete/', ProcessDeleteView.as_view(), name='process-delete'),
    path('user/dashboard/', UserDashboardView.as_view(), name='user-dashboard'),
]
