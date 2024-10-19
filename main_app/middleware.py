from django.utils.deprecation import MiddlewareMixin
from django.urls import reverse
from django.shortcuts import redirect


class LoginCheckMiddleWare(MiddlewareMixin):
    def process_view(self, request, view_func, view_args, view_kwargs):
        modulename = view_func.__module__
        user = request.user  # Retrieve the current user

        # Check if the user is authenticated
        if user.is_authenticated:
            # If the user is HOD/Admin
            if user.user_type == '1': 
                if modulename == 'main_app.student_views':
                    return redirect(reverse('admin_home'))

            # If the user is Staff
            elif user.user_type == '2':
                if modulename == 'main_app.student_views' or modulename == 'main_app.hod_views':
                    return redirect(reverse('staff_home'))

            # If the user is Student
            elif user.user_type == '3':
                if modulename == 'main_app.hod_views' or modulename == 'main_app.staff_views':
                    return redirect(reverse('student_home'))

            # If none of the aforementioned, redirect to login page
            else:
                return redirect(reverse('login_page'))

        # If the user is not authenticated
        else:
            # Allow access to login page and authentication views
            if request.path == reverse('login_page') or modulename == 'django.contrib.auth.views' or request.path == reverse('user_login'):
                pass
            # Otherwise, redirect to the login page
            else:
                return redirect(reverse('login_page'))

