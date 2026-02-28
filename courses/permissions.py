from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsInstructor(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == "instructor")

class IsOwnerInstructorOrReadOnly(BasePermission):
    """
    Read allowed for everyone.
    Write allowed only for course owner instructor.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user.is_authenticated and request.user.role == "instructor" and obj.instructor == request.user)