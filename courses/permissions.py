from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsInstructor(BasePermission):
    """
    Allow only authenticated instructors (or staff/superuser).
    """
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        if getattr(user, "is_staff", False) or getattr(user, "is_superuser", False):
            return True

        return getattr(user, "role", "") == "instructor"


class IsOwnerInstructorOrReadOnly(BasePermission):
    """
    Read for everyone, write only for the instructor who owns the course.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return getattr(obj, "instructor", None) == request.user