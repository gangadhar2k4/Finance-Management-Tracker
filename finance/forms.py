from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Account, Category, Transaction, Budget, SavingsGoal


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control bg-dark text-light border-secondary'
            })


class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control bg-dark text-light border-secondary'
            })


class AccountForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ['name', 'account_type', 'initial_balance', 'color', 'icon']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control bg-dark text-light border-secondary'}),
            'account_type': forms.Select(attrs={'class': 'form-select bg-dark text-light border-secondary'}),
            'initial_balance': forms.NumberInput(attrs={'class': 'form-control bg-dark text-light border-secondary', 'step': '0.01'}),
            'color': forms.TextInput(attrs={'class': 'form-control bg-dark text-light border-secondary', 'type': 'color'}),
            'icon': forms.Select(attrs={'class': 'form-select bg-dark text-light border-secondary'}),
        }
        labels = {
            'initial_balance': 'Initial Balance',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['icon'].widget = forms.Select(
            choices=[
                ('bi-wallet2', 'Wallet'),
                ('bi-bank', 'Bank'),
                ('bi-credit-card', 'Credit Card'),
                ('bi-cash', 'Cash'),
                ('bi-piggy-bank', 'Piggy Bank'),
                ('bi-safe', 'Safe'),
                ('bi-phone', 'Phone (UPI)'),
            ],
            attrs={'class': 'form-select bg-dark text-light border-secondary'}
        )


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'category_type', 'color', 'icon']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control bg-dark text-light border-secondary'}),
            'category_type': forms.Select(attrs={'class': 'form-select bg-dark text-light border-secondary'}),
            'color': forms.TextInput(attrs={'class': 'form-control bg-dark text-light border-secondary', 'type': 'color'}),
            'icon': forms.Select(attrs={'class': 'form-select bg-dark text-light border-secondary'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['icon'].widget = forms.Select(
            choices=[
                ('bi-tag', 'Tag'),
                ('bi-cup-hot', 'Food'),
                ('bi-car-front', 'Transport'),
                ('bi-bag', 'Shopping'),
                ('bi-receipt', 'Bills'),
                ('bi-controller', 'Entertainment'),
                ('bi-heart-pulse', 'Healthcare'),
                ('bi-book', 'Education'),
                ('bi-house', 'Home'),
                ('bi-briefcase', 'Work'),
                ('bi-gift', 'Gift'),
                ('bi-airplane', 'Travel'),
            ],
            attrs={'class': 'form-select bg-dark text-light border-secondary'}
        )


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['transaction_type', 'amount', 'category', 'account', 'date', 'description', 'tags']
        widgets = {
            'transaction_type': forms.Select(attrs={'class': 'form-select bg-dark text-light border-secondary'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control bg-dark text-light border-secondary', 'step': '0.01', 'min': '0.01'}),
            'category': forms.Select(attrs={'class': 'form-select bg-dark text-light border-secondary'}),
            'account': forms.Select(attrs={'class': 'form-select bg-dark text-light border-secondary'}),
            'date': forms.DateInput(attrs={'class': 'form-control bg-dark text-light border-secondary', 'type': 'date'}),
            'description': forms.TextInput(attrs={'class': 'form-control bg-dark text-light border-secondary', 'placeholder': 'What was this for?'}),
            'tags': forms.TextInput(attrs={'class': 'form-control bg-dark text-light border-secondary', 'placeholder': 'e.g., groceries, weekly'}),
        }

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.filter(user=user)
        self.fields['account'].queryset = Account.objects.filter(user=user, is_active=True)


class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ['category', 'amount', 'month', 'year', 'is_overall']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-select bg-dark text-light border-secondary'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control bg-dark text-light border-secondary', 'step': '0.01', 'min': '0.01'}),
            'month': forms.Select(attrs={'class': 'form-select bg-dark text-light border-secondary'}),
            'year': forms.NumberInput(attrs={'class': 'form-control bg-dark text-light border-secondary', 'min': '2020', 'max': '2030'}),
            'is_overall': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.filter(user=user, category_type='expense')
        self.fields['category'].required = False
        self.fields['month'].widget = forms.Select(
            choices=[(i, name) for i, name in enumerate(['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'], 1)],
            attrs={'class': 'form-select bg-dark text-light border-secondary'}
        )


class SavingsGoalForm(forms.ModelForm):
    class Meta:
        model = SavingsGoal
        fields = ['name', 'target_amount', 'current_amount', 'target_date', 'color', 'icon']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control bg-dark text-light border-secondary', 'placeholder': 'e.g., New Phone, Vacation'}),
            'target_amount': forms.NumberInput(attrs={'class': 'form-control bg-dark text-light border-secondary', 'step': '0.01', 'min': '0.01'}),
            'current_amount': forms.NumberInput(attrs={'class': 'form-control bg-dark text-light border-secondary', 'step': '0.01', 'min': '0'}),
            'target_date': forms.DateInput(attrs={'class': 'form-control bg-dark text-light border-secondary', 'type': 'date'}),
            'color': forms.TextInput(attrs={'class': 'form-control bg-dark text-light border-secondary', 'type': 'color'}),
            'icon': forms.Select(attrs={'class': 'form-select bg-dark text-light border-secondary'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['icon'].widget = forms.Select(
            choices=[
                ('bi-bullseye', 'Target'),
                ('bi-phone', 'Phone'),
                ('bi-car-front', 'Car'),
                ('bi-house', 'House'),
                ('bi-airplane', 'Travel'),
                ('bi-laptop', 'Laptop'),
                ('bi-gift', 'Gift'),
                ('bi-mortarboard', 'Education'),
                ('bi-heart', 'Health'),
                ('bi-piggy-bank', 'Savings'),
            ],
            attrs={'class': 'form-select bg-dark text-light border-secondary'}
        )


class TransactionFilterForm(forms.Form):
    start_date = forms.DateField(required=False, widget=forms.DateInput(
        attrs={'class': 'form-control bg-dark text-light border-secondary', 'type': 'date'}
    ))
    end_date = forms.DateField(required=False, widget=forms.DateInput(
        attrs={'class': 'form-control bg-dark text-light border-secondary', 'type': 'date'}
    ))
    transaction_type = forms.ChoiceField(
        required=False,
        choices=[('', 'All Types'), ('income', 'Income'), ('expense', 'Expense')],
        widget=forms.Select(attrs={'class': 'form-select bg-dark text-light border-secondary'})
    )
    category = forms.ModelChoiceField(
        required=False,
        queryset=Category.objects.none(),
        empty_label='All Categories',
        widget=forms.Select(attrs={'class': 'form-select bg-dark text-light border-secondary'})
    )
    account = forms.ModelChoiceField(
        required=False,
        queryset=Account.objects.none(),
        empty_label='All Accounts',
        widget=forms.Select(attrs={'class': 'form-select bg-dark text-light border-secondary'})
    )
    search = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control bg-dark text-light border-secondary', 'placeholder': 'Search transactions...'}
    ))

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.filter(user=user)
        self.fields['account'].queryset = Account.objects.filter(user=user)
