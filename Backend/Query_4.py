import google.generativeai as genai
import os
import pandas as pd
from flask import Flask, request, jsonify

# Initialize Flask App
app = Flask(__name__)

# Configure Google Gemini API
os.environ['GOOGLE_API_KEY'] = "AIzaSyDzm-8Pse0TLpDbtYIFCWJj1q7QK7IhBVE"
genai.configure(
    api_key=os.environ['GOOGLE_API_KEY']
)

# Use correct model loading function
model = genai.GenerativeModel('gemini-pro')

# File path for the Excel file containing employee data
xlsx_file = "Employee.xlsx"
csv_file = "invoice_database.csv"

def get_employee_invoice_data(employee_id, csv_file):
    try:
        # Read the CSV file
        df = pd.read_csv(csv_file)

        # Filter the data for the specific employee_id
        employee_data = df[df['employee_id'] == employee_id]

        # Check if data exists for the employee
        if employee_data.empty:
            return f"No invoices found for employee ID: {employee_id}"

        # Convert the filtered data into a readable text format
        invoice_data_text = ""
        for _, row in employee_data.iterrows():
            invoice_data_text += f"Invoice ID: {row['invoice_id']}\n" \
                                 f"Amount: {row['amount']}\n" \
                                 f"Date: {row['date']}\n" \
                                 f"Location: {row['location']}\n" \
                                 f"Type: {row['type']}\n" \
                                 f"Vendor: {row['vendor']}\n" \
                                 f"--------------------------\n"

        return invoice_data_text

    except Exception as e:
        return f"Error: {str(e)}"

# Function to filter and format employee data
def filter_employee_data(employee_id, xlsx_file):
    # Read the Excel file and filter by employee ID
    df = pd.read_excel(xlsx_file)
    filtered_data = df[df['employee_id'] == employee_id]

    # Check if the employee exists
    if filtered_data.empty:
        return None

    # Convert the filtered data to a dictionary for better format handling
    employee_data = filtered_data.to_dict(orient='records')[0]

    # Format the employee data as human-readable text for the model to understand better
    employee_data_text = f"Employee ID: {employee_data['employee_id']}\n" \
                         f"Name: {employee_data['name']}\n" \
                         f"Phone Number: {employee_data['phone_no']}\n" \
                         f"Date of Birth: {employee_data['dob']}\n" \
                         f"Sex: {employee_data['sex']}\n" \
                         f"Department: {employee_data['department']}\n" \
                         f"Role: {employee_data['role']}\n" \
                         f"Balance Money: {employee_data['balance_money']}\n" \
                         f"CTC: {employee_data['ctc']}\n" \
                         f"Base Package: {employee_data['base_package']}\n" \
                         f"Food Allowance: {employee_data['food_allowance']}\n" \
                         f"Transport Allowance: {employee_data['transport_allowance']}\n" \
                         f"Medical Allowance: {employee_data['medical_allowance']}\n" \
                         f"Electronics Allowance: {employee_data['electronics_allowance']}\n" \
                         f"Miscellaneous Allowance: {employee_data['misc_allowance']}\n" \
                         f"Debt Budget: {employee_data['debt_budget']}\n" \
                         f"Monthly EMI: {employee_data['monthly_emi']}\n"

    return employee_data_text

# Function to generate the prompt and request Gemini to generate a response
def generate_response(employee_id, user_input, xlsx_file):
    # Get the employee data in text format
    employee_data_text = filter_employee_data(employee_id, xlsx_file)
    employee_invoice_data = get_employee_invoice_data(employee_id, csv_file)

    # If employee data is not found, return None
    if not employee_data_text:
        return "Employee data not found."

    # Create the prompt
    prompt = f"This is the my data in employee data in the database:\n{employee_data_text}\n\n the following data is my data in invoice database: \n{employee_invoice_data}\n\n\n" \
             f"Based on the above data, answer the following question:\n{user_input}.\nGive the response in atleast 1-2 lines."

    # Use the Gemini model to generate a response based on the prompt
    response = model.generate_content(prompt)  # Corrected method and argument

    return response.text  # Get the generated text

# Define the route for the chatbot interaction
@app.route('/chat', methods=['POST'])
def chat():
    try:
        # Get the JSON data from the request
        data = request.get_json()
        employee_id = data.get('employee_id')
        user_input = data.get('user_input')

        # Check if the required data is provided
        if not employee_id or not user_input:
            return jsonify({"error": "Employee ID or User Input not provided"}), 400

        # Generate a response using the employee data and the Gemini model
        gemini_response = generate_response(employee_id, user_input, xlsx_file)

        # Return the response as JSON
        return jsonify({"response": gemini_response}), 200

    except Exception as e:
        # Handle any exceptions and return error message
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=8080)
