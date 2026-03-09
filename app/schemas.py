# app/schemas.py

from pydantic import BaseModel, Field
from datetime import date
from typing import Optional


class ExpenseCreate(BaseModel):
    amount: float
    category: str
    description: Optional[str] = None
    expense_date: date = Field(default_factory=date.today)


class ExpenseResponse(BaseModel):
    id: int
    amount: float
    category: str
    description: Optional[str]
    expense_date: date

    model_config = {"from_attributes": True}


class BudgetSet(BaseModel):
    month: str = Field(..., description="Format: YYYY-MM e.g. 2025-06")
    amount: float


class BudgetResponse(BaseModel):
    id: int
    month: str
    amount: float

    model_config = {"from_attributes": True}
