from rest_framework import mixins, viewsets
from .models import Form
from .permissions import IsAuthenticatedFormOwner
from .serializers import FormSerializer


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