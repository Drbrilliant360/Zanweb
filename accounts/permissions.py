from rest_framework import permissions


SAFE_METHODS = ('GET', 'HEAD', 'OPTIONS')


class IsAdminRole(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_admin_role
        )


class IsCoordinatorOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_coordinator or request.user.is_admin_role
        )


class IsCoordinatorOrAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_authenticated and (
            request.user.is_coordinator or request.user.is_admin_role
        )


class IsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_admin_role:
            return True
        owner = getattr(obj, 'user', None) or getattr(obj, 'volunteer', None) or getattr(obj, 'applicant', None)
        return owner == user
