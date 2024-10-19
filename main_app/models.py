from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import UserManager
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.db import models
from django.contrib.auth.models import AbstractUser


# Custom manager for the CustomUser model
class CustomUserManager(UserManager):
    def _create_user(self, email, password, **extra_fields):
        # Normalize the email and create a user with a hashed password
        email = self.normalize_email(email)
        user = CustomUser(email=email, **extra_fields)
        user.password = make_password(password)  # Hash the password
        user.save(using=self._db)  # Save the user instance to the database
        return user

    def create_user(self, email, password=None, **extra_fields):
        # Set default values for is_staff and is_superuser fields
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        # Set fields for creating a superuser
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        assert extra_fields["is_staff"]
        assert extra_fields["is_superuser"]
        return self._create_user(email, password, **extra_fields)


# Model to represent academic sessions (e.g., 2023-2024)
class Session(models.Model):
    start_year = models.DateField()
    end_year = models.DateField()

    def __str__(self):
        return "From " + str(self.start_year) + " to " + str(self.end_year)


# Custom user model extending Django's AbstractUser
class CustomUser(AbstractUser):
    USER_TYPE = ((1, "HOD"), (2, "Staff"), (3, "Student"))  # Choices for user types
    GENDER = [("M", "Male"), ("F", "Female")]  # Choices for gender
    
    username = None  # Removed username field, using email instead
    email = models.EmailField(unique=True)  # Unique email field for authentication
    user_type = models.CharField(default=1, choices=USER_TYPE, max_length=1)  # User role
    gender = models.CharField(max_length=1, choices=GENDER)  # Gender field
    profile_pic = models.ImageField()  # Profile picture field
    address = models.TextField()  # Address field
    fcm_token = models.TextField(default="")  # For Firebase notifications
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp for creation
    updated_at = models.DateTimeField(auto_now=True)  # Timestamp for last update
    USERNAME_FIELD = "email"  # Use email as the unique identifier for login
    REQUIRED_FIELDS = []  # No additional fields required for creating a user
    objects = CustomUserManager()  # Use custom user manager

    def __str__(self):
        return self.last_name + ", " + self.first_name  # String representation of the user


# Model to represent the admin profile linked to CustomUser
class Admin(models.Model):
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)  # One-to-one relation with CustomUser


# Model to represent courses offered
class Course(models.Model):
    name = models.CharField(max_length=120)  # Course name
    created_at = models.DateTimeField(auto_now_add=True)  # Creation timestamp
    updated_at = models.DateTimeField(auto_now=True)  # Last update timestamp

    def __str__(self):
        return self.name  # String representation of the course


# Model to represent students
class Student(models.Model):
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)  # Link to CustomUser
    course = models.ForeignKey(Course, on_delete=models.DO_NOTHING, null=True, blank=False)  # Link to Course
    session = models.ForeignKey(Session, on_delete=models.DO_NOTHING, null=True)  # Link to Session

    def __str__(self):
        return self.admin.last_name + ", " + self.admin.first_name  # String representation of the student


# Model to represent staff members
class Staff(models.Model):
    course = models.ForeignKey(Course, on_delete=models.DO_NOTHING, null=True, blank=False)  # Link to Course
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)  # Link to CustomUser

    def __str__(self):
        return self.admin.last_name + " " + self.admin.first_name  # String representation of the staff


# Model to represent subjects taught by staff
class Subject(models.Model):
    name = models.CharField(max_length=120)  # Subject name
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)  # Link to Staff
    course = models.ForeignKey(Course, on_delete=models.CASCADE)  # Link to Course
    updated_at = models.DateTimeField(auto_now=True)  # Last update timestamp
    created_at = models.DateTimeField(auto_now_add=True)  # Creation timestamp

    def __str__(self):
        return self.name  # String representation of the subject


# Model to track attendance
class Attendance(models.Model):
    session = models.ForeignKey(Session, on_delete=models.DO_NOTHING)  # Link to Session
    subject = models.ForeignKey(Subject, on_delete=models.DO_NOTHING)  # Link to Subject
    date = models.DateField()  # Date of attendance
    created_at = models.DateTimeField(auto_now_add=True)  # Creation timestamp
    updated_at = models.DateTimeField(auto_now=True)  # Last update timestamp


# Model to represent attendance reports for students
class AttendanceReport(models.Model):
    student = models.ForeignKey(Student, on_delete=models.DO_NOTHING)  # Link to Student
    attendance = models.ForeignKey(Attendance, on_delete=models.CASCADE)  # Link to Attendance
    status = models.BooleanField(default=False)  # Attendance status (Present/Absent)
    created_at = models.DateTimeField(auto_now_add=True)  # Creation timestamp
    updated_at = models.DateTimeField(auto_now=True)  # Last update timestamp


# Model to represent leave reports submitted by students
class LeaveReportStudent(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)  # Link to Student
    date = models.CharField(max_length=60)  # Date of leave
    message = models.TextField()  # Reason/message for leave
    status = models.SmallIntegerField(default=0)  # Status of leave request (0: Pending, 1: Approved, 2: Rejected)
    created_at = models.DateTimeField(auto_now_add=True)  # Creation timestamp
    updated_at = models.DateTimeField(auto_now=True)  # Last update timestamp


# Model to represent leave reports submitted by staff
class LeaveReportStaff(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)  # Link to Staff
    date = models.CharField(max_length=60)  # Date of leave
    message = models.TextField()  # Reason/message for leave
    status = models.SmallIntegerField(default=0)  # Status of leave request (0: Pending, 1: Approved, 2: Rejected)
    created_at = models.DateTimeField(auto_now_add=True)  # Creation timestamp
    updated_at = models.DateTimeField(auto_now=True)  # Last update timestamp


# Model to represent feedback submitted by students
class FeedbackStudent(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)  # Link to Student
    feedback = models.TextField()  # Feedback message
    reply = models.TextField()  # Reply to the feedback
    created_at = models.DateTimeField(auto_now_add=True)  # Creation timestamp
    updated_at = models.DateTimeField(auto_now=True)  # Last update timestamp


# Model to represent feedback submitted by staff
class FeedbackStaff(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)  # Link to Staff
    feedback = models.TextField()  # Feedback message
    reply = models.TextField()  # Reply to the feedback
    created_at = models.DateTimeField(auto_now_add=True)  # Creation timestamp
    updated_at = models.DateTimeField(auto_now=True)  # Last update timestamp


# Model to represent notifications sent to staff
class NotificationStaff(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)  # Link to Staff
    message = models.TextField()  # Notification message
    created_at = models.DateTimeField(auto_now_add=True)  # Creation timestamp
    updated_at = models.DateTimeField(auto_now=True)  # Last update timestamp


# Model to represent notifications sent to students
class NotificationStudent(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)  # Link to Student
    message = models.TextField()  # Notification message
    created_at = models.DateTimeField(auto_now_add=True)  # Creation timestamp
    updated_at = models.DateTimeField(auto_now=True)  # Last update timestamp


# Model to store results for students in subjects
class StudentResult(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)  # Link to Student
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)  # Link to Subject
    test = models.FloatField(default=0)  # Test score
    exam = models.FloatField(default=0)  # Exam score
    created_at = models.DateTimeField(auto_now_add=True)  # Creation timestamp
    updated_at = models.DateTimeField(auto_now=True)  # Last update timestamp


# Signal receiver for creating user profiles
@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # Create profile based on user type
        if instance.user_type == 1:
            Admin.objects.create(admin=instance)  # Create Admin profile
        if instance.user_type == 2:
            Staff.objects.create(admin=instance)  # Create Staff profile
        if instance.user_type == 3:
            Student.objects.create(admin=instance)  # Create Student profile


# Signal receiver for saving user profiles
@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    # Save the associated profile when CustomUser is saved
    if instance.user_type == 1:
        instance.admin.save()  # Save Admin profile
    if instance.user_type == 2:
        instance.staff.save()  # Save Staff profile
    if instance.user_type == 3:
        instance.student.save()  # Save Student profile
