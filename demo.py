import gradio as gr
import pandas as pd
from expense_manager import ExpenseManager
from dotenv import load_dotenv
from PIL import Image
from io import BytesIO
import seaborn as sns
import matplotlib.pyplot as plt

def create_pie_chart_with_seaborn(category_expense_report):
    """
    Creates a pie chart from the category_expense_report using Seaborn and saves it as an image.
    """
    categories = list(category_expense_report.keys())
    amounts = list(category_expense_report.values())

    # Create a DataFrame for Seaborn
    data = pd.DataFrame({"Category": categories, "Amount": amounts})

    # Plot using Seaborn's barplot as an alternative to pie chart for better visuals
    plt.figure(figsize=(10, 6))
    sns.set_theme(style="whitegrid")
    sns.barplot(x="Amount", y="Category", data=data, palette="viridis")
    plt.title("Category-Wise Expenses")
    plt.xlabel("Cumulative Expense")
    plt.ylabel("Category")
    plt.tight_layout()

    # Save the chart to a BytesIO object
    chart_buffer = BytesIO()
    plt.savefig(chart_buffer, format="png")
    plt.close()
    chart_buffer.seek(0)
    return chart_buffer

def process_expenses(images, state):
    images = [Image.open(img) for img in images]
    # Initialize or update the ExpenseManager
    if state is None or state.get("manager") is None:
        expense_manager = ExpenseManager(images)
        state = {"manager": expense_manager}  # Initialize the state with the manager
    else:
        # Update the existing manager with new images
        state["manager"].images = images
        state["manager"].parse_all_bills()
        state["manager"].populate_categories()
        state["manager"].calculate_category_expense()

    # Prepare categorized expense data for table
    categorized_data = []
    for i, expense in enumerate(state["manager"].categorized_expense_report.categorized_expenses):
        categorized_data.append({
            "Expense ID": i+1,
            "Description": expense.description,
            "Category": expense.category,
            "Amount": expense.amount
        })

    # Create a DataFrame for exporting as a table
    df_categorized = pd.DataFrame(categorized_data)
    print(df_categorized)
    export_file = "categorized_expenses.csv"
    df_categorized.to_csv(export_file, index=False)

    # Generate a pie chart with Seaborn
    chart_buffer = create_pie_chart_with_seaborn(state["manager"].category_expense_report)
    chart_file = "category_expenses_chart.png"
    with open(chart_file, "wb") as f:
        f.write(chart_buffer.read())

    # Display categorized expense report and export link
    return df_categorized, export_file, chart_file, chart_file, gr.update(visible=True), gr.update(visible=True), gr.update(visible=True), gr.update(visible=True), state

def chat_with_manager(query, state):
    """
    Handles user queries by interacting with the ExpenseManager.
    """
    if state is None or state.get("manager") is None:
        return "No Expense Manager is available. Please upload bills first."
    
    # Use the ExpenseManager instance in the state to answer queries
    response = state["manager"].answer_user_query(query)
    return response
# Define the structure of the empty DataFrame
empty_df = pd.DataFrame(columns=["Expense ID", "Description", "Category", "Amount"])
empty_fig = Image.new('RGB',(2,2))

# Gradio Interface
with gr.Blocks() as demo:
    # Add custom CSS for buttons with !important to override default styles
    gr.HTML("""
    <style>
        .custom-button {
            background-color: #ff9800 !important; /* Orange color */
            color: white !important; /* White text */
            border: none !important;
            padding: 10px 20px !important;
            text-align: center !important;
            font-size: 14px !important;
            border-radius: 5px !important;
            cursor: pointer !important;
        }
        .custom-button:hover {
            background-color: #e68900 !important; /* Slightly darker orange for hover */
        }
    </style>
    """)
    gr.HTML("""
    <div style="text-align: center; font-size: 24px; font-weight: bold; margin-bottom: 20px;">
        Expense Management Assistant
    </div>
    """)
    
    # Input Section: Upload Images
    with gr.Row():
        with gr.Column():
            gr.Markdown("### Upload Bill Images")
            image_input = gr.File(file_types=["image"], file_count="multiple", label="Upload Bill Images")
            process_button = gr.Button("Process Bills" , elem_classes="custom-button")
    
    # Output Section: Display Expense Reports
    with gr.Row():
        with gr.Column():
            expense_table = gr.DataFrame(label="Categorized Expenses", visible=True, value = empty_df)
            download_csv_button = gr.File(label="Download Categorized Report", visible=False)
            expense_chart = gr.Image(label="Expense Chart", visible=False, value = empty_fig)
            download_chart_button = gr.File(label="Download Expense Chart", visible=False)

    # Chat Section: User Query
    with gr.Row():
        with gr.Column():
            gr.Markdown("### Chat with Expense Manager")
            chat_input = gr.Textbox(label="Enter your query")
            chat_output = gr.Textbox(label="Response")
            chat_button = gr.Button("Ask",  elem_classes="custom-button")

    # State for maintaining the ExpenseManager
    state = gr.State(value=None)

    # Processing Bills
    process_button.click(
        fn=process_expenses,
        inputs=[image_input, state],
        outputs=[
            expense_table,          # Update DataFrame
            download_csv_button,    # Update CSV download
            expense_chart,          # Update chart image
            download_chart_button,

            expense_table,  # Toggle DataFrame visibility
            download_csv_button,  # Toggle CSV visibility
            expense_chart,  # Toggle chart visibility
            download_chart_button,  # Toggle chart download visibility
            state,  # Update state
        ],
        show_progress = True
    )
    

    # Chatting with Manager
    chat_button.click(
        fn=chat_with_manager,
        inputs=[chat_input, state],
        outputs=[chat_output]
    )

# Launch the app
if __name__ == "__main__":
    load_dotenv("env/.env")
    demo.launch(debug=True)