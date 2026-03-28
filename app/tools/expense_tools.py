# app/tools/expense_tools.py

from sqlalchemy import extract, func
from app.database import SessionLocal
from app.models import Expense
from app.schemas import ExpenseCreate
from datetime import date
from typing import Optional


def get_db():
    """Open and return a database session."""
    return SessionLocal()


def add_expense(
    amount: float,
    category: str,
    description: Optional[str] = None,
    expense_date: Optional[date] = None,
) -> dict:
    """
    Save a new expense to the database.
    If no date is given, use today's date automatically.
    """
    db = get_db()
    try:
        expense = Expense(
            amount=amount,
            category=category.lower().strip(),
            description=description,
            expense_date=expense_date or date.today(),  # default to today
        )
        db.add(expense)
        db.commit()
        db.refresh(expense)  # reload from DB to get the generated id

        return {
            "success": True,
            "id": expense.id,
            "amount": expense.amount,
            "category": expense.category,
            "description": expense.description,
            "expense_date": str(expense.expense_date),
        }
    except Exception as e:
        db.rollback()  # undo if something went wrong
        return {"success": False, "error": str(e)}
    finally:
        db.close()


def update_expense(
    expense_id: int,
    amount: Optional[float] = None,
    category: Optional[str] = None,
    description: Optional[str] = None,
    expense_date: Optional[date] = None,
) -> dict:
    """Update an existing expense by id.

    Only fields that are provided (not None) will be updated.
    Returns the updated expense data or an error.
    """
    db = get_db()
    try:
        expense = db.query(Expense).filter(Expense.id == expense_id).first()
        if not expense:
            return {"success": False, "error": "Expense not found"}

        if amount is not None:
            expense.amount = amount
        if category is not None:
            expense.category = category.lower().strip()
        if description is not None:
            expense.description = description
        if expense_date is not None:
            expense.expense_date = expense_date

        db.commit()
        db.refresh(expense)

        return {
            "success": True,
            "id": expense.id,
            "amount": expense.amount,
            "category": expense.category,
            "description": expense.description,
            "expense_date": str(expense.expense_date),
        }
    except Exception as e:
        db.rollback()
        return {"success": False, "error": str(e)}
    finally:
        db.close()


def delete_expense(expense_id: int) -> dict:
    """Delete an existing expense by id.

    Use together with get_recent_expenses to let the user
    confirm which expense they want to remove.
    """
    db = get_db()
    try:
        expense = db.query(Expense).filter(Expense.id == expense_id).first()
        if not expense:
            return {"success": False, "error": "Expense not found"}

        db.delete(expense)
        db.commit()

        return {"success": True, "id": expense_id}
    except Exception as e:
        db.rollback()
        return {"success": False, "error": str(e)}
    finally:
        db.close()


def get_monthly_spending(year: int, month: int) -> dict:
    """
    Get total amount spent in a given month.
    Example: get_monthly_spending(2025, 6)
    """
    db = get_db()
    try:
        total = (
            db.query(func.sum(Expense.amount))
            .filter(
                extract("year", Expense.expense_date) == year,
                extract("month", Expense.expense_date) == month,
            )
            .scalar()
        )  # .scalar() returns a single value instead of a list

        return {
            "year": year,
            "month": month,
            "total_spent": round(total or 0, 2),  # if no expenses, return 0
        }
    finally:
        db.close()


def get_spending_by_category(year: int, month: int) -> dict:
    """
    Get spending broken down by category for a given month.
    Example result: {"food": 3200, "transport": 800, "shopping": 1500}
    """
    db = get_db()
    try:
        rows = (
            db.query(Expense.category, func.sum(Expense.amount).label("total"))
            .filter(
                extract("year", Expense.expense_date) == year,
                extract("month", Expense.expense_date) == month,
            )
            .group_by(Expense.category)
            .all()
        )

        return {
            "year": year,
            "month": month,
            "breakdown": {row.category: round(row.total, 2) for row in rows},
        }
    finally:
        db.close()


def get_recent_expenses(limit: int = 10) -> dict:
    """
    Get the most recent expenses.
    Useful when user asks 'what did I spend recently?'
    """
    db = get_db()
    try:
        expenses = (
            db.query(Expense)
            .order_by(Expense.expense_date.desc(), Expense.created_at.desc())
            .limit(limit)
            .all()
        )

        return {
            "expenses": [
                {
                    "id": e.id,
                    "amount": e.amount,
                    "category": e.category,
                    "description": e.description,
                    "date": str(e.expense_date),
                }
                for e in expenses
            ]
        }
    finally:
        db.close()


def get_spending_on_date(target_date: date) -> dict:
    """Get total amount spent on a specific calendar date.

    Used for questions like "how much did I spend today?".
    """
    db = get_db()
    try:
        total = (
            db.query(func.sum(Expense.amount))
            .filter(Expense.expense_date == target_date)
            .scalar()
        ) or 0

        return {
            "date": str(target_date),
            "total_spent": round(total, 2),
        }
    finally:
        db.close()
