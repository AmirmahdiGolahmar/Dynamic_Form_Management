from django.urls import path
from .views import ProcessSettingsUpdateView

urlpatterns = [
    path('processes/<int:pk>/settings/', ProcessSettingsUpdateView.as_view(), name='process-settings-update'),
]
