from django.contrib.auth import login
from django.shortcuts import redirect, render
from .forms import CustomerSignUpForm
from .models import User
from django.contrib.auth.views import LoginView

def signup(request):
    if request.method == "POST":
        form = CustomerSignUpForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = User.Role.CUSTOMER
            user.save()
            login(request, user, backend="accounts.backends.EmailOrPhoneBackend")
            return redirect(user.get_home_url())
    else:
        form = CustomerSignUpForm()
    return render(request, "accounts/signup.html", {"form": form})


class RoleBasedLoginView(LoginView):
    template_name = "accounts/login.html"
    def get_success_url(self):
        redirect_to = self.get_redirect_url()
        if redirect_to:
            return redirect_to
        return self.request.user.get_home_url()


"""self.get_redirect_url() is LoginView's own built-in method that reads and validates the next parameter (rejecting unsafe redirects to external domains) — using it here means we get that safety check for free instead of reimplementing it."""