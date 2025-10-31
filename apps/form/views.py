# views.py
from .permissions import IsAuthenticatedFormOwner, IsAuthenticatedCategoryOwner
from django.db import models
from rest_framework import generics
from rest_framework import permissions
from form.serializers import (
    ProcessDetailSerializer,
    ProcessBuildSerializer,
    ProcessWelcomeSerializer,
    ProcessEndSerializer,
    ProcessSubmitSerializer, 
    ProcessSettingsSerializer,
    FormSerializer,
    CategorySerializer,
)
from rest_framework import status
from rest_framework.response import Response
from rest_framework import mixins
from rest_framework import filters
from rest_framework.views import APIView
from django.db.models import Count, Avg
from .models import Process, ProcessForm, Form, ResponseSession, Category
from rest_framework import viewsets



class CategoryViewSet(mixins.ListModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.CreateModelMixin,
                      mixins.UpdateModelMixin,
                      mixins.DestroyModelMixin,
                      viewsets.GenericViewSet):
    """CRUD for user's own categories."""
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedCategoryOwner]
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']

    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return Category.objects.none()
        return Category.objects.filter(owner=user).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)




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


class ProcessWelcomeView(generics.RetrieveAPIView):
    serializer_class = ProcessWelcomeSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        user = self.request.user
        return Process.objects.filter(
            models.Q(is_public=True) | models.Q(creator=user)
        )
    


class ProcessEndView(generics.RetrieveAPIView):
    serializer_class = ProcessEndSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        user = self.request.user
        return Process.objects.filter(
            models.Q(is_public=True) | models.Q(creator=user)
        )
    




class ProcessSubmitView(generics.RetrieveAPIView):
    serializer_class = ProcessSubmitSerializer
    permission_classes = [permissions.IsAuthenticated]  # یا AllowAny اگر عمومی می‌خوای
    lookup_field = 'id'

    def get_queryset(self):
        user = self.request.user
        return Process.objects.filter(
            models.Q(is_public=True) | models.Q(creator=user)
        )

class UserDashboardView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user

        processes = Process.objects.filter(creator=user)
        forms = Form.objects.filter(creator=user)
        submissions = ResponseSession.objects.filter(responder=user)

        total_processes = processes.count()
        total_forms = forms.count()
        total_submissions = submissions.count()

        
        public_processes = processes.filter(is_public=True).count()
        private_processes = total_processes - public_processes

        
        avg_forms_per_process = (
            ProcessForm.objects.filter(process__creator=user)
            .values('process')
            .annotate(form_count=Count('form'))
            .aggregate(average=Avg('form_count'))['average'] or 0
        )

        
        most_used_form_data = (
            ProcessForm.objects
            .filter(process__creator=user)
            .values('form__title')
            .annotate(count=Count('process'))
            .order_by('-count')
            .first()
        )
        most_used_form = most_used_form_data['form__title'] if most_used_form_data else None

        data = {
            "overview": {
                "total_processes": total_processes,
                "total_forms": total_forms,
                "total_submissions": total_submissions,
            },
            "visibility": {
                "public_processes": public_processes,
                "private_processes": private_processes,
            },
            "statistics": {
                "avg_forms_per_process": round(avg_forms_per_process, 2),
                "most_used_form": most_used_form,
            },
        }

        return Response(data, status=status.HTTP_200_OK)
