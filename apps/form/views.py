from django.db import models
from rest_framework import generics
from rest_framework import permissions
from form.serializers import ProcessDetailSerializer
from form.models import Process

# Create your views here.

class ProcessDetailView(generics.RetrieveAPIView):
    serializer_class = ProcessDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'
    def get_queryset(self):
        user = self.request.user
        return Process.objects.filter(
            models.Q(is_public=True) | models.Q(creator=user)
        )
