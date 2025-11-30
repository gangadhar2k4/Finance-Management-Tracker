# MoneyFlow - Personal Finance Tracker

## Overview
MoneyFlow is a comprehensive personal finance management system built with Django. It helps users track income/expenses, set budgets, create savings goals, and visualize spending habits with a beautiful neon cyber security dark theme.

## Current State
The application is fully functional with all core MVP features implemented:
- User authentication (register, login, logout)
- Dashboard with financial overview and charts
- Transaction management with filtering
- Multiple accounts/wallets
- Budget planning with alerts
- Savings goals tracking
- Reports and analytics
- Neon cyber security dark theme

## Project Structure
```
/
├── moneyflow/           # Django project settings
│   ├── settings.py      # Main settings
│   ├── urls.py          # Root URL configuration
│   └── wsgi.py          # WSGI entry point
├── finance/             # Main application
│   ├── models.py        # Database models
│   ├── views.py         # View functions
│   ├── forms.py         # Form classes
│   ├── urls.py          # App URL patterns
│   └── admin.py         # Admin configuration
├── templates/           # HTML templates
│   └── finance/         # App templates
├── static/              # Static files
├── media/               # User uploads
├── manage.py            # Django CLI
└── db.sqlite3           # SQLite database
```

## Tech Stack
- **Backend**: Django 5.2
- **Database**: SQLite
- **Frontend**: Django Templates + Bootstrap 5
- **Charts**: Chart.js
- **Forms**: django-crispy-forms with Bootstrap 5

## Key Features
1. **Dashboard**: Total income, expenses, balance, net worth with charts
2. **Transactions**: Add/Edit/Delete with categories, accounts, tags
3. **Accounts**: Multiple wallets (Cash, Bank, UPI, Credit Cards)
4. **Categories**: Default categories with color coding
5. **Budgets**: Monthly budgets with progress bars and alerts
6. **Goals**: Savings goals with circular progress
7. **Reports**: Yearly trends and top spending categories

## Running the App
The app runs on port 5000 using Django's development server:
```bash
python manage.py runserver 0.0.0.0:5000
```

## Database
Using SQLite with the following models:
- UserProfile
- Account
- Category
- Transaction
- Budget
- SavingsGoal

## Recent Changes
- November 30, 2025: Initial implementation of all MVP features

## User Preferences
- Dark theme with neon cyan/purple color scheme
- Bootstrap 5 for responsive design
- Chart.js for data visualizations
