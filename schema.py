from pydantic import BaseModel, Field
from typing import List, Dict

class Expense(BaseModel):
    expense_id: int = Field(..., description="A Unique Expense ID")
    date: str = Field(..., description="Date of the expense")
    description: str = Field(..., description="Description of the expense")
    amount: float = Field(..., description="Amount paid")


class ExpenseReport(BaseModel):
    expenses: List[Expense] = Field(..., description="List of expenses")
    total_spent: float = Field(..., description="A Unique Expense ID")
    

class CategorizedExpense(BaseModel):
    expense_id: int
    description: str
    category: str
    amount: float = Field(..., description="Amount paid")
    date: str = Field(..., description="Date of the expense")

class CategorizedExpenseReport(BaseModel):
    categorized_expenses: List[CategorizedExpense]

# class CalculateCategoryExpensesInput(BaseModel):
#     categorized_expenses: List[CategorizedExpense]
#     original_expenses: List[Expense]