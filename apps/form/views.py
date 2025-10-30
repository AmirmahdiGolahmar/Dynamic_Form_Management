from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated
from form.models import Form
from .serializers import FormUpdateSerializer
from .permissions import IsFormCreatorOrAdmin


class FormViewSet(mixins.UpdateModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Form.objects.select_related('creator', 'category')
    serializer_class = FormUpdateSerializer
    permission_classes = [IsAuthenticated, IsFormCreatorOrAdmin]

    def get_queryset(self):
        qs = super().get_queryset()
        u = self.request.user
        if u.is_staff or u.is_superuser:
            return qs
        return qs.filter(creator=u)
