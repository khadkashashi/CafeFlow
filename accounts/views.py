from django.contrib.auth import login
from django.shortcuts import redirect, render
from .forms import CustomerSignUpForm
from .models import User


def signup(request):
    if request.method == "POST":
        form = CustomerSignUpForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = User.Role.CUSTOMER
            user.save()
            login(request, user, backend="accounts.backends.EmailOrPhoneBackend")
            return redirect("landing:home")
    else:
        form = CustomerSignUpForm()

    return render(request, "accounts/signup.html", {"form": form})