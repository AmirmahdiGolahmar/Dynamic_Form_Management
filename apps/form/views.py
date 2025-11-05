from django.db import models, transaction
from django.utils import timezone
from rest_framework import generics, permissions, status, mixins, filters, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError, PermissionDenied

from .permissions import IsAuthenticatedFormOwner, IsAuthenticatedCategoryOwner
from .models import Process, ProcessForm, Form, ResponseSession, Category, Question, Answer

from form.serializers import (
    # Forms
    FormDetailSerializer,
    FormListSerializer,
    FormCreateUpdateSerializer,
    CategorySerializer,

    # Process
    ProcessDetailSerializer,
    ProcessBuildSerializer,

    # Process page titles
    ProcessWelcomeSerializer,
    ProcessEndSerializer,

    # Submit flow
    ProcessSubmitRequestSerializer,
    ProcessSubmitResponseSerializer,
)


# --------------------------------------------
# Helpers / permissions
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
# Form List & Create
# --------------------------------------------
class FormListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Form.objects.select_related('creator', 'category').filter(creator=user)

    def get_serializer_class(self):
        return FormCreateUpdateSerializer if self.request.method == 'POST' else FormListSerializer

    def perform_create(self, serializer):
        serializer.save()


# --------------------------------------------
# Form Retrieve / Update / Delete
# --------------------------------------------
class FormDetailUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, IsFormOwnerOrAdmin]
    lookup_field = 'id'

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'message': 'Form deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)

    def get_queryset(self):
        user = self.request.user
        qs = Form.objects.select_related('creator', 'category')
        if user.is_staff or user.is_superuser:
            return qs
        return qs.filter(creator=user)

    def get_serializer_class(self):
        return FormDetailSerializer if self.request.method == 'GET' else FormCreateUpdateSerializer


# --------------------------------------------
# Category CRUD
# --------------------------------------------
class CategoryViewSet(mixins.ListModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.CreateModelMixin,
                      mixins.UpdateModelMixin,
                      mixins.DestroyModelMixin,
                      viewsets.GenericViewSet):
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

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'message': 'Category deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)


# --------------------------------------------
# Process ViewSet (build/read)
# --------------------------------------------
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
        return Response({'message': 'Process deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ProcessBuildSerializer
        return ProcessDetailSerializer


# --------------------------------------------
# Process detail (GET)
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
# Process pages: Welcome / End (POST-only)
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




class ProcessEndView(generics.RetrieveAPIView):
    serializer_class = ProcessEndSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        user = self.request.user
        return Process.objects.filter(
            models.Q(is_public=True) | models.Q(creator=user)
        )



# --------------------------------------------
# Process Submit (POST): ذخیره همه پاسخ‌ها و ثبت Session به submitted
# --------------------------------------------
class ProcessSubmitView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'
    serializer_class = ProcessSubmitRequestSerializer

    def get_queryset(self):
        user = self.request.user
        return Process.objects.filter(models.Q(is_public=True) | models.Q(creator=user))

    def post(self, request, *args, **kwargs):
        process = self.get_object()
        if not process.is_public and process.creator_id != request.user.id and not request.user.is_staff:
            raise PermissionDenied("You cannot submit answers to this private process.")

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        answers_payload = serializer.validated_data['answers']

        process_form_ids = set(process.forms.values_list('id', flat=True))
        if not process_form_ids:
            raise ValidationError("This process has no forms to answer.")

        # Validate all form_ids belong to this process
        for item in answers_payload:
            if item['form_id'] not in process_form_ids:
                raise ValidationError(f"Form #{item['form_id']} does not belong to this process.")

        with transaction.atomic():
            session = ResponseSession.objects.create(
                process=process,
                responder=request.user,
                status='draft',
            )

            saved_count = 0
            for item in answers_payload:
                question = Question.objects.get(form_id=item['form_id'])
                Answer.objects.create(
                    response_session=session,
                    form_id=item['form_id'],
                    question=question,
                    answer_json=item['answer']
                )
                saved_count += 1

            session.status = 'submitted'
            session.submitted_at = timezone.now()
            session.save()

        response_data = {
            "session_id": session.id,
            "message": "Submission completed successfully.",
            "saved_answers": saved_count,
        }
        return Response(response_data, status=status.HTTP_201_CREATED)


# --------------------------------------------
# User dashboard (نمونه)
# --------------------------------------------
class UserDashboardView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        from django.db.models import Count, Avg

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
