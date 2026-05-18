from assessments.models import Assignment, AssignmentSubmission, Quiz, QuizAttempt
from courses.models import Enrollment, Lesson

from .models import Certificate, UserProgress


def sync_course_completion(student, course, touch_progress=False):
    progress, _ = UserProgress.objects.get_or_create(student=student, course=course)

    lesson_total = Lesson.objects.filter(module__course=course).count()
    completed_lessons = progress.completed_lessons.filter(module__course=course).count()

    quizzes_total = Quiz.objects.filter(module__course=course).count()
    quizzes_completed = QuizAttempt.objects.filter(
        student=student,
        quiz__module__course=course,
    ).values('quiz_id').distinct().count()

    assignments_total = Assignment.objects.filter(course=course).count()
    assignments_submitted = AssignmentSubmission.objects.filter(
        student=student,
        assignment__course=course,
    ).values('assignment_id').distinct().count()

    total_items = lesson_total + quizzes_total + assignments_total
    completed_items = completed_lessons + quizzes_completed + assignments_submitted
    is_completed = total_items > 0 and completed_items == total_items

    if progress.is_completed != is_completed or touch_progress:
        progress.is_completed = is_completed
        progress.save(update_fields=['is_completed', 'last_accessed'])

    certificate = None
    certificate_created = False
    is_enrolled = Enrollment.objects.filter(student=student, course=course).exists()
    if is_completed and is_enrolled:
        certificate, certificate_created = Certificate.objects.get_or_create(student=student, course=course)

    return {
        'progress': progress,
        'certificate': certificate,
        'certificate_created': certificate_created,
        'lesson_total': lesson_total,
        'completed_lessons': completed_lessons,
        'quizzes_total': quizzes_total,
        'quizzes_completed': quizzes_completed,
        'assignments_total': assignments_total,
        'assignments_submitted': assignments_submitted,
        'total_items': total_items,
        'completed_items': completed_items,
        'is_completed': is_completed,
    }
