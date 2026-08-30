from django.contrib.auth.forms import UserCreationForm
from .models import User

class CustomerSignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["username", "email", "phone","profile_picture"]
