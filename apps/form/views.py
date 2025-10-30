# views.py
from rest_framework import mixins, viewsets, filters
from .models import Form, Category
from .permissions import IsAuthenticatedFormOwner, IsAuthenticatedCategoryOwner
from .serializers import FormSerializer, CategorySerializer

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


class FormViewSet(mixins.CreateModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin,
                  viewsets.GenericViewSet):
    """ViewSet allowing creators to manage their forms."""
    serializer_class = FormSerializer
    permission_classes = [IsAuthenticatedFormOwner]
    http_method_names = ['post', 'put', 'patch', 'delete']

    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return Form.objects.none()
        return Form.objects.filter(creator=user)

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)
