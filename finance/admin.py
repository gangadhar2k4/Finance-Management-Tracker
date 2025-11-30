from django.contrib import admin
from .models import UserProfile, Account, Category, Transaction, Budget, SavingsGoal


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'currency', 'created_at']


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'account_type', 'balance', 'is_active']
    list_filter = ['account_type', 'is_active']
    search_fields = ['name', 'user__username']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'category_type', 'color', 'is_default']
    list_filter = ['category_type', 'is_default']
    search_fields = ['name']


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['date', 'user', 'transaction_type', 'amount', 'category', 'account']
    list_filter = ['transaction_type', 'date', 'category']
    search_fields = ['description', 'tags']
    date_hierarchy = 'date'


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ['user', 'category', 'amount', 'month', 'year', 'is_overall']
    list_filter = ['month', 'year', 'is_overall']


@admin.register(SavingsGoal)
class SavingsGoalAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'target_amount', 'current_amount', 'target_date', 'is_completed']
    list_filter = ['is_completed', 'target_date']
    search_fields = ['name']
