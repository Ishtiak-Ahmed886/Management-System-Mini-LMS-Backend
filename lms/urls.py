from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from users.views import LogoutView

from courses.views import (
    CourseListCreateView,
    CourseDetailView,
    LessonListByCourseView,
    LessonDetailView,
    EnrollView,
    MyEnrollmentsView,
    MarkLessonCompleteView,
    CourseProgressView,
)

urlpatterns = [
    path("admin/", admin.site.urls),

    # Users (Register)
    path("api/", include("users.urls")),

    # JWT Auth
    path("api/login/", TokenObtainPairView.as_view(), name="login"),
    path("api/logout/", LogoutView.as_view(), name="logout"),
    path("api/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # Courses
    path("api/courses/", CourseListCreateView.as_view(), name="course_list_create"),
    path("api/courses/<int:pk>/", CourseDetailView.as_view(), name="course_detail"),

    # Lessons
    path("api/courses/<int:course_id>/lessons/", LessonListByCourseView.as_view(), name="lessons_by_course"),
    path("api/lessons/<int:pk>/", LessonDetailView.as_view(), name="lesson_detail"),

    # Enrollment
    path("api/enroll/", EnrollView.as_view(), name="enroll"),
    path("api/my-enrollments/", MyEnrollmentsView.as_view(), name="my_enrollments"),

    # Progress ✅ STEP 6.1 & 6.2
    path("api/progress/complete/", MarkLessonCompleteView.as_view(), name="mark_lesson_complete"),
    path("api/courses/<int:course_id>/progress/", CourseProgressView.as_view(), name="course_progress"),
]

# Media files (for thumbnail)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)