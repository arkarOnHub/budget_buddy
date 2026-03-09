# test_tools.py
from app.tools.expense_tools import (
    add_expense,
    get_monthly_spending,
    get_spending_by_category,
)
from app.tools.budget_tools import (
    set_budget,
    get_remaining_budget,
    get_daily_spending_limit,
)
from datetime import date

# Test 1: Set a budget
print(set_budget("2025-06", 15000))

# Test 2: Add some expenses
print(add_expense(50, "food", "lunch"))
print(add_expense(70, "food", "coffee"))
print(add_expense(120, "transport", "taxi"))

# Test 3: Check spending
print(get_monthly_spending(2025, 6))
print(get_spending_by_category(2025, 6))

# Test 4: Check remaining budget
print(get_remaining_budget(2025, 6))

# Test 5: Daily limit
print(get_daily_spending_limit(2025, 6))
