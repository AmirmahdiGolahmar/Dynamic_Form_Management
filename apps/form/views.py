from django.db import models
from rest_framework import generics
from rest_framework import permissions
from form.serializers import (
    ProcessDetailSerializer,
    ProcessBuildSerializer,
)
from form.models import Process
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status

# Create your views here.

# # --------------------------------------------
# # (Process Detail)
# # --------------------------------------------
# class ProcessDetailView(generics.RetrieveAPIView):
#     serializer_class = ProcessDetailSerializer
#     permission_classes = [permissions.IsAuthenticated]
#     lookup_field = 'id'
#     def get_queryset(self):s
#         user = self.request.user
#         return Process.objects.filter(
#             models.Q(is_public=True) | models.Q(creator=user)
#         )
    


# # --------------------------------------------
# # (Process Build)
# # --------------------------------------------


# class ProcessBuildView(generics.CreateAPIView):
#     serializer_class = ProcessBuildSerializer
#     permission_classes = [permissions.IsAuthenticated]

#     def get_queryset(self):
#         return Process.objects.filter(creator=self.request.user)

class ProcessViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        user = self.request.user
        return Process.objects.filter(
            models.Q(is_public=True) | models.Q(creator=user)
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {'message': 'Process deleted successfully.'},
            status=status.HTTP_204_NO_CONTENT,
        )

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ProcessBuildSerializer
        return ProcessDetailSerializer