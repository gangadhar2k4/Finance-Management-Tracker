from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.db.models import Sum, Q
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
import json

from .models import UserProfile, Account, Category, Transaction, Budget, SavingsGoal
from .forms import (
    CustomUserCreationForm, CustomAuthenticationForm, AccountForm, 
    CategoryForm, TransactionForm, BudgetForm, SavingsGoalForm, TransactionFilterForm
)


def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user)
            Category.create_defaults_for_user(user)
            Account.objects.create(
                user=user,
                name='Cash',
                account_type='cash',
                color='#00d4ff',
                icon='bi-cash'
            )
            login(request, user)
            messages.success(request, 'Welcome to MoneyFlow! Your account has been created.')
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'finance/register.html', {'form': form})


class CustomLoginView(LoginView):
    authentication_form = CustomAuthenticationForm
    template_name = 'finance/login.html'
    redirect_authenticated_user = True


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')


@login_required
def dashboard(request):
    today = timezone.now()
    current_month = today.month
    current_year = today.year
    
    income_total = Transaction.objects.filter(
        user=request.user,
        transaction_type='income',
        date__month=current_month,
        date__year=current_year
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
    
    expense_total = Transaction.objects.filter(
        user=request.user,
        transaction_type='expense',
        date__month=current_month,
        date__year=current_year
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
    
    balance = income_total - expense_total
    
    net_worth = Account.objects.filter(
        user=request.user,
        is_active=True
    ).aggregate(total=Sum('balance'))['total'] or Decimal('0')
    
    expense_by_category = Transaction.objects.filter(
        user=request.user,
        transaction_type='expense',
        date__month=current_month,
        date__year=current_year,
        category__isnull=False
    ).values('category__name', 'category__color').annotate(
        total=Sum('amount')
    ).order_by('-total')[:8]
    
    months_data = []
    for i in range(5, -1, -1):
        month_date = today - timedelta(days=i*30)
        month_income = Transaction.objects.filter(
            user=request.user,
            transaction_type='income',
            date__month=month_date.month,
            date__year=month_date.year
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        month_expense = Transaction.objects.filter(
            user=request.user,
            transaction_type='expense',
            date__month=month_date.month,
            date__year=month_date.year
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        months_data.append({
            'month': month_date.strftime('%b'),
            'income': float(month_income),
            'expense': float(month_expense)
        })
    
    recent_transactions = Transaction.objects.filter(
        user=request.user
    ).select_related('category', 'account')[:5]
    
    accounts = Account.objects.filter(user=request.user, is_active=True)[:5]
    
    budgets = Budget.objects.filter(
        user=request.user,
        month=current_month,
        year=current_year
    ).select_related('category')[:4]
    
    goals = SavingsGoal.objects.filter(
        user=request.user,
        is_completed=False
    )[:3]
    
    context = {
        'income_total': income_total,
        'expense_total': expense_total,
        'balance': balance,
        'net_worth': net_worth,
        'expense_by_category': list(expense_by_category),
        'months_data': json.dumps(months_data),
        'recent_transactions': recent_transactions,
        'accounts': accounts,
        'budgets': budgets,
        'goals': goals,
        'current_month': today.strftime('%B %Y'),
    }
    
    return render(request, 'finance/dashboard.html', context)


@login_required
def transaction_list(request):
    transactions = Transaction.objects.filter(user=request.user).select_related('category', 'account')
    filter_form = TransactionFilterForm(request.user, request.GET)
    
    if filter_form.is_valid():
        if filter_form.cleaned_data.get('start_date'):
            transactions = transactions.filter(date__gte=filter_form.cleaned_data['start_date'])
        if filter_form.cleaned_data.get('end_date'):
            transactions = transactions.filter(date__lte=filter_form.cleaned_data['end_date'])
        if filter_form.cleaned_data.get('transaction_type'):
            transactions = transactions.filter(transaction_type=filter_form.cleaned_data['transaction_type'])
        if filter_form.cleaned_data.get('category'):
            transactions = transactions.filter(category=filter_form.cleaned_data['category'])
        if filter_form.cleaned_data.get('account'):
            transactions = transactions.filter(account=filter_form.cleaned_data['account'])
        if filter_form.cleaned_data.get('search'):
            search = filter_form.cleaned_data['search']
            transactions = transactions.filter(
                Q(description__icontains=search) | Q(tags__icontains=search)
            )
    
    return render(request, 'finance/transactions.html', {
        'transactions': transactions[:100],
        'filter_form': filter_form,
    })


@login_required
def transaction_create(request):
    if request.method == 'POST':
        form = TransactionForm(request.user, request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.save()
            messages.success(request, 'Transaction added successfully!')
            return redirect('transactions')
    else:
        form = TransactionForm(request.user)
    
    return render(request, 'finance/transaction_form.html', {
        'form': form,
        'title': 'Add Transaction'
    })


@login_required
def transaction_edit(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = TransactionForm(request.user, request.POST, instance=transaction)
        if form.is_valid():
            form.save()
            messages.success(request, 'Transaction updated successfully!')
            return redirect('transactions')
    else:
        form = TransactionForm(request.user, instance=transaction)
    
    return render(request, 'finance/transaction_form.html', {
        'form': form,
        'title': 'Edit Transaction'
    })


@login_required
def transaction_delete(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
    
    if request.method == 'POST':
        transaction.delete()
        messages.success(request, 'Transaction deleted successfully!')
        return redirect('transactions')
    
    return render(request, 'finance/confirm_delete.html', {
        'object': transaction,
        'type': 'transaction'
    })


@login_required
def account_list(request):
    accounts = Account.objects.filter(user=request.user)
    total_balance = accounts.filter(is_active=True).aggregate(total=Sum('balance'))['total'] or Decimal('0')
    
    return render(request, 'finance/accounts.html', {
        'accounts': accounts,
        'total_balance': total_balance,
    })


@login_required
def account_create(request):
    if request.method == 'POST':
        form = AccountForm(request.POST)
        if form.is_valid():
            account = form.save(commit=False)
            account.user = request.user
            account.balance = account.initial_balance
            account.save()
            messages.success(request, 'Account created successfully!')
            return redirect('accounts')
    else:
        form = AccountForm()
    
    return render(request, 'finance/account_form.html', {
        'form': form,
        'title': 'Add Account'
    })


@login_required
def account_edit(request, pk):
    account = get_object_or_404(Account, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = AccountForm(request.POST, instance=account)
        if form.is_valid():
            account = form.save()
            account.update_balance()
            account.refresh_from_db()
            messages.success(request, 'Account updated successfully!')
            return redirect('accounts')
    else:
        form = AccountForm(instance=account)
    
    return render(request, 'finance/account_form.html', {
        'form': form,
        'title': 'Edit Account'
    })


@login_required
def account_delete(request, pk):
    account = get_object_or_404(Account, pk=pk, user=request.user)
    
    if request.method == 'POST':
        account.delete()
        messages.success(request, 'Account deleted successfully!')
        return redirect('accounts')
    
    return render(request, 'finance/confirm_delete.html', {
        'object': account,
        'type': 'account'
    })


@login_required
def category_list(request):
    categories = Category.objects.filter(user=request.user)
    
    return render(request, 'finance/categories.html', {
        'categories': categories,
    })


@login_required
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.user = request.user
            category.save()
            messages.success(request, 'Category created successfully!')
            return redirect('categories')
    else:
        form = CategoryForm()
    
    return render(request, 'finance/category_form.html', {
        'form': form,
        'title': 'Add Category'
    })


@login_required
def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully!')
            return redirect('categories')
    else:
        form = CategoryForm(instance=category)
    
    return render(request, 'finance/category_form.html', {
        'form': form,
        'title': 'Edit Category'
    })


@login_required
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk, user=request.user)
    
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Category deleted successfully!')
        return redirect('categories')
    
    return render(request, 'finance/confirm_delete.html', {
        'object': category,
        'type': 'category'
    })


@login_required
def budget_list(request):
    today = timezone.now()
    budgets = Budget.objects.filter(
        user=request.user,
        month=today.month,
        year=today.year
    ).select_related('category')
    
    budget_data = []
    for budget in budgets:
        budget_data.append({
            'budget': budget,
            'spent': budget.get_spent(),
            'percentage': budget.get_percentage(),
            'remaining': budget.get_remaining(),
        })
    
    return render(request, 'finance/budgets.html', {
        'budget_data': budget_data,
        'current_month': today.strftime('%B %Y'),
    })


@login_required
def budget_create(request):
    if request.method == 'POST':
        form = BudgetForm(request.user, request.POST)
        if form.is_valid():
            budget = form.save(commit=False)
            budget.user = request.user
            if budget.is_overall:
                budget.category = None
            budget.save()
            messages.success(request, 'Budget created successfully!')
            return redirect('budgets')
    else:
        today = timezone.now()
        form = BudgetForm(request.user, initial={'month': today.month, 'year': today.year})
    
    return render(request, 'finance/budget_form.html', {
        'form': form,
        'title': 'Add Budget'
    })


@login_required
def budget_edit(request, pk):
    budget = get_object_or_404(Budget, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = BudgetForm(request.user, request.POST, instance=budget)
        if form.is_valid():
            budget = form.save(commit=False)
            if budget.is_overall:
                budget.category = None
            budget.save()
            messages.success(request, 'Budget updated successfully!')
            return redirect('budgets')
    else:
        form = BudgetForm(request.user, instance=budget)
    
    return render(request, 'finance/budget_form.html', {
        'form': form,
        'title': 'Edit Budget'
    })


@login_required
def budget_delete(request, pk):
    budget = get_object_or_404(Budget, pk=pk, user=request.user)
    
    if request.method == 'POST':
        budget.delete()
        messages.success(request, 'Budget deleted successfully!')
        return redirect('budgets')
    
    return render(request, 'finance/confirm_delete.html', {
        'object': budget,
        'type': 'budget'
    })


@login_required
def goal_list(request):
    goals = SavingsGoal.objects.filter(user=request.user)
    
    goal_data = []
    for goal in goals:
        goal_data.append({
            'goal': goal,
            'percentage': goal.get_percentage(),
            'remaining': goal.get_remaining(),
            'monthly_needed': goal.get_monthly_needed(),
        })
    
    return render(request, 'finance/goals.html', {
        'goal_data': goal_data,
    })


@login_required
def goal_create(request):
    if request.method == 'POST':
        form = SavingsGoalForm(request.POST)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.user = request.user
            goal.save()
            messages.success(request, 'Savings goal created successfully!')
            return redirect('goals')
    else:
        form = SavingsGoalForm()
    
    return render(request, 'finance/goal_form.html', {
        'form': form,
        'title': 'Add Savings Goal'
    })


@login_required
def goal_edit(request, pk):
    goal = get_object_or_404(SavingsGoal, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = SavingsGoalForm(request.POST, instance=goal)
        if form.is_valid():
            goal = form.save()
            if goal.current_amount >= goal.target_amount:
                goal.is_completed = True
                goal.save()
            messages.success(request, 'Savings goal updated successfully!')
            return redirect('goals')
    else:
        form = SavingsGoalForm(instance=goal)
    
    return render(request, 'finance/goal_form.html', {
        'form': form,
        'title': 'Edit Savings Goal'
    })


@login_required
def goal_delete(request, pk):
    goal = get_object_or_404(SavingsGoal, pk=pk, user=request.user)
    
    if request.method == 'POST':
        goal.delete()
        messages.success(request, 'Savings goal deleted successfully!')
        return redirect('goals')
    
    return render(request, 'finance/confirm_delete.html', {
        'object': goal,
        'type': 'savings goal'
    })


@login_required
def reports(request):
    today = timezone.now()
    
    monthly_data = []
    for i in range(11, -1, -1):
        month_date = today - timedelta(days=i*30)
        income = Transaction.objects.filter(
            user=request.user,
            transaction_type='income',
            date__month=month_date.month,
            date__year=month_date.year
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        expense = Transaction.objects.filter(
            user=request.user,
            transaction_type='expense',
            date__month=month_date.month,
            date__year=month_date.year
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        monthly_data.append({
            'month': month_date.strftime('%b %Y'),
            'income': float(income),
            'expense': float(expense),
            'savings': float(income) - float(expense)
        })
    
    top_categories = Transaction.objects.filter(
        user=request.user,
        transaction_type='expense',
        date__year=today.year
    ).values('category__name', 'category__color').annotate(
        total=Sum('amount')
    ).order_by('-total')[:10]
    
    return render(request, 'finance/reports.html', {
        'monthly_data': json.dumps(monthly_data),
        'top_categories': list(top_categories),
    })


@login_required
def api_chart_data(request):
    today = timezone.now()
    
    expense_by_category = Transaction.objects.filter(
        user=request.user,
        transaction_type='expense',
        date__month=today.month,
        date__year=today.year,
        category__isnull=False
    ).values('category__name', 'category__color').annotate(
        total=Sum('amount')
    ).order_by('-total')[:8]
    
    return JsonResponse({
        'expense_by_category': list(expense_by_category)
    })
