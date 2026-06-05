from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from courses.models import Course, Enrollment, Module
from interactions.models import Certificate
from .models import Assignment, Choice, Question, Quiz, QuizAttempt


class QuizDetailTests(TestCase):
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
            description='Learn Django.',
            instructor=self.instructor,
        )
        self.module = Module.objects.create(course=self.course, title='Intro', order=1)

    def test_quiz_list_loads_quizzes_after_module_is_selected(self):
        module_quiz = Quiz.objects.create(
            module=self.module,
            title='Intro Quiz',
            quiz_type='multiple_choice',
        )
        other_course = Course.objects.create(
            title='Other Course',
            description='A separate course.',
            instructor=self.instructor,
        )
        other_module = Module.objects.create(course=other_course, title='Other Module', order=1)
        Quiz.objects.create(
            module=other_module,
            title='Other Quiz',
            quiz_type='multiple_choice',
        )
        self.client.login(username='student', password='pass12345')

        default_response = self.client.get(reverse('quiz_list'))
        self.assertEqual(default_response.status_code, 200)
        self.assertContains(default_response, 'Select a module to view its quizzes.')
        self.assertNotContains(default_response, module_quiz.title)

        selected_response = self.client.get(reverse('quiz_list'), {'module': self.module.pk})
        self.assertEqual(selected_response.status_code, 200)
        self.assertContains(selected_response, module_quiz.title)
        self.assertNotContains(selected_response, 'Other Quiz')

    def test_essay_quiz_submission_shows_pending_review_not_zero_score(self):
        quiz = Quiz.objects.create(
            module=self.module,
            title='Essay Quiz',
            quiz_type='essay',
        )
        self.client.login(username='student', password='pass12345')

        response = self.client.post(reverse('quiz_detail', args=[quiz.pk]), {
            'text_response': 'My essay answer.',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Pending instructor review')
        self.assertNotContains(response, 'You scored <strong>0.0%</strong>', html=True)
        attempt = QuizAttempt.objects.get(student=self.student, quiz=quiz)
        self.assertIsNone(attempt.score)

    def test_multiple_choice_quiz_submission_shows_auto_score(self):
        quiz = Quiz.objects.create(
            module=self.module,
            title='Multiple Choice Quiz',
            quiz_type='multiple_choice',
        )
        question = Question.objects.create(quiz=quiz, text='What framework is this?')
        correct_choice = Choice.objects.create(question=question, text='Django', is_correct=True)
        self.client.login(username='student', password='pass12345')

        response = self.client.post(reverse('quiz_detail', args=[quiz.pk]), {
            str(question.pk): str(correct_choice.pk),
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '100.0%')
        attempt = QuizAttempt.objects.get(student=self.student, quiz=quiz)
        self.assertEqual(attempt.score, 100.0)

    def test_instructor_can_create_qcm_quiz_with_questions_and_choices(self):
        self.client.login(username='instructor', password='pass12345')

        response = self.client.post(reverse('create_quiz'), {
            'module': str(self.module.pk),
            'title': 'QCM Quiz',
            'description': 'Choose the correct answer.',
            'quiz_type': 'multiple_choice',
            'qcm_question_count': '2',
            'question_0_text': 'What framework is this?',
            'question_0_choice_0': 'Django',
            'question_0_choice_1': 'Flask',
            'question_0_correct': '0',
            'question_1_text': 'Which language is Django written in?',
            'question_1_choice_0': 'Python',
            'question_1_choice_1': 'JavaScript',
            'question_1_correct': '0',
        })

        self.assertRedirects(response, reverse('quiz_list'))
        quiz = Quiz.objects.get(title='QCM Quiz')
        self.assertEqual(quiz.questions.count(), 2)
        first_question = quiz.questions.get(text='What framework is this?')
        second_question = quiz.questions.get(text='Which language is Django written in?')
        self.assertEqual(first_question.choices.count(), 2)
        self.assertEqual(second_question.choices.count(), 2)
        self.assertTrue(first_question.choices.get(text='Django').is_correct)
        self.assertFalse(first_question.choices.get(text='Flask').is_correct)
        self.assertTrue(second_question.choices.get(text='Python').is_correct)
        self.assertFalse(second_question.choices.get(text='JavaScript').is_correct)

    def test_qcm_quiz_creation_requires_questions(self):
        self.client.login(username='instructor', password='pass12345')

        response = self.client.post(reverse('create_quiz'), {
            'module': str(self.module.pk),
            'title': 'Empty QCM Quiz',
            'description': '',
            'quiz_type': 'multiple_choice',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Add at least one QCM question')
        self.assertFalse(Quiz.objects.filter(title='Empty QCM Quiz').exists())

    def test_quiz_submission_can_create_course_certificate(self):
        Enrollment.objects.create(student=self.student, course=self.course)
        quiz = Quiz.objects.create(
            module=self.module,
            title='Final Quiz',
            quiz_type='multiple_choice',
        )
        question = Question.objects.create(quiz=quiz, text='What framework is this?')
        correct_choice = Choice.objects.create(question=question, text='Django', is_correct=True)
        self.client.login(username='student', password='pass12345')

        response = self.client.post(reverse('quiz_detail', args=[quiz.pk]), {
            str(question.pk): str(correct_choice.pk),
        })

        self.assertEqual(response.status_code, 200)
        self.assertTrue(Certificate.objects.filter(student=self.student, course=self.course).exists())

    def test_assignment_submission_can_create_course_certificate(self):
        Enrollment.objects.create(student=self.student, course=self.course)
        assignment = Assignment.objects.create(
            course=self.course,
            title='Final Assignment',
            description='Submit the final task.',
            due_date='2026-06-01 12:00:00Z',
        )
        self.client.login(username='student', password='pass12345')

        response = self.client.post(reverse('assignment_submit', args=[assignment.pk]), {
            'text_submission': 'My final answer.',
        })

        self.assertRedirects(response, reverse('assignment_list'))
        self.assertTrue(Certificate.objects.filter(student=self.student, course=self.course).exists())

    def test_instructor_can_review_and_grade_quiz_attempt(self):
        quiz = Quiz.objects.create(
            module=self.module,
            title='Essay Quiz',
            quiz_type='essay',
        )
        attempt = QuizAttempt.objects.create(
            student=self.student,
            quiz=quiz,
            text_response='My essay answer.',
        )
        self.client.login(username='instructor', password='pass12345')

        list_response = self.client.get(reverse('review_quiz_attempts'))
        self.assertEqual(list_response.status_code, 200)
        self.assertContains(list_response, 'Essay Quiz')
        self.assertContains(list_response, 'Pending')

        grade_response = self.client.post(reverse('grade_quiz_attempt', args=[attempt.pk]), {
            'score': '88.50',
            'feedback': 'Good work. Add more detail next time.',
        })

        self.assertRedirects(grade_response, reverse('review_quiz_attempts'))
        attempt.refresh_from_db()
        self.assertEqual(str(attempt.score), '88.50')
        self.assertEqual(attempt.feedback, 'Good work. Add more detail next time.')

    def test_instructor_cannot_grade_attempt_for_another_instructor_course(self):
        User = get_user_model()
        other_instructor = User.objects.create_user(
            username='other-instructor',
            password='pass12345',
            role='instructor',
        )
        other_course = Course.objects.create(
            title='Other Course',
            description='Not owned by this instructor.',
            instructor=other_instructor,
        )
        other_module = Module.objects.create(course=other_course, title='Other Module', order=1)
        quiz = Quiz.objects.create(
            module=other_module,
            title='Private Essay Quiz',
            quiz_type='essay',
        )
        attempt = QuizAttempt.objects.create(
            student=self.student,
            quiz=quiz,
            text_response='Hidden answer.',
        )
        self.client.login(username='instructor', password='pass12345')

        response = self.client.get(reverse('grade_quiz_attempt', args=[attempt.pk]))

        self.assertEqual(response.status_code, 404)
