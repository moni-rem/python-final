from django.contrib.auth.decorators import user_passes_test


def is_admin_user(user):
    return user.is_active and (user.role == 'admin' or user.is_staff or user.is_superuser)


def is_instructor_user(user):
    return user.is_active and (user.role == 'instructor' or user.role == 'admin' or user.is_staff or user.is_superuser)


def instructor_required(view_func):
    return user_passes_test(is_instructor_user, login_url='login')(view_func)
