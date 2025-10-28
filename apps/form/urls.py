from django.urls import path
from form import views


urlpatterns = [
    path('processes/<int:id>/', views.ProcessDetailView.as_view(), name='process-detail'),
]