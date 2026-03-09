# app/agent/agent.py

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from app.tools.expense_tools import (
    add_expense,
    get_monthly_spending,
    get_spending_by_category,
    get_recent_expenses,
)
from app.tools.budget_tools import (
    set_budget,
    get_remaining_budget,
    get_daily_spending_limit,
)
from dotenv import load_dotenv
import os

load_dotenv()


# ── Wrap each function as a LangChain tool ──────────────────────────────────
# The @tool decorator does 2 things:
# 1. Tells LangChain this function is callable by the AI
# 2. Uses the docstring to tell the AI WHEN to call it


@tool
def tool_add_expense(
    amount: float, category: str, description: str = None, expense_date: str = None
) -> dict:
    """
    Use this to save a new expense to the database.
    Call this when user mentions spending money on anything.
    expense_date format: "YYYY-MM-DD". If not mentioned use today's date.
    """
    from datetime import date

    parsed_date = None
    if expense_date:
        try:
            from datetime import datetime

            parsed_date = datetime.strptime(expense_date, "%Y-%m-%d").date()
        except:
            parsed_date = date.today()

    return add_expense(amount, category, description, parsed_date)


@tool
def tool_set_budget(month: str, amount: float) -> dict:
    """
    Use this to set or update the monthly budget.
    Call this when user says things like:
    'my budget this month is 15000' or 'set June budget to 20000'.
    month format: 'YYYY-MM' e.g. '2025-06'
    """
    return set_budget(month, amount)


@tool
def tool_get_monthly_spending(year: int, month: int) -> dict:
    """
    Use this to get total spending for a specific month.
    Call this when user asks 'how much did I spend in June?' or
    'what is my total spending this month?'
    """
    return get_monthly_spending(year, month)


@tool
def tool_get_spending_by_category(year: int, month: int) -> dict:
    """
    Use this to get spending broken down by category.
    Call this when user asks 'what did I spend on food?' or
    'show me my spending by category'.
    """
    return get_spending_by_category(year, month)


@tool
def tool_get_remaining_budget(year: int, month: int) -> dict:
    """
    Use this to check how much budget is remaining.
    Call this when user asks 'how much do I have left?' or
    'can I still spend more?' or 'am I over budget?'
    """
    return get_remaining_budget(year, month)


@tool
def tool_get_daily_spending_limit(year: int, month: int) -> dict:
    """
    Use this to calculate how much the user can spend per day
    for the rest of the month.
    Call this when user asks 'how much can I spend per day?' or
    'what is my daily limit?'
    """
    return get_daily_spending_limit(year, month)


@tool
def tool_get_recent_expenses(limit: int = 10) -> dict:
    """
    Use this to get the most recent expenses.
    Call this when user asks 'what did I spend recently?' or
    'show my last expenses'.
    """
    return get_recent_expenses(limit)


# ── All tools in one list ───────────────────────────────────────────────────
tools = [
    tool_add_expense,
    tool_set_budget,
    tool_get_monthly_spending,
    tool_get_spending_by_category,
    tool_get_remaining_budget,
    tool_get_daily_spending_limit,
    tool_get_recent_expenses,
]


# ── The LLM ─────────────────────────────────────────────────────────────────
def get_llm():
    return ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        google_api_key=os.getenv("GEMINI_API_KEY"),
        temperature=0,  # 0 = consistent, predictable responses
    )
