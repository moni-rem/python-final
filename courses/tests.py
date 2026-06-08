from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Category, Course, Lesson, Module


class CreateCourseTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.instructor = User.objects.create_user(
            username='instructor',
            password='pass12345',
            role='instructor',
        )
        self.category = Category.objects.create(name='Programming')

    def _course_payload(self, **overrides):
        payload = {
            'title': 'Python Fundamentals',
            'description': 'Learn Python from the ground up.',
            'category': str(self.category.pk),
            'modules-TOTAL_FORMS': '5',
            'modules-INITIAL_FORMS': '0',
            'modules-MIN_NUM_FORMS': '0',
            'modules-MAX_NUM_FORMS': '20',
            'modules-0-title': '',
            'modules-0-order': '0',
            'modules-1-title': '',
            'modules-1-order': '1',
            'modules-2-title': '',
            'modules-2-order': '2',
            'modules-3-title': '',
            'modules-3-order': '3',
            'modules-4-title': '',
            'modules-4-order': '4',
            'lesson-title': '',
            'lesson-content': '',
            'lesson-video_url': '',
            'lesson-order': '0',
        }
        payload.update(overrides)
        return payload

    def test_instructor_can_create_course_with_many_modules(self):
        self.client.login(username='instructor', password='pass12345')

        response = self.client.post(reverse('create_course'), self._course_payload(
            **{
                'modules-0-title': 'Getting Started',
                'modules-1-title': 'Core Syntax',
                'modules-2-title': 'Final Project',
            }
        ))

        course = Course.objects.get(title='Python Fundamentals')
        self.assertRedirects(response, reverse('course_detail', args=[course.pk]))
        self.assertEqual(
            list(course.modules.order_by('order').values_list('title', flat=True)),
            ['Getting Started', 'Core Syntax', 'Final Project'],
        )

    def test_first_lesson_is_added_to_first_entered_module(self):
        self.client.login(username='instructor', password='pass12345')

        response = self.client.post(reverse('create_course'), self._course_payload(
            **{
                'modules-0-title': 'Getting Started',
                'modules-1-title': 'Core Syntax',
                'lesson-title': 'Welcome',
                'lesson-content': 'Start here.',
            }
        ))

        course = Course.objects.get(title='Python Fundamentals')
        first_module = course.modules.order_by('order').first()
        self.assertRedirects(response, reverse('course_detail', args=[course.pk]))
        self.assertTrue(Lesson.objects.filter(
            module=first_module,
            title='Welcome',
            content='Start here.',
        ).exists())

    def test_lesson_content_requires_at_least_one_module(self):
        self.client.login(username='instructor', password='pass12345')

        response = self.client.post(reverse('create_course'), self._course_payload(
            **{
                'lesson-title': 'Welcome',
                'lesson-content': 'Start here.',
            }
        ))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Add a module title before uploading a lesson.')
        self.assertFalse(Module.objects.exists())
