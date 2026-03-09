# app/models.py

from sqlalchemy import Column, Integer, String, Float, Date, DateTime, func
from app.database import Base
from datetime import date


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, nullable=False)
    category = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)
    expense_date = Column(Date, nullable=False, default=date.today)
    created_at = Column(DateTime, server_default=func.now())


class Budget(Base):
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True, index=True)
    month = Column(String(7), nullable=False, unique=True)  # "2025-06"
    amount = Column(Float, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
