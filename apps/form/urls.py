from django.urls import path
from form import views


urlpatterns = [
    path('processes/<int:id>/', views.ProcessDetailView.as_view(), name='process-detail'),
    path('process/<int:id>/welcome/', views.ProcessWelcomeView.as_view(), name='process-welcome'),
    path('process/<int:id>/end/', views.ProcessEndView.as_view(), name='process-end'),
    path('process/<int:id>/submit/', views.ProcessSubmitView.as_view(), name='process-submit'),


]


urlpatterns = [
    path('processes/<int:pk>/settings/', ProcessSettingsUpdateView.as_view(), name='process-settings-update'),
    path('processes/<int:pk>/delete/', ProcessDeleteView.as_view(), name='process-delete'),
    path('user/dashboard/', UserDashboardView.as_view(), name='user-dashboard'),
]
