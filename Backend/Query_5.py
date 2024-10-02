import pandas as pd
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
import matplotlib.pyplot as plt
import matplotlib.table as tbl
import io
import base64
import re

app = Flask(__name__)

# Function to get invoices for the last month
def get_invoices_for_last_month(employee_id):
    # Load the invoice data
    df = pd.read_csv('invoice_database.csv')

    # Convert the 'date' column to datetime format
    df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y')

    # Get the current date and calculate the first and last day of last month
    today = datetime.now()
    first_day_last_month = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
    last_day_last_month = today.replace(day=1) - timedelta(days=1)

    # Filter the DataFrame for the specified employee_id and date range
    filtered_invoices = df[
        (df['employee_id'] == employee_id) &
        (df['date'] >= first_day_last_month) &
        (df['date'] <= last_day_last_month)
    ]

    # Format the 'date' column to remove time
    if not filtered_invoices.empty:
        filtered_invoices['date'] = filtered_invoices['date'].dt.date  # Keep only the date part

    return filtered_invoices

# API to plot invoices table
@app.route('/invoices', methods=['POST'])
def plot_invoices_table():
    # Get JSON data from request
    data = request.get_json()
    employee_id = data.get('emp_id')

    # Get invoices for the specified employee_id
    invoices = get_invoices_for_last_month(employee_id)

    # Check if there are invoices for the employee in the last month
    if invoices.empty:
        return jsonify({"error": f"No invoices found for employee ID {employee_id} in the last month."}), 404

    # Create a figure and a set of subplots
    fig, ax = plt.subplots(figsize=(10, 5))  # Adjust the size as needed
    ax.axis('tight')
    ax.axis('off')

    # Add title and employee ID
    title = f'Transaction List for Employee ID: {employee_id}'
    plt.title(title, fontsize=16, fontweight='bold')

    # Create the table
    table_data = invoices[['invoice_id', 'amount', 'date', 'location', 'type', 'vendor']].values
    columns = ['Invoice ID', 'Amount', 'Date', 'Location', 'Type', 'Vendor']
    
    table = tbl.table(ax, cellText=table_data, colLabels=columns, cellLoc='center', loc='center')

    # Adjust the layout
    table.auto_set_font_size(False)
    table.set_fontsize(12)
    table.scale(1.2, 1.2)  # Scale the table for better visibility

    # Save the plot to a BytesIO object
    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight', dpi=300)
    plt.close()
    img.seek(0)

    # Encode the image to base64
    img_base64 = base64.b64encode(img.getvalue()).decode('utf-8')

    # Return the image in base64 format
    return jsonify({"image": f"data:image/png;base64,{img_base64}"}), 200

# Function to manage debt for an employee
def manage_debt(emp_id, debt_amount):
    # Load employee data
    df = pd.read_excel('Employee.xlsx')

    # Check if employee exists
    employee = df[df['emp_id'] == emp_id]
    if employee.empty:
        return {"error": "Employee ID not found."}

    # Get current values and convert to native Python types
    current_debt_budget = int(employee['debt_budget'].values[0])
    current_monthly_emi = float(employee['monthly_emi'].values[0])

    # Check if debt can be taken
    if debt_amount > current_debt_budget:
        return {"error": "Insufficient debt budget."}

    # Store old values for the summary
    old_debt_budget = current_debt_budget
    old_monthly_emi = current_monthly_emi

    # Update debt budget
    new_debt_budget = current_debt_budget - debt_amount

    # Calculate new EMI
    new_monthly_emi = (current_monthly_emi * 12 + debt_amount) / 12

    # Update DataFrame
    df.loc[df['emp_id'] == emp_id, 'debt_budget'] = new_debt_budget
    df.loc[df['emp_id'] == emp_id, 'monthly_emi'] = new_monthly_emi

    # Save the updated data back to Excel
    df.to_excel('Employee.xlsx', index=False)

    # Prepare final changes string
    changes = {
        "Debt taken": debt_amount,
        "Old Debt Budget": old_debt_budget,
        "New Debt Budget": new_debt_budget,
        "Old Monthly EMI": round(old_monthly_emi, 2),
        "New Monthly EMI": round(new_monthly_emi, 2)
    }
    
    return changes

# API to manage debt
@app.route('/manage_debt', methods=['POST'])
def debt_management():
    data = request.json
    emp_id = data.get('emp_id')
    debt_amount = data.get('debt_amount')

    if emp_id is None or debt_amount is None:
        return jsonify({"error": "emp_id and debt_amount are required."}), 400

    result = manage_debt(emp_id, debt_amount)

    if "error" in result:  # Check if the result is an error message
        return jsonify(result), 400

    return jsonify(result), 200

# Function to preprocess OCR text blocks
def preprocess_ocr_numbers(json_data):
    """Preprocess all text blocks to correct common OCR errors in numbers"""
    for block in json_data['textBlocks']:
        # Replace 'O' with '0' when it appears to be part of a number
        text = block['blockText']
        # Find all numbers that contain 'O'
        numbers_with_o = re.findall(r'\d+O\d*|\d*O\d+', text)
        for num in numbers_with_o:
            corrected_num = num.replace('O', '0')
            text = text.replace(num, corrected_num)
        block['blockText'] = text
        
        # Do the same for each line
        for line in block['lines']:
            text = line['lineText']
            numbers_with_o = re.findall(r'\d+O\d*|\d*O\d+', text)
            for num in numbers_with_o:
                corrected_num = num.replace('O', '0')
                text = text.replace(num, corrected_num)
            line['lineText'] = text
    
    return json_data

# Function to extract invoice details from OCR text
def extract_invoice_details(json_data):
    # Preprocess the JSON data to correct OCR errors in numbers
    json_data = preprocess_ocr_numbers(json_data)
    
    extracted_text = "\n".join([block['blockText'] for block in json_data['textBlocks']])

    # Extract the "Issued to" or relevant name
    name_pattern = r'Issued to:\s*(.*)'
    name_match = re.search(name_pattern, extracted_text)
    name = name_match.group(1).strip() if name_match else 'Not Found'

    # Extract the "vendor"
    vendor_pattern = r'vendor\s*:\s*(.*)'
    vendor_match = re.search(vendor_pattern, extracted_text)
    vendor = vendor_match.group(1).strip() if vendor_match else 'Not Found'

    # Extract Employee Id
    emp_id_pattern = r'Employee ld:\s*(\d+)'
    employee_id_match = re.search(emp_id_pattern, extracted_text)
    employee_id = employee_id_match.group(1) if employee_id_match else 'Not Found'

    # Extract Date Issued
    date_pattern = r'Date Issued:\s*(\d{1,2}-\d{1,2}-\d{4})'
    date_match = re.search(date_pattern, extracted_text)
    date = date_match.group(1) if date_match else 'Not Found'

    # Total Amount Extraction
    total_amount = 'Not Found'
    grand_total_index = -1
    
    # First, find the index of the GRAND TOTAL text
    for i, block in enumerate(json_data['textBlocks']):
        if 'GRAND TOTAL' in block['blockText']:
            grand_total_index = i
            break
    
    if grand_total_index != -1:
        # Look at blocks after GRAND TOTAL
        potential_totals = []
        for i in range(grand_total_index + 1, len(json_data['textBlocks'])):
            block_text = json_data['textBlocks'][i]['blockText']
            # Clean up the text and check if it's a number
            cleaned_number = re.sub(r'[^\d]', '', block_text)
            if cleaned_number.isdigit():
                potential_totals.append(int(cleaned_number))
        
        # If we found any numbers after GRAND TOTAL, use the largest one
        if potential_totals:
            total_amount = str(max(potential_totals))

    # Extract Invoice ID (6-digit pattern)
    invoice_id_pattern = r'(\d{6})'
    invoice_id_match = re.search(invoice_id_pattern, extracted_text)
    invoice_id = invoice_id_match.group(1) if invoice_id_match else 'Not Found'

    # Extract location (Address)
    location_pattern = r'Address:\s*(.*)'
    location_match = re.search(location_pattern, extracted_text)
    location = location_match.group(1).strip() if location_match else 'Not Found'

    # Category mapping
    category_mapping = {
        'Food': ['chole', 'bhature', 'pizza', 'coffee', 'restaurant', 'meal', 'food', 'Panner Pizza', 'Choco Lava'],
        'Transport': ['taxi', 'flight', 'transportation', 'bus', 'train', 'travel'],
        'Medicine': ['medical', 'hospital', 'clinic', 'medicine', 'doctor', 'Betnovate-N', 'Avomine'],
        'Electronics': ['phone', 'laptop', 'electronics', 'device', 'gadget', 'Macbook Air M3', 'Iphone 16'],
        'Miscellaneous': ['service', 'miscellaneous', 'other', 'misc']
    }

    # Categorize the overall expense
    expense_category = 'Miscellaneous'
    for block in json_data['textBlocks']:
        for category, keywords in category_mapping.items():
            if any(keyword.lower() in block['blockText'].lower() for keyword in keywords):
                expense_category = category
                break

    # Summarize the extracted information
    summary = {
        'employee_id': employee_id,
        'amount': '₹' + total_amount if total_amount != 'Not Found' else 'Not Found',
        'date': date,
        'location': location,
        'invoice_id': invoice_id,
        'Vendor': vendor,
        'type': expense_category
    }

    return summary

# API to extract invoice details from OCR
@app.route('/extract_invoice', methods=['POST'])
def extract_invoice():
    json_data = request.get_json()
    extracted_data = extract_invoice_details(json_data)
    return jsonify(extracted_data)

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')