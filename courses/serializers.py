from rest_framework import serializers
from .models import Course, Lesson, Enrollment, LessonProgress


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ["id", "title", "video_url", "duration", "order"]


class CourseSerializer(serializers.ModelSerializer):
    instructor = serializers.StringRelatedField(read_only=True)
    lessons = LessonSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = ["id", "title", "description", "thumbnail", "instructor", "created_at", "lessons"]
        read_only_fields = ["instructor", "created_at"]


class EnrollmentSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)
    course_id = serializers.PrimaryKeyRelatedField(
        source="course",
        queryset=Course.objects.all(),
        write_only=True
    )

    class Meta:
        model = Enrollment
        fields = ["id", "course", "course_id", "enrolled_at"]

class LessonProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonProgress
        fields = ["id", "student", "lesson", "completed"]
        read_only_fields = ["student"]