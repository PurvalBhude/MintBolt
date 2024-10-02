import os
import requests
import pandas as pd
import json
from flask import Flask, request, jsonify
from statsmodels.tsa.arima.model import ARIMA
import google.generativeai as genai
import seaborn as sns
import matplotlib.pyplot as plt
import io
import base64

# Set up the Google API key
os.environ['GOOGLE_API_KEY'] = "AIzaSyDzm-8Pse0TLpDbtYIFCWJj1q7QK7IhBVE"
genai.configure(api_key=os.environ['GOOGLE_API_KEY'])

app = Flask(__name__)

# Load the invoice data
file_path = 'invoice_database.csv'
df = pd.read_csv(file_path)
df['date'] = pd.to_datetime(df['date'], dayfirst=True)

@app.route('/api/expenses_by_type', methods=['POST'])
def expenses_by_type():
    data = request.get_json()
    
    if 'employee_id' not in data:
        return jsonify({"error": "Missing employee_id"}), 400

    employee_id = data['employee_id']
    employee_data = df[df['employee_id'] == employee_id]

    if employee_data.empty:
        return jsonify({"error": f"No data found for employee {employee_id}"}), 400

    total_by_type = employee_data.groupby('type')['amount'].sum().reset_index()
    total_by_type.columns = ['Expense Type', 'Total Amount']
    
    return jsonify(total_by_type.to_dict(orient='records')), 200

@app.route('/api/expenses_by_vendor', methods=['POST'])
def expenses_by_vendor():
    data = request.get_json()
    
    if 'employee_id' not in data:
        return jsonify({"error": "Missing employee_id"}), 400

    employee_id = data['employee_id']
    employee_data = df[df['employee_id'] == employee_id]

    if employee_data.empty:
        return jsonify({"error": f"No data found for employee {employee_id}"}), 400

    total_by_vendor = employee_data.groupby('vendor')['amount'].sum().reset_index()
    total_by_vendor.columns = ['Vendor', 'Total Amount']
    
    return jsonify(total_by_vendor.to_dict(orient='records')), 200

@app.route('/api/expenses_by_location', methods=['POST'])
def expenses_by_location():
    data = request.get_json()
    
    if 'employee_id' not in data:
        return jsonify({"error": "Missing employee_id"}), 400

    employee_id = data['employee_id']
    employee_data = df[df['employee_id'] == employee_id]

    if employee_data.empty:
        return jsonify({"error": f"No data found for employee {employee_id}"}), 400

    total_by_location = employee_data.groupby('location')['amount'].sum().reset_index()
    total_by_location.columns = ['Location', 'Total Amount']
    
    return jsonify(total_by_location.to_dict(orient='records')), 200

# Function to call the APIs and summarize the expenses
def fetch_expenses_summary(employee_id):
    # Call the expenses by type API
    response_type = requests.post(f"http://localhost:5000/api/expenses_by_type", json={"employee_id": employee_id})
    if response_type.status_code != 200:
        print(f"Error fetching expenses by type: {response_type.json()}")
        return None

    # Call the expenses by vendor API
    response_vendor = requests.post(f"http://localhost:5000/api/expenses_by_vendor", json={"employee_id": employee_id})
    if response_vendor.status_code != 200:
        print(f"Error fetching expenses by vendor: {response_vendor.json()}")
        return None

    # Call the expenses by location API
    response_location = requests.post(f"http://localhost:5000/api/expenses_by_location", json={"employee_id": employee_id})
    if response_location.status_code != 200:
        print(f"Error fetching expenses by location: {response_location.json()}")
        return None

    # Summarize the responses
    summary = {
        "by_type": response_type.json(),
        "by_vendor": response_vendor.json(),
        "by_location": response_location.json()
    }

    return summary

@app.route('/get_expenses_summary', methods=['POST'])
def get_expenses_summary_route():
    data = request.get_json()

    if 'employee_id' not in data:
        return jsonify({"error": "Missing employee_id"}), 400

    employee_id = data['employee_id']

    # Generate the summary
    summary = fetch_expenses_summary(employee_id)
    if summary is None:
        return jsonify({"error": f"No data found for employee {employee_id}"}), 404

    # Use the Gemini model to generate the response
    model = genai.GenerativeModel('gemini-pro')
    prompt = (
        "I have the following expense data for employee ID {employee_id}:\n\n"
        "Expenses by Type:\n{by_type}\n\n"
        "Expenses by Vendor:\n{by_vendor}\n\n"
        "Expenses by Location:\n{by_location}\n\n"
        "Please summarize this data in a clear and concise manner. "
        "Highlight the key points, total amounts, and any notable trends or insights. "
        "Make the summary easy to understand for someone who is not familiar with the data."
    ).format(employee_id=employee_id,
             by_type=json.dumps(summary['by_type'], indent=4),
             by_vendor=json.dumps(summary['by_vendor'], indent=4),
             by_location=json.dumps(summary['by_location'], indent=4))

    response = model.generate_content(prompt)

    # Assuming 'response' has an attribute that contains the generated text
    summary_text = response.text  # Adjust based on actual response structure

    return jsonify({"summary": summary_text}), 200

file_path = 'invoice_database.csv'
df = pd.read_csv(file_path)
df['date'] = pd.to_datetime(df['date'], dayfirst=True)

def create_barplot(employee_data):
    plt.figure(figsize=(12, 6))
    sns.barplot(data=employee_data, x='type', y='amount', estimator=sum, ci=None, palette='viridis')
    plt.title('Total Expenses by Category')
    plt.ylabel('Total Amount')
    plt.xticks(rotation=45)

    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close()
    return base64.b64encode(img.getvalue()).decode()

def create_piechart(employee_data):
    top_vendors = employee_data.groupby('vendor')['amount'].sum().nlargest(10)
    plt.figure(figsize=(8, 8))
    plt.pie(top_vendors, labels=top_vendors.index, autopct='%1.1f%%', startangle=140, colors=sns.color_palette("viridis", len(top_vendors)))
    plt.title('Top 10 Vendor Expense Distribution')
    plt.axis('equal')

    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close()
    return base64.b64encode(img.getvalue()).decode()

def create_heatmap(employee_data):
    category_location = employee_data.groupby(['type', 'location'])['amount'].sum().unstack().fillna(0)
    plt.figure(figsize=(12, 8))
    sns.heatmap(category_location, annot=True, fmt=".1f", cmap="YlGnBu", cbar_kws={'label': 'Amount Spent'})
    plt.title('Expenses by Category and Location')
    plt.ylabel('Category')
    plt.xlabel('Location')

    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close()
    return base64.b64encode(img.getvalue()).decode()

@app.route('/api/barplot', methods=['POST'])
def barplot_api():
    data = request.get_json()
    
    if 'employee_id' not in data:
        return jsonify({"error": "Missing employee_id"}), 400

    employee_id = data['employee_id']
    employee_data = df[df['employee_id'] == employee_id]

    if employee_data.empty:
        return jsonify({"error": f"No data found for employee {employee_id}"}), 400

    plot_url = create_barplot(employee_data)
    return jsonify({
        "employee_id": employee_id,
        "plot_url": plot_url
    }), 200

@app.route('/api/piechart', methods=['POST'])
def piechart_api():
    data = request.get_json()
    
    if 'employee_id' not in data:
        return jsonify({"error": "Missing employee_id"}), 400

    employee_id = data['employee_id']
    employee_data = df[df['employee_id'] == employee_id]

    if employee_data.empty:
        return jsonify({"error": f"No data found for employee {employee_id}"}), 400

    plot_url = create_piechart(employee_data)
    return jsonify({
        "employee_id": employee_id,
        "plot_url": plot_url
    }), 200

@app.route('/api/heatmap', methods=['POST'])
def heatmap_api():
    data = request.get_json()
    
    if 'employee_id' not in data:
        return jsonify({"error": "Missing employee_id"}), 400

    employee_id = data['employee_id']
    employee_data = df[df['employee_id'] == employee_id]

    if employee_data.empty:
        return jsonify({"error": f"No data found for employee {employee_id}"}), 400

    plot_url = create_heatmap(employee_data)
    return jsonify({
        "employee_id": employee_id,
        "plot_url": plot_url
    }), 200

file_path = 'invoice_database.csv'
df = pd.read_csv(file_path)
df['date'] = pd.to_datetime(df['date'], dayfirst=True)


def fit_arima_for_employee_monthly(employee_id, df):
    employee_data = df[df['employee_id'] == int(employee_id)]

    if employee_data.empty:
        return None, f"No data found for employee {employee_id}"

    employee_expenses = employee_data.groupby('date')['amount'].sum().reset_index()

    if employee_expenses.empty or len(employee_expenses) < 2:
        return None, f"Not enough data to build a model for employee {employee_id}"

    employee_expenses.set_index('date', inplace=True)
    employee_expenses = employee_expenses.resample('MS').sum()

    if employee_expenses.shape[0] < 2:
        return None, f"Not enough data points to build an ARIMA model for employee {employee_id}"

    try:
        model = ARIMA(employee_expenses['amount'], order=(1, 1, 1))
        model_fit = model.fit()
    except ValueError as e:
        return None, f"Error fitting ARIMA model: {str(e)}"

    forecast_steps = 6
    forecast = model_fit.get_forecast(steps=forecast_steps)
    forecast_index = pd.date_range(start=employee_expenses.index[-1], periods=forecast_steps + 1, freq='MS')[1:]
    forecast_series = pd.Series(forecast.predicted_mean, index=forecast_index)

    fig, ax = plt.subplots(figsize=(14, 8))
    ax.plot(employee_expenses, label=f'Historical Monthly Expenses (Employee {employee_id})', color='blue')
    ax.plot(forecast_series, label=f'Future Monthly Predictions (Employee {employee_id})', color='orange', linestyle='--')
    ax.set_title(f'Historical and Future Monthly Expenses for Employee {employee_id}')
    ax.set_xlabel('Date')
    ax.set_ylabel('Amount')
    ax.legend()

    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close()

    plot_url = base64.b64encode(img.getvalue()).decode()

    return plot_url, None


def predict_spending(employee_id, month_str, year_str):
    try:
        month_number = pd.to_datetime(month_str, format='%B', errors='coerce').month
    except Exception as e:
        return None, "Invalid month name."

    query_date = pd.to_datetime(f"{year_str}-{month_number}-01")

    employee_data = df[df['employee_id'] == employee_id]

    if employee_data.empty:
        return None, f"No data found for employee {employee_id}."

    monthly_data = employee_data.resample('M', on='date').sum()

    try:
        model = ARIMA(monthly_data['amount'], order=(1, 1, 1))
        model_fit = model.fit()
    except ValueError as e:
        return None, f"Error fitting ARIMA model: {str(e)}"

    forecast = model_fit.forecast(steps=1)
    return forecast[0], None


def predict_total_expenses(employee_id, year_str):
    start_date = pd.to_datetime(f"{year_str}-01-01")
    end_date = pd.to_datetime(f"{year_str}-12-31")

    employee_data = df[(df['employee_id'] == employee_id) & (df['date'] >= start_date) & (df['date'] <= end_date)]

    if employee_data.empty:
        return None, f"No data found for employee {employee_id} in the year {year_str}."

    monthly_data = employee_data.resample('M', on='date').sum()

    if len(monthly_data) < 2:
        return None, f"Not enough data to build a model for employee {employee_id} in the year {year_str}."

    try:
        model = ARIMA(monthly_data['amount'], order=(1, 1, 1))
        model_fit = model.fit()
    except ValueError as e:
        return None, f"Error fitting ARIMA model: {str(e)}"

    forecast = model_fit.forecast(steps=12)
    total_forecast = forecast.sum()

    return total_forecast, None


def predict_category_expenses(employee_id, category, month_str, year_str):
    start_date = pd.to_datetime(f"{year_str}-{month_str}-01")
    end_date = start_date + pd.offsets.MonthEnd(1)

    employee_data = df[(df['employee_id'] == employee_id) &
                       (df['type'] == category) &
                       (df['date'] >= start_date) &
                       (df['date'] <= end_date)]

    if employee_data.empty:
        return None, f"No data found for employee {employee_id} on {category} in {month_str} {year_str}."

    daily_data = employee_data.resample('D', on='date').sum()

    try:
        model = ARIMA(daily_data['amount'], order=(1, 1, 1))
        model_fit = model.fit()
    except ValueError as e:
        return None, f"Error fitting ARIMA model: {str(e)}"

    forecast = model_fit.forecast(steps=30)
    total_forecast = forecast.sum()

    return total_forecast, None


@app.route('/api/ARIMA', methods=['POST'])
def employee_expenses():
    data = request.get_json()

    if 'employee_id' not in data:
        return jsonify({"error": "Missing employee_id"}), 400

    employee_id = data['employee_id']
    plot_url, error_message = fit_arima_for_employee_monthly(employee_id, df)

    if error_message:
        return jsonify({"error": error_message}), 400

    return jsonify({
        "employee_id": employee_id,
        "plot_url": plot_url
    }), 200


@app.route('/api/Monthly_Spending', methods=['POST'])
def predict_employee_spending():
    data = request.get_json()

    if 'employee_id' not in data or 'month_str' not in data or 'year_str' not in data:
        return jsonify({"error": "Missing parameters"}), 400

    employee_id = data['employee_id']
    month_str = data['month_str']
    year_str = data['year_str']

    prediction, error_message = predict_spending(employee_id, month_str, year_str)

    if error_message:
        return jsonify({"error": error_message}), 400

    return jsonify({
        "employee_id": employee_id,
        "month": month_str,
        "year": year_str,
        "predicted_spending": prediction
    }), 200


@app.route('/api/Yearly_Spending', methods=['POST'])
def predict_employee_total_expenses():
    data = request.get_json()

    if 'employee_id' not in data or 'year_str' not in data:
        return jsonify({"error": "Missing parameters"}), 400

    employee_id = data['employee_id']
    year_str = data['year_str']

    prediction, error_message = predict_total_expenses(employee_id, year_str)

    if error_message:
        return jsonify({"error": error_message}), 400

    return jsonify({
        "employee_id": employee_id,
        "year": year_str,
        "predicted_total_expenses": prediction
    }), 200


@app.route('/api/Category_Spending', methods=['POST'])
def predict_employee_category_expenses():
    data = request.get_json()

    if 'employee_id' not in data or 'category' not in data or 'month_str' not in data or 'year_str' not in data:
        return jsonify({"error": "Missing parameters"}), 400

    employee_id = data['employee_id']
    category = data['category']
    month_str = data['month_str']
    year_str = data['year_str']

    prediction, error_message = predict_category_expenses(employee_id, category, month_str, year_str)

    if error_message:
        return jsonify({"error": error_message}), 400

    return jsonify({
        "employee_id": employee_id,
        "category": category,
        "month": month_str,
        "year": year_str,
        "predicted_category_expenses": prediction
    }), 200


if __name__ == "__main__":
    app.run(host='0.0.0.0')
