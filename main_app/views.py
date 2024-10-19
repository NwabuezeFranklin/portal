import json
import requests
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.views.decorators.csrf import csrf_exempt

from .EmailBackend import EmailBackend  # Custom email backend for authentication
from .models import Attendance, Session, Subject  # Import models for attendance, session, and subject

# Create your views here.


def login_page(request):
    # Render the login page or redirect if the user is already authenticated
    if request.user.is_authenticated:
        if request.user.user_type == '1':  # Check if user is an admin
            return redirect(reverse("admin_home"))
        elif request.user.user_type == '2':  # Check if user is staff
            return redirect(reverse("staff_home"))
        else:  # Assume user is a student
            return redirect(reverse("student_home"))
    return render(request, 'main_app/login.html')  # Render login template if not authenticated


def doLogin(request, **kwargs):
    # Handle user login
    if request.method != 'POST':
        return HttpResponse("<h4>Denied</h4>")  # Deny access if not a POST request
    else:
        # Google reCAPTCHA verification
        captcha_token = request.POST.get('g-recaptcha-response')  # Get reCAPTCHA token from request
        captcha_url = "https://www.google.com/recaptcha/api/siteverify"
        captcha_key = "6LfswtgZAAAAABX9gbLqe-d97qE2g1JP8oUYritJ"  # Your reCAPTCHA secret key
        data = {
            'secret': captcha_key,
            'response': captcha_token
        }
        # Make request to verify reCAPTCHA
        try:
            captcha_server = requests.post(url=captcha_url, data=data)  # Send verification request
            response = json.loads(captcha_server.text)  # Parse response
            if response['success'] == False:  # Check if reCAPTCHA was successful
                messages.error(request, 'Invalid Captcha. Try Again')  # Show error message
                return redirect('/')  # Redirect back to login page
        except:
            messages.error(request, 'Captcha could not be verified. Try Again')  # Handle request errors
            return redirect('/')  # Redirect back to login page
        
        # Authenticate user using custom EmailBackend
        user = EmailBackend.authenticate(request, username=request.POST.get('email'), password=request.POST.get('password'))
        if user is not None:  # If user is authenticated successfully
            login(request, user)  # Log the user in
            if user.user_type == '1':
                return redirect(reverse("admin_home"))  # Redirect admin
            elif user.user_type == '2':
                return redirect(reverse("staff_home"))  # Redirect staff
            else:
                return redirect(reverse("student_home"))  # Redirect student
        else:
            messages.error(request, "Invalid details")  # Show error message for invalid login
            return redirect("/")  # Redirect back to login page


def logout_user(request):
    # Log out the user and redirect to the homepage
    if request.user is not None:
        logout(request)  # Log out the user
    return redirect("/")  # Redirect to homepage


@csrf_exempt  # Allow CSRF exemption for this view
def get_attendance(request):
    # Retrieve attendance records based on subject and session
    subject_id = request.POST.get('subject')  # Get subject ID from POST data
    session_id = request.POST.get('session')  # Get session ID from POST data
    try:
        subject = get_object_or_404(Subject, id=subject_id)  # Fetch subject or return 404
        session = get_object_or_404(Session, id=session_id)  # Fetch session or return 404
        attendance = Attendance.objects.filter(subject=subject, session=session)  # Query attendance records
        attendance_list = []
        for attd in attendance:  # Iterate through attendance records
            data = {
                "id": attd.id,
                "attendance_date": str(attd.date),  # Convert date to string
                "session": attd.session.id  # Get session ID
            }
            attendance_list.append(data)  # Append attendance data to list
        return JsonResponse(json.dumps(attendance_list), safe=False)  # Return JSON response
    except Exception as e:
        return None  # Handle exceptions gracefully


def showFirebaseJS(request):
    # Serve Firebase JavaScript for handling notifications
    data = """
    // Give the service worker access to Firebase Messaging.
    // Note that you can only use Firebase Messaging here, other Firebase libraries
    // are not available in the service worker.
    importScripts('https://www.gstatic.com/firebasejs/7.22.1/firebase-app.js');
    importScripts('https://www.gstatic.com/firebasejs/7.22.1/firebase-messaging.js');

    // Initialize the Firebase app in the service worker by passing in
    // your app's Firebase config object.
    // https://firebase.google.com/docs/web/setup#config-object
    firebase.initializeApp({
        apiKey: "AIzaSyBarDWWHTfTMSrtc5Lj3Cdw5dEvjAkFwtM",
        authDomain: "sms-with-django.firebaseapp.com",
        databaseURL: "https://sms-with-django.firebaseio.com",
        projectId: "sms-with-django",
        storageBucket: "sms-with-django.appspot.com",
        messagingSenderId: "945324593139",
        appId: "1:945324593139:web:03fa99a8854bbd38420c86",
        measurementId: "G-2F2RXTL9GT"
    });

    // Retrieve an instance of Firebase Messaging so that it can handle background
    // messages.
    const messaging = firebase.messaging();
    messaging.setBackgroundMessageHandler(function (payload) {
        const notification = JSON.parse(payload);  // Parse the incoming payload
        const notificationOption = {
            body: notification.body,  // Get the body of the notification
            icon: notification.icon  // Get the icon for the notification
        }
        return self.registration.showNotification(payload.notification.title, notificationOption);  // Show the notification
    });
    """
    return HttpResponse(data, content_type='application/javascript')  # Serve the Firebase JS as a response
