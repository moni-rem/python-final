from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from courses.models import Category, Course, Module, Lesson


class Command(BaseCommand):
    help = 'Create starter categories and courses for a fresh deployed database.'

    def handle(self, *args, **options):
        User = get_user_model()
        instructor, created = User.objects.get_or_create(
            username='demo_instructor',
            defaults={
                'email': 'instructor@example.com',
                'first_name': 'Demo',
                'last_name': 'Instructor',
                'role': 'instructor',
                'is_staff': True,
            },
        )
        if created:
            instructor.set_password('ChangeMe123!')
            instructor.save(update_fields=['password'])
        elif instructor.role != 'instructor':
            instructor.role = 'instructor'
            instructor.save(update_fields=['role'])

        course_data = [
            {
                'category': 'Web Development',
                'category_description': 'Build practical websites and web applications.',
                'title': 'Django Foundations',
                'description': 'Learn Django models, views, templates, authentication, and deployment basics through a practical course project.',
                'price': Decimal('0.00'),
                'modules': [
                    ('Getting Started', ['Project setup', 'Django apps and routing']),
                    ('Building Features', ['Models and migrations', 'Templates and forms']),
                ],
            },
            {
                'category': 'Programming',
                'category_description': 'Sharpen programming skills with hands-on lessons.',
                'title': 'Python for Problem Solving',
                'description': 'Practice core Python syntax, functions, data structures, and small problem-solving workflows for beginners.',
                'price': Decimal('0.00'),
                'modules': [
                    ('Python Basics', ['Variables and types', 'Control flow']),
                    ('Useful Patterns', ['Functions', 'Lists and dictionaries']),
                ],
            },
            {
                'category': 'Data Skills',
                'category_description': 'Explore data analysis, reporting, and dashboards.',
                'title': 'Data Analysis Essentials',
                'description': 'Get comfortable cleaning data, asking useful questions, and presenting insights clearly.',
                'price': Decimal('19.00'),
                'modules': [
                    ('Data Thinking', ['Understanding datasets', 'Asking better questions']),
                    ('Analysis Practice', ['Cleaning records', 'Summarizing results']),
                ],
            },
        ]

        courses_created = 0
        for item in course_data:
            category, _ = Category.objects.get_or_create(
                name=item['category'],
                defaults={'description': item['category_description']},
            )
            course, created = Course.objects.get_or_create(
                title=item['title'],
                defaults={
                    'description': item['description'],
                    'category': category,
                    'instructor': instructor,
                    'price': item['price'],
                },
            )
            if created:
                courses_created += 1

            for module_order, (module_title, lessons) in enumerate(item['modules'], start=1):
                module, _ = Module.objects.get_or_create(
                    course=course,
                    title=module_title,
                    defaults={'order': module_order},
                )
                for lesson_order, lesson_title in enumerate(lessons, start=1):
                    Lesson.objects.get_or_create(
                        module=module,
                        title=lesson_title,
                        defaults={
                            'order': lesson_order,
                            'content': f'Introductory material for {lesson_title}.',
                        },
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f'Seed data ready. Created {courses_created} new course(s). '
                'Demo instructor username: demo_instructor'
            )
        )
