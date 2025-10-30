from rest_framework.permissions import BasePermission

class IsFormCreatorOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user and (request.user.is_staff or request.user.is_superuser):
            return True
        return getattr(obj, 'creator_id', None) == getattr(request.user, 'id', None)
