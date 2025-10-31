from django.db import models
from rest_framework import generics
from rest_framework import permissions
from form.serializers import (
    ProcessDetailSerializer,
    ProcessBuildSerializer,
    FormListSerializer,
    FormDetailSerializer,
    FormCreateUpdateSerializer,
)
from form.models import Process, Form

# Create your views here.

# --------------------------------------------
# (Form CRUD)
# --------------------------------------------


class IsFormOwnerOrAdmin(permissions.BasePermission):
    """
    Only the form creator or an admin user can modify or delete a form.
    Regular users can only see their own forms.
    """
    def has_object_permission(self, request, view, obj):
        if request.user and (request.user.is_staff or request.user.is_superuser):
            return True
        return getattr(obj, 'creator_id', None) == getattr(request.user, 'id', None)


# --------------------------------------------
# (Form List & Create)
# --------------------------------------------
class FormListCreateView(generics.ListCreateAPIView):
    """
    GET  /forms/      → list all forms for current user
    POST /forms/      → create a new form (with optional question)
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # Normal users only see their own forms
        return Form.objects.select_related('creator', 'category').filter(creator=user)

    def get_serializer_class(self):
        # Use Create/Update serializer for POST, List serializer for GET
        return FormCreateUpdateSerializer if self.request.method == 'POST' else FormListSerializer

    def perform_create(self, serializer):
        serializer.save()  # creator is set inside serializer


# --------------------------------------------
# (Form Retrieve / Update / Delete)
# --------------------------------------------
class FormDetailUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /forms/<id>/ → retrieve form + question
    PATCH  /forms/<id>/ → partial update (form + question inline)
    PUT    /forms/<id>/ → full update (optional)
    DELETE /forms/<id>/ → delete form and cascade to question/answers
    """
    permission_classes = [permissions.IsAuthenticated, IsFormOwnerOrAdmin]
    lookup_field = 'id'

    def get_queryset(self):
        user = self.request.user
        qs = Form.objects.select_related('creator', 'category')
        if user.is_staff or user.is_superuser:
            return qs
        return qs.filter(creator=user)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return FormDetailSerializer
        return FormCreateUpdateSerializer


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
# (Process Build)
# --------------------------------------------


class ProcessBuildView(generics.CreateAPIView):
    serializer_class = ProcessBuildSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Process.objects.filter(creator=self.request.user)