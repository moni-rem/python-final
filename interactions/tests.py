from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from courses.models import Course, Enrollment, Lesson, Module
from .models import Certificate, UserProgress


class ProgressDashboardTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.student = User.objects.create_user(username='student', password='pass12345')
        self.instructor = User.objects.create_user(
            username='instructor',
            password='pass12345',
            role='instructor',
        )
        self.course = Course.objects.create(
            title='Django Basics',
            description='Learn Django fundamentals.',
            instructor=self.instructor,
        )
        self.module = Module.objects.create(course=self.course, title='Getting Started', order=1)
        self.lesson_one = Lesson.objects.create(module=self.module, title='Install Django', order=1)
        self.lesson_two = Lesson.objects.create(module=self.module, title='Create a Project', order=2)
        Enrollment.objects.create(student=self.student, course=self.course)

    def test_progress_dashboard_shows_enrolled_course_progress(self):
        progress = UserProgress.objects.create(student=self.student, course=self.course)
        progress.completed_lessons.add(self.lesson_one)
        self.client.login(username='student', password='pass12345')

        response = self.client.get(reverse('progress_dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Django Basics')
        self.assertContains(response, '1/2 complete')
        self.assertEqual(response.context['summary']['enrolled_courses'], 1)
        self.assertEqual(response.context['summary']['completed_lessons'], 1)

    def test_progress_dashboard_creates_missing_progress_for_enrollment(self):
        self.client.login(username='student', password='pass12345')

        response = self.client.get(reverse('progress_dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(UserProgress.objects.filter(student=self.student, course=self.course).exists())

    def test_mark_lesson_complete_tracks_completed_lesson(self):
        self.client.login(username='student', password='pass12345')

        response = self.client.post(reverse('mark_lesson_complete', args=[self.lesson_one.pk]))

        self.assertRedirects(response, reverse('module_detail', args=[self.module.pk]))
        progress = UserProgress.objects.get(student=self.student, course=self.course)
        self.assertTrue(progress.completed_lessons.filter(pk=self.lesson_one.pk).exists())
        self.assertFalse(progress.is_completed)

    def test_marking_final_course_item_creates_certificate(self):
        progress = UserProgress.objects.create(student=self.student, course=self.course)
        progress.completed_lessons.add(self.lesson_one)
        self.client.login(username='student', password='pass12345')

        response = self.client.post(reverse('mark_lesson_complete', args=[self.lesson_two.pk]))

        self.assertRedirects(response, reverse('module_detail', args=[self.module.pk]))
        progress.refresh_from_db()
        self.assertTrue(progress.is_completed)
        self.assertTrue(Certificate.objects.filter(student=self.student, course=self.course).exists())

    def test_student_can_download_own_certificate(self):
        certificate = Certificate.objects.create(student=self.student, course=self.course)
        self.client.login(username='student', password='pass12345')

        response = self.client.get(reverse('download_certificate', args=[certificate.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'image/svg+xml')
        self.assertIn('attachment;', response['Content-Disposition'])
        self.assertContains(response, 'CERTIFICATE')
        self.assertContains(response, 'Django Basics')

    def test_student_cannot_download_another_students_certificate(self):
        User = get_user_model()
        other_student = User.objects.create_user(username='other-student', password='pass12345')
        certificate = Certificate.objects.create(student=other_student, course=self.course)
        self.client.login(username='student', password='pass12345')

        response = self.client.get(reverse('download_certificate', args=[certificate.pk]))

        self.assertEqual(response.status_code, 404)
