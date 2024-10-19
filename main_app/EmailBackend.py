# Import the ModelBackend, which is a built-in class Django uses to handle authentication
from django.contrib.auth.backends import ModelBackend

# Import the function that retrieves the currently active User model (which can be customized)
from django.contrib.auth import get_user_model


# This class defines a custom authentication backend that allows users to log in using their email
class EmailBackend(ModelBackend):
    # The 'authenticate' method is called when a user tries to log in
    # It takes in a username (which will be the email in this case), password, and any additional arguments (kwargs)
    def authenticate(self, username=None, password=None, **kwargs):
        # Get the User model (could be Django's default or a custom User model)
        UserModel = get_user_model()
        
        try:
            # Try to find a user in the database with the given email (since 'username' is passed as the email here)
            user = UserModel.objects.get(email=username)
        
        # If no user with that email exists, return None (authentication fails)
        except UserModel.DoesNotExist:
            return None
        
        # If a user is found, check if the provided password is correct
        else:
            # 'check_password' verifies if the password entered matches the one stored in the database
            if user.check_password(password):
                # If the password is correct, return the user object (this means authentication succeeded)
                return user
        
        # If the password is incorrect or another error occurs, return None (authentication fails)
        return None

