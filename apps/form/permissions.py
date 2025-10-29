from rest_framework import permissions


class IsAuthenticatedFormOwner(permissions.BasePermission):
    """Allow access to authenticated users who own the form instance."""

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return obj.creator_id == request.user.id