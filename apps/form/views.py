from django.db import models
from rest_framework import generics
from rest_framework import permissions
from form.serializers import ProcessDetailSerializer,ProcessWelcomeSerializer
from form.models import Process

# Create your views here.

# --------------------------------------------
# (Process Detail)
# --------------------------------------------
class ProcessDetailView(generics.RetrieveAPIView):
    serializer_class = ProcessDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'
    def get_queryset(self):
        user = self.request.user
        return Process.objects.filter(
            models.Q(is_public=True) | models.Q(creator=user)
        )

# --------------------------------------------
# (Process Welcome Page)
# --------------------------------------------
class ProcessWelcomeView(generics.RetrieveAPIView):
    serializer_class = ProcessWelcomeSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        user = self.request.user
        return Process.objects.filter(
            models.Q(is_public=True) | models.Q(creator=user)
        )