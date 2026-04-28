from rest_framework.permissions import BasePermission, SAFE_METHODS

from .utils import is_instructor_user


class IsInstructorOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated and is_instructor_user(request.user))


class IsInstructor(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and is_instructor_user(request.user))
