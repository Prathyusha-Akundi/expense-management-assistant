from langchain.agents import initialize_agent
from PIL import Image
from langchain_core.messages import HumanMessage, SystemMessage
from langchain.chat_models import ChatOpenAI
from schema import *
from tools import ScanBillTool, CategorizeExpensesTool, CalculateCategoryExpensesTool

class ExpenseAgent:
    def __init__(self):
        self.query_llm = ChatOpenAI(model="gpt-4o-mini-2024-07-18")
        self.tools = [CategorizeExpensesTool(), CalculateCategoryExpensesTool()]
        self.agent = initialize_agent(
            self.tools, self.query_llm, agent="zero-shot-react-description", verbose=False, handle_parsing_errors=True
        )

    def scan_bill(self, image: Image):
        scan_tool = ScanBillTool()
        raw_expenses = scan_tool._run(image)
        return raw_expenses

    def categorize_expenses(self, raw_expenses: ExpenseReport):
        categorize_tool = CategorizeExpensesTool()
        categorized_expenses = categorize_tool._run(raw_expenses.expenses)
        return categorized_expenses

    def calculate_expenses(self, categorized_expenses: CategorizedExpenseReport):
        calculate_tool = CalculateCategoryExpensesTool()
        return calculate_tool._run(categorized_expenses.categorized_expenses)

    def answer_query(self, query: str, context: Dict):
        messages = [
        SystemMessage(content="You are an assistant for expense analysis. Use the provided context to answer the query directly.Do not invoke any tools to answer the query unnecesarily. Strictly answer from context. If there is no enough information to answer from context, respond as 'No Enough Information available to answer the query'"),
        HumanMessage(content=f"Answer the use query based on below context strictly. \nContext: {context} \nUser Query: {query}")
    ]
        return self.agent.invoke(messages )["output"]