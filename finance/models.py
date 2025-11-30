from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    currency = models.CharField(max_length=10, default='$')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"


class Account(models.Model):
    ACCOUNT_TYPES = [
        ('cash', 'Cash'),
        ('bank', 'Bank Account'),
        ('upi', 'UPI Wallet'),
        ('credit', 'Credit Card'),
        ('savings', 'Savings Account'),
        ('investment', 'Investment'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='accounts')
    name = models.CharField(max_length=100)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES, default='bank')
    initial_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    color = models.CharField(max_length=7, default='#00d4ff')
    icon = models.CharField(max_length=50, default='bi-wallet2')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.get_account_type_display()})"

    def update_balance(self):
        income = self.transactions.filter(transaction_type='income').aggregate(
            total=models.Sum('amount'))['total'] or Decimal('0')
        expense = self.transactions.filter(transaction_type='expense').aggregate(
            total=models.Sum('amount'))['total'] or Decimal('0')
        self.balance = self.initial_balance + income - expense
        self.save(update_fields=['balance'])


class Category(models.Model):
    CATEGORY_TYPES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
    ]
    
    DEFAULT_CATEGORIES = [
        ('Food & Dining', 'expense', '#ff6b6b', 'bi-cup-hot'),
        ('Transport', 'expense', '#4ecdc4', 'bi-car-front'),
        ('Shopping', 'expense', '#45b7d1', 'bi-bag'),
        ('Bills & Utilities', 'expense', '#96ceb4', 'bi-receipt'),
        ('Entertainment', 'expense', '#dfe6e9', 'bi-controller'),
        ('Healthcare', 'expense', '#fd79a8', 'bi-heart-pulse'),
        ('Education', 'expense', '#a29bfe', 'bi-book'),
        ('Personal Care', 'expense', '#ffeaa7', 'bi-person'),
        ('Groceries', 'expense', '#55efc4', 'bi-cart'),
        ('Rent', 'expense', '#fab1a0', 'bi-house'),
        ('Subscriptions', 'expense', '#74b9ff', 'bi-credit-card'),
        ('Other Expense', 'expense', '#b2bec3', 'bi-three-dots'),
        ('Salary', 'income', '#00b894', 'bi-briefcase'),
        ('Freelance', 'income', '#00cec9', 'bi-laptop'),
        ('Investment Returns', 'income', '#0984e3', 'bi-graph-up'),
        ('Gift', 'income', '#e17055', 'bi-gift'),
        ('Refund', 'income', '#fdcb6e', 'bi-arrow-counterclockwise'),
        ('Other Income', 'income', '#636e72', 'bi-plus-circle'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='categories', null=True, blank=True)
    name = models.CharField(max_length=100)
    category_type = models.CharField(max_length=10, choices=CATEGORY_TYPES)
    color = models.CharField(max_length=7, default='#00d4ff')
    icon = models.CharField(max_length=50, default='bi-tag')
    is_default = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.get_category_type_display()})"

    @classmethod
    def create_defaults_for_user(cls, user):
        for name, cat_type, color, icon in cls.DEFAULT_CATEGORIES:
            cls.objects.get_or_create(
                user=user,
                name=name,
                defaults={
                    'category_type': cat_type,
                    'color': color,
                    'icon': icon,
                    'is_default': True
                }
            )


class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='transactions')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='transactions')
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    description = models.CharField(max_length=255, blank=True)
    date = models.DateField(default=timezone.now)
    tags = models.CharField(max_length=255, blank=True)
    receipt = models.ImageField(upload_to='receipts/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.transaction_type}: {self.amount} - {self.description[:30]}"

    def save(self, *args, **kwargs):
        old_account = None
        if self.pk:
            try:
                old_transaction = Transaction.objects.get(pk=self.pk)
                if old_transaction.account_id != self.account_id:
                    old_account = old_transaction.account
            except Transaction.DoesNotExist:
                pass
        
        super().save(*args, **kwargs)
        self.account.update_balance()
        
        if old_account:
            old_account.update_balance()

    def delete(self, *args, **kwargs):
        account = self.account
        super().delete(*args, **kwargs)
        account.update_balance()


class Budget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='budgets')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True, related_name='budgets')
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    month = models.IntegerField()
    year = models.IntegerField()
    is_overall = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'category', 'month', 'year', 'is_overall']

    def __str__(self):
        if self.is_overall:
            return f"Overall Budget: {self.amount} ({self.month}/{self.year})"
        return f"{self.category.name} Budget: {self.amount} ({self.month}/{self.year})"

    def get_spent(self):
        from django.db.models import Sum
        filters = {
            'user': self.user,
            'transaction_type': 'expense',
            'date__month': self.month,
            'date__year': self.year,
        }
        if not self.is_overall and self.category:
            filters['category'] = self.category
        
        spent = Transaction.objects.filter(**filters).aggregate(
            total=Sum('amount'))['total'] or Decimal('0')
        return spent

    def get_percentage(self):
        if self.amount == 0:
            return 0
        return min(100, int((self.get_spent() / self.amount) * 100))

    def get_remaining(self):
        return max(Decimal('0'), self.amount - self.get_spent())


class SavingsGoal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='savings_goals')
    name = models.CharField(max_length=100)
    target_amount = models.DecimalField(max_digits=15, decimal_places=2)
    current_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    target_date = models.DateField()
    color = models.CharField(max_length=7, default='#00d4ff')
    icon = models.CharField(max_length=50, default='bi-bullseye')
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['target_date']

    def __str__(self):
        return f"{self.name}: {self.current_amount}/{self.target_amount}"

    def get_percentage(self):
        if self.target_amount == 0:
            return 0
        return min(100, int((self.current_amount / self.target_amount) * 100))

    def get_remaining(self):
        return max(Decimal('0'), self.target_amount - self.current_amount)

    def get_monthly_needed(self):
        from datetime import date
        today = date.today()
        if self.target_date <= today:
            return self.get_remaining()
        months_left = (self.target_date.year - today.year) * 12 + (self.target_date.month - today.month)
        if months_left <= 0:
            return self.get_remaining()
        return self.get_remaining() / months_left
