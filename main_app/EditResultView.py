# Import necessary modules and functions
from django.shortcuts import get_object_or_404, render, redirect  # To get objects, render templates, and redirect after form submission
from django.views import View  # This is a Django class-based view
from django.contrib import messages  # For displaying success or warning messages to the user
from .models import Subject, Staff, Student, StudentResult  # Importing necessary models from the app
from .forms import EditResultForm  # Importing the form used to edit results
from django.urls import reverse  # For redirecting to a URL by its name

# This class handles displaying the form (GET request) and submitting the form (POST request) for editing student results
class EditResultView(View):
    # This method handles GET requests - when the user opens the "Edit Result" page
    def get(self, request, *args, **kwargs):
        # Create an empty form instance
        resultForm = EditResultForm()
        
        # Get the staff object based on the current logged-in user (request.user)
        staff = get_object_or_404(Staff, admin=request.user)
        
        # Filter the subjects that this particular staff teaches, so the staff can only edit results for subjects they are assigned to
        resultForm.fields['subject'].queryset = Subject.objects.filter(staff=staff)
        
        # Create a context dictionary to pass data to the template
        context = {
            'form': resultForm,  # Passing the form to the template
            'page_title': "Edit Student's Result"  # Title of the page
        }
        
        # Render the HTML template and pass in the context (the form and page title)
        return render(request, "staff_template/edit_student_result.html", context)

    # This method handles POST requests - when the user submits the "Edit Result" form
    def post(self, request, *args, **kwargs):
        # Create a form instance and populate it with the data submitted via POST
        form = EditResultForm(request.POST)
        
        # Create a context dictionary for re-rendering the page in case something goes wrong
        context = {'form': form, 'page_title': "Edit Student's Result"}
        
        # Check if the form is valid (e.g., all required fields are filled, correct data types)
        if form.is_valid():
            try:
                # If the form is valid, get the cleaned data (data that passed validation)
                student = form.cleaned_data.get('student')  # The student whose result we want to edit
                subject = form.cleaned_data.get('subject')  # The subject of the result
                test = form.cleaned_data.get('test')  # The test score entered by the user
                exam = form.cleaned_data.get('exam')  # The exam score entered by the user
                
                # Try to get the existing result for the given student and subject
                result = StudentResult.objects.get(student=student, subject=subject)
                
                # Update the test and exam scores with the new data from the form
                result.exam = exam
                result.test = test
                
                # Save the updated result in the database
                result.save()
                
                # Display a success message to the user
                messages.success(request, "Result Updated")
                
                # Redirect the user back to the same page (so they can edit another result if they want)
                return redirect(reverse('edit_student_result'))
            
            # If there's any issue (e.g., the result doesn't exist), show a warning message
            except Exception as e:
                messages.warning(request, "Result Could Not Be Updated")
        
        # If the form is not valid (e.g., missing data or wrong format), show a warning message
        else:
            messages.warning(request, "Result Could Not Be Updated")
        
        # If the form is invalid or there's an error, render the page again with the form data
        return render(request, "staff_template/edit_student_result.html", context)
