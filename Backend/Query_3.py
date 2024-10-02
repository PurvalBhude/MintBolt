from flask import Flask, request, jsonify
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use a non-interactive backend for generating charts
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)

# Load employee data
df = pd.read_excel('Employee.xlsx')

@app.route('/net_worth', methods=['POST'])
def get_net_worth():
    try:
        # Get JSON data from request
        data = request.get_json()
        employee_id = data.get('emp_id')

        # Check if employee_id is provided
        if not employee_id:
            return jsonify({"error": "Employee ID not provided"}), 400

        # Filter for employee with the provided emp_id
        employee_data = df[df['emp_id'] == employee_id]

        # Check if employee data exists
        if employee_data.empty:
            return jsonify({"error": "Employee not found"}), 404
        
        employee_data = employee_data.iloc[0]  # Get the first (and should be only) row
        
        # Extract relevant data
        base_salary = int(employee_data['base_package'])
        food_allowance = int(employee_data['food_allowance'])
        transport_allowance = int(employee_data['transport_allowance'])
        medical_allowance = int(employee_data['medical_allowance'])
        electronics_allowance = int(employee_data['electronics_allowance'])
        misc_allowance = int(employee_data['misc_allowance'])
        monthly_emi = int(employee_data['monthly_emi'])
        debt_budget = int(employee_data['debt_budget'])

        # Calculate total assets and liabilities
        total_assets = base_salary + food_allowance + transport_allowance + \
                       medical_allowance + electronics_allowance + \
                       misc_allowance
        total_liabilities = monthly_emi + debt_budget

        # Calculate net worth
        net_worth = total_assets - total_liabilities

        # Prepare response data
        response_data = {
            "employee_id": employee_id,
            "total_assets": total_assets,
            "total_liabilities": total_liabilities,
            "net_worth": net_worth
        }

        return jsonify(response_data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/employee', methods=['POST'])
def get_employee_details():
    try:
        # Get JSON data from request
        data = request.get_json()
        employee_id = data.get('emp_id')

        # Check if employee_id is provided
        if not employee_id:
            return jsonify({"error": "Employee ID not provided"}), 400

        # Filter for employee with the provided emp_id
        employee_data = df[df['emp_id'] == employee_id]

        # Check if employee data exists
        if employee_data.empty:
            return jsonify({"error": "Employee not found"}), 404
        
        employee_data = employee_data.iloc[0]  # Get the first (and should be only) row
        
        # Extract relevant data and convert to standard Python types
        ctc = int(employee_data['ctc'])
        base_salary = int(employee_data['base_package'])
        food_allowance = int(employee_data['food_allowance'])
        transport_allowance = int(employee_data['transport_allowance'])
        medical_allowance = int(employee_data['medical_allowance'])
        electronics_allowance = int(employee_data['electronics_allowance'])
        misc_allowance = int(employee_data['misc_allowance'])
        monthly_emi = int(employee_data['monthly_emi'])

        # Calculate total allowances
        total_allowances = (food_allowance + transport_allowance + 
                            medical_allowance + electronics_allowance + 
                            misc_allowance)

        # Prepare response data
        response_data = {
            "employee_id": employee_id,
            "total_ctc": ctc,
            "base_salary": base_salary,
            "food_allowance": food_allowance,
            "transport_allowance": transport_allowance,
            "medical_allowance": medical_allowance,
            "electronics_allowance": electronics_allowance,
            "miscellaneous_allowance": misc_allowance,
            "monthly_emi": monthly_emi,
            "remaining_balance": base_salary - (total_allowances + monthly_emi)
        }

        return jsonify(response_data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/ctc_chart', methods=['POST'])
def get_ctc_chart():
    try:
        # Get JSON data from request
        data = request.get_json()
        employee_id = data.get('emp_id')

        # Check if employee_id is provided
        if not employee_id:
            return jsonify({"error": "Employee ID not provided"}), 400

        # Filter for employee with the provided emp_id
        employee_data = df[df['emp_id'] == employee_id]

        # Check if employee data exists
        if employee_data.empty:
            return jsonify({"error": "Employee not found"}), 404
        
        employee_data = employee_data.iloc[0]  # Get the first (and should be only) row

        # Extract relevant data for employee and convert to standard Python types
        ctc = int(employee_data['ctc'])
        base_salary = int(employee_data['base_package'])
        food_allowance = int(employee_data['food_allowance'])
        transport_allowance = int(employee_data['transport_allowance'])
        medical_allowance = int(employee_data['medical_allowance'])
        electronics_allowance = int(employee_data['electronics_allowance'])
        misc_allowance = int(employee_data['misc_allowance'])
        monthly_emi = int(employee_data['monthly_emi'])

        # Data for the pie chart of CTC breakdown
        labels = ['Base Salary', 'Food Allowance', 'Transport Allowance', 
                  'Medical Allowance', 'Electronics Allowance', 
                  'Miscellaneous Allowance', 'Monthly EMI']
        values = [base_salary, food_allowance, transport_allowance, 
                  medical_allowance, electronics_allowance, 
                  misc_allowance, monthly_emi]

        # Create pie chart in memory
        plt.figure(figsize=(10, 8))
        plt.pie(values, startangle=90, 
                colors=['#66b3ff', '#ff9999', '#99ff99', 
                        '#ffcc99', '#c2c2f0', '#ffb3e6', 
                        '#ff6666'],
                explode=[0.1] * len(labels)
                )  # Adding labels directly to the pie chart

        # Add legend outside the chart
        plt.legend(labels, loc='upper left', bbox_to_anchor=(1, 1), fontsize='large')

        plt.axis('equal')  # Equal aspect ratio ensures the pie is drawn as a circle.

        # Save the pie chart to a BytesIO object
        buf = io.BytesIO()
        plt.tight_layout()  # Adjust layout
        plt.savefig(buf, format='png')
        plt.close()  # Close the plot to free memory
        buf.seek(0)

        # Encode the image to base64
        image_base64 = base64.b64encode(buf.read()).decode('utf-8')

        # Return the Base64 image in JSON format
        return jsonify({"employee_id": employee_id, "ctc_chart": image_base64}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=8000)