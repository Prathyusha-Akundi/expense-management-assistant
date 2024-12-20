from langchain.agents import initialize_agent, Tool
from langchain.tools import BaseTool
from openai import OpenAI
from schema import *
from PIL import Image
from io import BytesIO
import base64
import os

class ScanBillTool(BaseTool):
    name:str = "scan_bill"
    description:str = "Extract data from a bill image."
    _llm: OpenAI
    
    class Config:
        arbitrary_types_allowed = True  

    def __init__(self):
        super().__init__()
        self._llm = OpenAI(api_key = os.environ.get("OPENAI_API_KEY"), organization=os.environ.get("OPENAI_ORGANIZATION"))

    def _run(self, image: Image) -> ExpenseReport:

        byte_io = BytesIO()
        image.save(byte_io, format='JPEG')
        byte_io.seek(0)    
        image_base64 = base64.b64encode(byte_io.read()).decode('utf-8')

        system_message = {
            "role": "system",
            "content": "You are a system that extracts structured expense data from bill images."
        }
        query = "Extract expense details from the attached bill image. Return the data in JSON format matching the ExpenseReport schema."
        user_message = {
            "role": "user",
            "content": [
                    {"type": "text", "text": query},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
                ]
        }
        response = self._llm.beta.chat.completions.parse(
            messages=[system_message, user_message], 
            response_format=ExpenseReport,
            model = "gpt-4o-mini-2024-07-18"
        )
        return response  # Response should adhere to the ExpenseReport schema
    
# Step 3: Tool for Categorizing Expenses
class CategorizeExpensesTool(BaseTool):
    name :str= "categorize_expenses"
    description:str = "Categorize expenses based on their descriptions using an LLM."
    _llm: OpenAI
    
    class Config:
        arbitrary_types_allowed = True  

    def __init__(self):
        super().__init__()
        self._llm = OpenAI(api_key = os.environ.get("OPENAI_API_KEY"), organization=os.environ.get("OPENAI_ORGANIZATION"))

    def _run(self, expenses: List[Expense]) -> CategorizedExpenseReport:
        
        system_message = {
            "role": "system",
            "content": "You are a system that categorizes expenses into predefined categories such as Groceries, Transport, Entertainment, Utilities, Miscellaneous, Shopping etc."
        }
        user_message = {
            "role": "user",
            "content": (
                "Categorize the following expenses:\n" + 
                str([expense.dict() for expense in expenses]) + "\n" +
                "Return the data in JSON format matching the CategorizedExpenseReport schema."
            )
        }
        response = self._llm.beta.chat.completions.parse(
            messages=[system_message, user_message], 
            response_format=CategorizedExpenseReport,
            model = "gpt-4o-mini-2024-07-18"
        )
        return response
    
class CalculateCategoryExpensesTool(BaseTool):
    name: str = "calculate_category_expenses"
    description: str = "Calculate the total expenses for each category."

    def _run(self, categorized_expenses: List[CategorizedExpense]) -> ExpenseReport:
        

        category_totals = {}
        total = 0.0

        for categorized_expense in categorized_expenses:
            # Use the amount from categorized_expense if available, otherwise fall back to the original expense amount
            amount =  categorized_expense.amount
            total += amount

            if categorized_expense.category in category_totals:
                category_totals[categorized_expense.category] += amount
            else:
                category_totals[categorized_expense.category] = amount

        return category_totals

    
