from django.shortcuts import redirect, render
from accounts.decorators import role_required
from accounts.models import User
from .forms import ExpenseForm
from .models import Expense

# Create your views here.
@role_required(User.Role.MANAGER)
def expense_list(request):
    expenses = Expense.objects.select_related("recorded_by").all()
    return render(request, "expenses/expense_list.html", {"expenses": expenses})

@role_required(User.Role.MANAGER)
def add_expense(request):
    if request.method == "POST":
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.recorded_by = request.user
            expense.save()
            return redirect("expenses:expense_list")
    else:
        form = ExpenseForm()
    return render(request, "expenses/expense_form.html", {"form": form})