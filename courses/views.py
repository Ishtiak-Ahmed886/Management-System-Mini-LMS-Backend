from django.db import IntegrityError
from django.shortcuts import get_object_or_404

from rest_framework import generics, permissions, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Course, Lesson, Enrollment, LessonProgress
from .serializers import (
    CourseSerializer,
    LessonSerializer,
    EnrollmentSerializer,
    LessonProgressSerializer,
)
from .permissions import IsInstructor, IsOwnerInstructorOrReadOnly


# =========================
# ✅ Course APIs
# =========================
class CourseListCreateView(generics.ListCreateAPIView):
    queryset = Course.objects.all().order_by("-created_at")
    serializer_class = CourseSerializer

    def get_permissions(self):
        # ✅ Anyone can view course list
        if self.request.method == "GET":
            return [permissions.AllowAny()]
        # ✅ Only instructor can create course
        return [IsAuthenticated(), IsInstructor()]

    def perform_create(self, serializer):
        serializer.save(instructor=self.request.user)


class CourseDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def get_permissions(self):
        # ✅ Anyone can view course details
        if self.request.method == "GET":
            return [permissions.AllowAny()]
        # ✅ Only owner instructor can update/delete
        return [IsAuthenticated(), IsOwnerInstructorOrReadOnly()]


# =========================
# ✅ Lesson APIs
# =========================
class LessonListByCourseView(generics.ListCreateAPIView):
    serializer_class = LessonSerializer

    def get_queryset(self):
        return Lesson.objects.filter(course_id=self.kwargs["course_id"]).order_by("order")

    def get_permissions(self):
        # ✅ Anyone can view lessons list
        if self.request.method == "GET":
            return [permissions.AllowAny()]
        # ✅ Only instructor can add lessons
        return [IsAuthenticated(), IsInstructor()]

    def perform_create(self, serializer):
        course = get_object_or_404(Course, id=self.kwargs["course_id"])

        # ✅ only owner instructor can add lesson
        if course.instructor != self.request.user:
            raise PermissionDenied("You can only add lessons to your own course.")

        serializer.save(course=course)


class LessonDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def get_permissions(self):
        # ✅ Anyone can view single lesson (so video open works)
        if self.request.method == "GET":
            return [permissions.AllowAny()]
        # ✅ Only instructor can update/delete
        return [IsAuthenticated(), IsInstructor()]

    def perform_update(self, serializer):
        lesson = self.get_object()
        if lesson.course.instructor != self.request.user:
            raise PermissionDenied("You can only update lessons of your own course.")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.course.instructor != self.request.user:
            raise PermissionDenied("You can only delete lessons of your own course.")
        instance.delete()


# =========================
# ✅ Enrollment APIs
# =========================
class EnrollView(generics.CreateAPIView):
    """
    POST /api/enroll/
    body: { "course_id": 3 }
    """
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        course_id = request.data.get("course_id")
        if not course_id:
            return Response(
                {"course_id": ["This field is required."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ✅ only students can enroll
        if getattr(request.user, "role", None) != "student":
            return Response(
                {"detail": "Only students can enroll."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # ✅ course exists check
        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return Response(
                {"detail": "Course not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # ✅ prevent duplicate enrollment
        try:
            enrollment = Enrollment.objects.create(student=request.user, course=course)
        except IntegrityError:
            return Response(
                {"detail": "Already enrolled."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        data = EnrollmentSerializer(enrollment).data

        # ✅ extra info for frontend (optional but helpful)
        data["course_title"] = course.title
        data["course_description"] = course.description
        data["instructor_username"] = getattr(course.instructor, "username", "")

        return Response(data, status=status.HTTP_201_CREATED)


class MyEnrollmentsView(generics.ListAPIView):
    """
    GET /api/my-enrollments/
    returns list with course info so frontend can show title instead of id
    """
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            Enrollment.objects
            .filter(student=self.request.user)
            .select_related("course", "course__instructor")
            .order_by("-enrolled_at")
        )

    def list(self, request, *args, **kwargs):
        qs = self.get_queryset()
        serializer = self.get_serializer(qs, many=True)
        results = serializer.data

        # ✅ add course info in each row
        for i, en in enumerate(qs):
            results[i]["course_title"] = en.course.title
            results[i]["course_description"] = en.course.description
            results[i]["instructor_username"] = getattr(en.course.instructor, "username", "")

        return Response(results, status=status.HTTP_200_OK)
# =========================
# ✅ Progress APIs
# =========================
class MarkLessonCompleteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # ✅ only students
        if getattr(request.user, "role", None) != "student":
            return Response({"detail": "Only students can mark progress."}, status=status.HTTP_403_FORBIDDEN)

        lesson_id = request.data.get("lesson")
        if not lesson_id:
            return Response({"lesson": ["This field is required."]}, status=status.HTTP_400_BAD_REQUEST)

        lesson = get_object_or_404(Lesson, id=lesson_id)

        # ✅ Must be enrolled
        is_enrolled = Enrollment.objects.filter(student=request.user, course=lesson.course).exists()
        if not is_enrolled:
            return Response({"detail": "You must enroll in this course first."}, status=status.HTTP_403_FORBIDDEN)

        progress, _ = LessonProgress.objects.get_or_create(
            student=request.user,
            lesson=lesson,
            defaults={"completed": True},
        )

        if not progress.completed:
            progress.completed = True
            progress.save()

        return Response(
            {"detail": "Marked as completed.", "lesson": lesson.id, "completed": True},
            status=status.HTTP_200_OK
        )


class CourseProgressView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, course_id):
        # ✅ only students
        if getattr(request.user, "role", None) != "student":
            return Response({"detail": "Only students can view progress."}, status=status.HTTP_403_FORBIDDEN)

        course = get_object_or_404(Course, id=course_id)

        # ✅ Must be enrolled
        is_enrolled = Enrollment.objects.filter(student=request.user, course=course).exists()
        if not is_enrolled:
            return Response({"detail": "You must enroll in this course first."}, status=status.HTTP_403_FORBIDDEN)

        total_lessons = Lesson.objects.filter(course=course).count()
        completed_lessons = LessonProgress.objects.filter(
            student=request.user,
            lesson__course=course,
            completed=True
        ).count()

        progress_percent = 0
        if total_lessons > 0:
            progress_percent = round((completed_lessons / total_lessons) * 100, 2)

        return Response({
            "course": course.id,
            "total_lessons": total_lessons,
            "completed_lessons": completed_lessons,
            "progress_percent": progress_percent
        }, status=status.HTTP_200_OK)