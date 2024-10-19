# Importing required Django form and widget classes
from django import forms
from django.forms.widgets import DateInput, TextInput

# Importing models used in the forms
from .models import *


# Base form class that inherits from Django's ModelForm.
# It allows customization of forms for different models.
class FormSettings(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        # Call the superclass constructor
        super(FormSettings, self).__init__(*args, **kwargs)
        # Iterate through all visible fields of the form and add a CSS class 'form-control'
        # This is typically used to apply Bootstrap styling to form fields.
        for field in self.visible_fields():
            field.field.widget.attrs['class'] = 'form-control'


# Form for managing CustomUser model, inherits from FormSettings
class CustomUserForm(FormSettings):
    # Define form fields for the custom user, including fields that are not directly tied to the model
    email = forms.EmailField(required=True)
    gender = forms.ChoiceField(choices=[('M', 'Male'), ('F', 'Female')])
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    address = forms.CharField(widget=forms.Textarea)
    password = forms.CharField(widget=forms.PasswordInput)
    profile_pic = forms.ImageField()

    # Customize widget for password field
    widget = {
        'password': forms.PasswordInput(),
    }

    def __init__(self, *args, **kwargs):
        # Call the superclass constructor
        super(CustomUserForm, self).__init__(*args, **kwargs)

        # If this is an instance being edited (not a new user)
        if kwargs.get('instance'):
            instance = kwargs.get('instance').admin.__dict__  # Accessing the 'admin' field for this instance
            self.fields['password'].required = False  # Make password not required if it's an update
            
            # Initialize form fields with values from the instance
            for field in CustomUserForm.Meta.fields:
                self.fields[field].initial = instance.get(field)
            
            # If updating, set a placeholder on the password field
            if self.instance.pk is not None:
                self.fields['password'].widget.attrs['placeholder'] = "Fill this only if you wish to update password"

    # Custom email validation to ensure email uniqueness
    def clean_email(self, *args, **kwargs):
        formEmail = self.cleaned_data['email'].lower()
        
        # If it's a new user (Insert)
        if self.instance.pk is None:
            if CustomUser.objects.filter(email=formEmail).exists():
                raise forms.ValidationError("The given email is already registered")
        # If it's an update (Update)
        else:
            dbEmail = self.Meta.model.objects.get(id=self.instance.pk).admin.email.lower()
            # If the email has been changed, check for uniqueness
            if dbEmail != formEmail:
                if CustomUser.objects.filter(email=formEmail).exists():
                    raise forms.ValidationError("The given email is already registered")
        
        return formEmail

    class Meta:
        # Link the form to the CustomUser model
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'gender', 'password', 'profile_pic', 'address']


# Form for creating or updating students, extends CustomUserForm
class StudentForm(CustomUserForm):
    def __init__(self, *args, **kwargs):
        super(StudentForm, self).__init__(*args, **kwargs)

    class Meta(CustomUserForm.Meta):
        model = Student
        fields = CustomUserForm.Meta.fields + ['course', 'session']


# Form for Admin users, inherits from CustomUserForm
class AdminForm(CustomUserForm):
    def __init__(self, *args, **kwargs):
        super(AdminForm, self).__init__(*args, **kwargs)

    class Meta(CustomUserForm.Meta):
        model = Admin
        fields = CustomUserForm.Meta.fields


# Form for Staff users, inherits from CustomUserForm
class StaffForm(CustomUserForm):
    def __init__(self, *args, **kwargs):
        super(StaffForm, self).__init__(*args, **kwargs)

    class Meta(CustomUserForm.Meta):
        model = Staff
        fields = CustomUserForm.Meta.fields + ['course']


# Form for creating or updating Course model
class CourseForm(FormSettings):
    def __init__(self, *args, **kwargs):
        super(CourseForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Course
        fields = ['name']


# Form for Subject model, includes staff and course associations
class SubjectForm(FormSettings):
    def __init__(self, *args, **kwargs):
        super(SubjectForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Subject
        fields = ['name', 'staff', 'course']


# Form for the Session model, with date input widgets
class SessionForm(FormSettings):
    def __init__(self, *args, **kwargs):
        super(SessionForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Session
        fields = '__all__'  # Include all fields in the Session model
        widgets = {
            'start_year': DateInput(attrs={'type': 'date'}),
            'end_year': DateInput(attrs={'type': 'date'}),
        }


# Form for leave requests from staff members
class LeaveReportStaffForm(FormSettings):
    def __init__(self, *args, **kwargs):
        super(LeaveReportStaffForm, self).__init__(*args, **kwargs)

    class Meta:
        model = LeaveReportStaff
        fields = ['date', 'message']
        widgets = {
            'date': DateInput(attrs={'type': 'date'}),
        }


# Form for staff feedback submissions
class FeedbackStaffForm(FormSettings):
    def __init__(self, *args, **kwargs):
        super(FeedbackStaffForm, self).__init__(*args, **kwargs)

    class Meta:
        model = FeedbackStaff
        fields = ['feedback']


# Form for leave requests from students
class LeaveReportStudentForm(FormSettings):
    def __init__(self, *args, **kwargs):
        super(LeaveReportStudentForm, self).__init__(*args, **kwargs)

    class Meta:
        model = LeaveReportStudent
        fields = ['date', 'message']
        widgets = {
            'date': DateInput(attrs={'type': 'date'}),
        }


# Form for student feedback submissions
class FeedbackStudentForm(FormSettings):
    def __init__(self, *args, **kwargs):
        super(FeedbackStudentForm, self).__init__(*args, **kwargs)

    class Meta:
        model = FeedbackStudent
        fields = ['feedback']


# Form for editing student details, inherits from CustomUserForm
class StudentEditForm(CustomUserForm):
    def __init__(self, *args, **kwargs):
        super(StudentEditForm, self).__init__(*args, **kwargs)

    class Meta(CustomUserForm.Meta):
        model = Student
        fields = CustomUserForm.Meta.fields


# Form for editing staff details, inherits from CustomUserForm
class StaffEditForm(CustomUserForm):
    def __init__(self, *args, **kwargs):
        super(StaffEditForm, self).__init__(*args, **kwargs)

    class Meta(CustomUserForm.Meta):
        model = Staff
        fields = CustomUserForm.Meta.fields


# Form for editing student results
class EditResultForm(FormSettings):
    # Define session year field with a queryset of all session objects
    session_list = Session.objects.all()
    session_year = forms.ModelChoiceField(label="Session Year", queryset=session_list, required=True)

    def __init__(self, *args, **kwargs):
        super(EditResultForm, self).__init__(*args, **kwargs)

    class Meta:
        model = StudentResult
        fields = ['session_year', 'subject', 'student', 'test', 'exam']
