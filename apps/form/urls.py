from django.urls import path
from form import views


urlpatterns = [
    path('processes/<int:id>/', views.ProcessDetailView.as_view(), name='process-detail'),
    path('process/build/', views.ProcessBuildView.as_view(), name='process-build'),
    path('forms/', views.FormListCreateView.as_view(), name='form-list-create'),
    path('forms/<int:id>/', views.FormDetailUpdateDeleteView.as_view(), name='form-detail-update-delete'),
]