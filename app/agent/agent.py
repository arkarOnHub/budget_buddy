# app/agent/agent.py

from langchain_groq import ChatGroq
from langchain_core.tools import tool
from app.tools.expense_tools import (
    add_expense,
    get_monthly_spending,
    get_spending_by_category,
    get_recent_expenses,
    update_expense,
    delete_expense,
    get_spending_on_date,
)
from app.tools.budget_tools import (
    set_budget,
    get_remaining_budget,
    get_daily_spending_limit,
    delete_budget,
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
    'my budget this month is 15000' or 'set June budget to 20000',
    or 'change my budget to 18000'.
    month format: 'YYYY-MM' e.g. '2025-06'
    """
    return set_budget(month, amount)


@tool
def tool_delete_budget(month: str) -> dict:
    """
    Use this to remove or delete the budget for a specific month.
    Call this when user says things like:
    'delete my budget for this month' or 'remove June budget'.
    month format: 'YYYY-MM' e.g. '2025-06'
    """
    return delete_budget(month)


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


@tool
def tool_get_spending_today() -> dict:
    """Get total spending for TODAY only.

    Use this when the user asks things like:
    - "how much did I spend today?"
    - "how much did I use today?"
    - "what's my spending today?"

    This should not be used for questions about the whole month;
    for that, use the monthly spending tool instead.
    """
    from datetime import date as _date

    return get_spending_on_date(_date.today())


@tool
def tool_update_expense(
    expense_id: int,
    amount: float | None = None,
    description: str | None = None,
    category: str | None = None,
    expense_date: str | None = None,
) -> dict:
    """Update an existing expense.

    Use this when the user wants to correct a saved expense, e.g.:
    - "change my lunch cost from 50 to 60"
    - "update today's coffee expense to 80 baht"

    Typically you should first call tool_get_recent_expenses to
    identify the correct expense and its id. Only fields that are
    provided will be changed.

    expense_date format: "YYYY-MM-DD" if provided.
    """
    from datetime import datetime

    parsed_date = None
    if expense_date:
        try:
            parsed_date = datetime.strptime(expense_date, "%Y-%m-%d").date()
        except Exception:
            parsed_date = None

    return update_expense(
        expense_id=expense_id,
        amount=amount,
        category=category,
        description=description,
        expense_date=parsed_date,
    )


@tool
def tool_delete_expense(expense_id: int) -> dict:
    """Delete an existing expense by id.

    Use this when the user wants to remove a mistaken entry, e.g.:
    - "remove my lunch today"
    - "delete that duplicate coffee expense"

    You should normally call tool_get_recent_expenses first so you
    (and the user) can verify which expense id to delete.
    """
    return delete_expense(expense_id)


# ── All tools in one list ───────────────────────────────────────────────────
tools = [
    tool_add_expense,
    tool_set_budget,
    tool_delete_budget,
    tool_get_monthly_spending,
    tool_get_spending_by_category,
    tool_get_remaining_budget,
    tool_get_daily_spending_limit,
    tool_get_recent_expenses,
    tool_get_spending_today,
    tool_update_expense,
    tool_delete_expense,
]


# ── The LLM ─────────────────────────────────────────────────────────────────
def get_llm():
    """Return the configured Groq chat model.

    Environment variables you can tweak without changing code:
    - GROQ_MODEL: override the default model name
    - GROQ_MAX_TOKENS: cap response length (int)
    """
    model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
    max_tokens_env = os.getenv("GROQ_MAX_TOKENS")
    max_tokens = int(max_tokens_env) if max_tokens_env else None

    return ChatGroq(
        model=model,
        groq_api_key=os.getenv("GROQ_API_KEY"),
        temperature=0,  # 0 = consistent, predictable responses
        max_tokens=max_tokens,
    )
