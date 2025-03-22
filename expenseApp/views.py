from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import Expense
from .forms import ExpenseForm
from django.shortcuts import render
from .models import Expense
from django.db.models import Sum
from django.utils.dateparse import parse_date
from sellApp.models import Sale
# Create View
def create_expense(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('expense_list')  # Redirect to the expense list page after successful creation
    else:
        form = ExpenseForm()
    return render(request, 'expenseApp/create_expense.html', {'form': form})

# Edit View
def edit_expense(request, pk):
    expense = get_object_or_404(Expense, pk=pk)
    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            return redirect('expense_list')  # Redirect to the expense list after update
    else:
        form = ExpenseForm(instance=expense)
    return render(request, 'expenseApp/edit_expense.html', {'form': form})

# Delete View
def delete_expense(request, pk):
    expense = get_object_or_404(Expense, pk=pk)
    if request.method == 'POST':
        expense.delete()
        return redirect('expense_list')  # Redirect to the expense list after deletion
    return render(request, 'expenseApp/delete_expense.html', {'expense': expense})


def expense_list_and_profit_summary(request):
    # Get filter parameters
    query = request.GET.get('q', '')
    min_amount = request.GET.get('min_amount', '')
    max_amount = request.GET.get('max_amount', '')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')

    # Filter Expenses
    expenses = Expense.objects.all()
    if query:
        expenses = expenses.filter(name__icontains=query)
    if min_amount:
        expenses = expenses.filter(amount__gte=min_amount)
    if max_amount:
        expenses = expenses.filter(amount__lte=max_amount)
    if start_date and end_date:
        expenses = expenses.filter(created_at__range=[parse_date(start_date), parse_date(end_date)])

    # Filter Sales for Profit Calculation
    sales = Sale.objects.all()
    if start_date and end_date:
        sales = sales.filter(created_at__range=[parse_date(start_date), parse_date(end_date)])

    # Calculate Profit Summary
    total_profit = sales.aggregate(Sum('total_profit'))['total_profit__sum'] or 0
    total_expenses = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    net_profit = total_profit - total_expenses

    return render(request, 'expenseApp/expense_profit_summary.html', {
        'expenses': expenses,
        'total_profit': total_profit,
        'total_expenses': total_expenses,
        'net_profit': net_profit,
        'query': query,
        'min_amount': min_amount,
        'max_amount': max_amount,
        'start_date': start_date,
        'end_date': end_date,
    })
