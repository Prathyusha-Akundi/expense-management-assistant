
from agent import *
import json
from dotenv import load_dotenv

class ExpenseManager:
    """
    Orchestrates the entire process of managing expenses:
    - Parsing bills from images
    - Categorizing expenses
    - Calculating category-wise expenses
    - Answering user queries based on the processed data
    """

    def __init__(self, images):
        """
        Initializes the ExpenseManager with a list of image paths and an instance of ExpenseAgent.
        Also, processes all bills upon initialization.
        """
        self.images = images
        self.agent = ExpenseAgent()
        self.parse_all_bills()
        self.populate_categories()
        self.calculate_category_expense()
        
    def merge_expense_reports(self, reports):
        """
        Merges multiple ExpenseReport objects into one by combining expenses
        and summing up the total spent.
        """
        merged_expenses = []
        total_spent = 0
        for report in reports:
            merged_expenses.extend(report.expenses)  # Combine expenses
            total_spent += report.total_spent  # Sum total spent
        # Create a new merged ExpenseReport
        new_report = ExpenseReport(expenses=merged_expenses, total_spent=total_spent)
        return new_report
    
    def parse_bill(self, image):
        """
        Parses a single bill image into an ExpenseReport object using the agent.
        """
        expense_report = self.agent.scan_bill(image)
        expense_report = expense_report.choices[0].message.parsed  # Extract parsed data
        return expense_report
    
    def parse_all_bills(self):
        """
        Processes all bill images, parses them into ExpenseReport objects, and merges them.
        """
        reports = []
        for image in self.images:
            expense_report = self.parse_bill(image)
            reports.append(expense_report)  # Collect individual reports
        # Merge all reports into a single ExpenseReport
        self.final_expense_report = self.merge_expense_reports(reports)

    def populate_categories(self):
        """
        Categorizes expenses in the final expense report using the agent.
        """
        categorized_expense_report = self.agent.categorize_expenses(self.final_expense_report)
        # Extract parsed data from the agent's response
        self.categorized_expense_report = categorized_expense_report.choices[0].message.parsed

    def calculate_category_expense(self):
        """
        Calculates total expenses for each category using the categorized expense report.
        """
        self.category_expense_report = self.agent.calculate_expenses(self.categorized_expense_report)

    def answer_user_query(self, query):
        """
        Answers user queries based on the categorized expenses and category-wise expense report.
        """
        context = {
            "expenses": self.categorized_expense_report, 
            "category_expense_report": self.category_expense_report
        }
        # Query the agent for answers
        response = self.agent.answer_query(query, context)
        return response
    

if __name__ == "__main__":

    load_dotenv("env/.env")
    # Example usage
    image_paths = ["/Users/koundinya/Documents/prathyusha/projects/bills/electricity_bill.jpg","/Users/koundinya/Documents/prathyusha/projects/bills/other_bill.jpg","/Users/koundinya/Documents/prathyusha/projects/bills/restaurant.jpg","/Users/koundinya/Documents/prathyusha/projects/bills/ticket.jpg"]  # List of paths to bill images to be processed
    images = [Image.open(image_path) for image_path in image_paths]
    expense_manager = ExpenseManager(image_paths)

    # Outputs
    print(expense_manager.categorized_expense_report)
    print(expense_manager.category_expense_report)

    # Query example
    response = expense_manager.answer_user_query(query="What is the highest expense category?")
    print(response)
