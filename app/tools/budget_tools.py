# app/tools/budget_tools.py

from sqlalchemy import extract, func
from app.database import SessionLocal
from app.models import Budget, Expense
from datetime import date
from calendar import monthrange


def get_db():
    return SessionLocal()


def set_budget(month: str, amount: float) -> dict:
    """
    Set or update the budget for a given month.
    month format: "YYYY-MM" e.g. "2025-06"

    This is an UPSERT:
    - If budget for that month doesn't exist → create it
    - If it already exists → update the amount
    """
    db = get_db()
    try:
        existing = db.query(Budget).filter(Budget.month == month).first()

        if existing:
            # Update
            old_amount = existing.amount
            existing.amount = amount
            db.commit()
            return {
                "success": True,
                "action": "updated",
                "month": month,
                "old_amount": old_amount,
                "new_amount": amount,
            }
        else:
            # Create new
            budget = Budget(month=month, amount=amount)
            db.add(budget)
            db.commit()
            return {
                "success": True,
                "action": "created",
                "month": month,
                "amount": amount,
            }
    except Exception as e:
        db.rollback()
        return {"success": False, "error": str(e)}
    finally:
        db.close()


def get_remaining_budget(year: int, month: int) -> dict:
    """
    Calculate how much budget is left for a given month.

    Formula: remaining = budget - total_spent
    """
    db = get_db()
    try:
        month_str = f"{year}-{month:02d}"  # "2025-06"

        # Get budget for this month
        budget = db.query(Budget).filter(Budget.month == month_str).first()

        if not budget:
            return {
                "success": False,
                "message": f"No budget set for {month_str}. Tell me your budget first!",
            }

        # Get total spent this month
        total_spent = (
            db.query(func.sum(Expense.amount))
            .filter(
                extract("year", Expense.expense_date) == year,
                extract("month", Expense.expense_date) == month,
            )
            .scalar()
            or 0
        )

        remaining = budget.amount - total_spent

        return {
            "success": True,
            "month": month_str,
            "budget": budget.amount,
            "total_spent": round(total_spent, 2),
            "remaining": round(remaining, 2),
            "is_over_budget": remaining < 0,
        }
    finally:
        db.close()


def get_daily_spending_limit(year: int, month: int) -> dict:
    """
    Calculate how much the user can spend per day
    for the rest of the month to stay within budget.

    Formula: daily_limit = remaining_budget / days_left_in_month
    """
    db = get_db()
    try:
        month_str = f"{year}-{month:02d}"
        today = date.today()

        # Get remaining budget
        budget_row = db.query(Budget).filter(Budget.month == month_str).first()
        if not budget_row:
            return {"success": False, "message": f"No budget set for {month_str}."}

        total_spent = (
            db.query(func.sum(Expense.amount))
            .filter(
                extract("year", Expense.expense_date) == year,
                extract("month", Expense.expense_date) == month,
            )
            .scalar()
            or 0
        )

        remaining = budget_row.amount - total_spent

        # How many days are left in this month including today
        last_day = monthrange(year, month)[1]  # total days in month
        days_left = last_day - today.day + 1

        if days_left <= 0:
            daily_limit = 0
        else:
            daily_limit = remaining / days_left

        return {
            "success": True,
            "month": month_str,
            "remaining_budget": round(remaining, 2),
            "days_left": days_left,
            "daily_limit": round(daily_limit, 2),
            "is_over_budget": remaining < 0,
        }
    finally:
        db.close()
