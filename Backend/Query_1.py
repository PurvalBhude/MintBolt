from flask import Flask, request, jsonify
import re
import joblib
from typing import Dict, Any
from transformers import pipeline

app = Flask(__name__)

# Global variable to store the most recent summary
current_summary = ""

# Load the pre-trained model and vectorizer
model = joblib.load('model/model.pkl')
vectorizer = joblib.load('model/vectorizer.pkl')

# Load the question-answering pipeline
qa_pipeline = pipeline("question-answering")

def preprocess_ocr_numbers(json_data):
    # Function to correct common OCR errors in numbers
    for block in json_data['textBlocks']:
        text = block['blockText']
        numbers_with_o = re.findall(r'\d+O\d*|\d*O\d+', text)
        for num in numbers_with_o:
            corrected_num = num.replace('O', '0')
            text = text.replace(num, corrected_num)
        block['blockText'] = text
        
        for line in block['lines']:
            text = line['lineText']
            numbers_with_o = re.findall(r'\d+O\d*|\d*O\d+', text)
            for num in numbers_with_o:
                corrected_num = num.replace('O', '0')
                text = text.replace(num, corrected_num)
            line['lineText'] = text
    
    return json_data

def extract_invoice_details(json_data):
    json_data = preprocess_ocr_numbers(json_data)
    extracted_text = "\n".join([block['blockText'] for block in json_data['textBlocks']])

    # Extract various fields using patterns
    name_pattern = r'Issued to:\s*(.*)'
    name_match = re.search(name_pattern, extracted_text)
    name = name_match.group(1).strip() if name_match else 'Not Found'

    vendor_pattern = r'vendor\s*:\s*(.*)'
    vendor_match = re.search(vendor_pattern, extracted_text)
    vendor = vendor_match.group(1).strip() if vendor_match else 'Not Found'

    emp_id_pattern = r'Employee ld:\s*(\d+)'
    employee_id_match = re.search(emp_id_pattern, extracted_text)
    employee_id = employee_id_match.group(1) if employee_id_match else 'Not Found'

    date_pattern = r'Date Issued:\s*(\d{1,2}-\d{1,2}-\d{4})'
    date_match = re.search(date_pattern, extracted_text)
    date = date_match.group(1) if date_match else 'Not Found'

    # Total Amount Extraction
    total_amount = 'Not Found'
    grand_total_index = -1
    
    for i, block in enumerate(json_data['textBlocks']):
        if 'GRAND TOTAL' in block['blockText']:
            grand_total_index = i
            break
    
    if grand_total_index != -1:
        potential_totals = []
        for i in range(grand_total_index + 1, len(json_data['textBlocks'])):
            block_text = json_data['textBlocks'][i]['blockText']
            cleaned_number = re.sub(r'[^\d]', '', block_text)
            if cleaned_number.isdigit():
                potential_totals.append(int(cleaned_number))
        
        if potential_totals:
            total_amount = str(max(potential_totals))

    invoice_id_pattern = r'(\d{6})'
    invoice_id_match = re.search(invoice_id_pattern, extracted_text)
    invoice_id = invoice_id_match.group(1) if invoice_id_match else 'Not Found'

    location_pattern = r'Address:\s*(.*)'
    location_match = re.search(location_pattern, extracted_text)
    location = location_match.group(1).strip() if location_match else 'Not Found'

    # Category mapping
    category_mapping = {
        'Food': ['chole', 'bhature', 'pizza', 'coffee', 'restaurant', 'meal', 'food'],
        'Transport': ['taxi', 'flight', 'transportation', 'bus', 'train', 'travel'],
        'Medicine': ['medical', 'hospital', 'clinic', 'medicine', 'doctor'],
        'Electronics': ['phone', 'laptop', 'electronics', 'device', 'gadget', 'Macbook Air'],
        'Miscellaneous': ['service', 'miscellaneous', 'other', 'misc']
    }

    expense_category = 'Miscellaneous'
    for block in json_data['textBlocks']:
        for category, keywords in category_mapping.items():
            if any(keyword.lower() in block['blockText'].lower() for keyword in keywords):
                expense_category = category
                break

    return {
        'Vendor': vendor,
        'Client Name': name,
        'Employee Id': employee_id,
        'Date Issued': date,
        'Invoice ID': invoice_id,
        'Total Amount': '₹' + total_amount if total_amount != 'Not Found' else 'Not Found',
        'Location': location,
        'Expense Category': expense_category
    
    }

def generate_summary(invoice_details: Dict[str, Any]) -> str:
    # Same summary generation logic
    global current_summary
    summary = f"""
    This invoice was issued by {invoice_details['Vendor']} to {invoice_details['Client Name']} 
    (Employee ID: {invoice_details['Employee Id']}) on {invoice_details['Date Issued']}. 
    The invoice, identified by ID {invoice_details['Invoice ID']}, is for a total amount of 
    {invoice_details['Total Amount']}. The transaction took place at {invoice_details['Location']} 
    and falls under the {invoice_details['Expense Category']} category.
    """
    current_summary = summary.strip()
    return current_summary

def classify_text(text_blocks):
    """Classify the text as either an Invoice or Contract"""
    full_text = " ".join([block['blockText'] for block in text_blocks])
    transformed_text = vectorizer.transform([full_text])
    prediction = model.predict(transformed_text)
    return prediction[0]

def ask_general_question(text, question):
    # Function to answer questions using the transformers pipeline
    result = qa_pipeline(question=question, context=text)
    return result['answer']

# API Endpoints
@app.route('/entity_recognition', methods=['POST'])
def entity_recognition():
    try:
        json_data = request.get_json()
        extracted_data = extract_invoice_details(json_data)
        return jsonify(extracted_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/summarize', methods=['POST'])
def summarize():
    try:
        global current_summary
        json_data = request.get_json()
        extracted_data = extract_invoice_details(json_data)
        summary = generate_summary(extracted_data)
        return jsonify({'summary': summary})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/classify', methods=['POST'])
def classify():
    """API endpoint for document classification"""
    try:
        data = request.get_json()
        if 'textBlocks' not in data:
            return jsonify({'error': 'Invalid input, expected "textBlocks" field in JSON.'}), 400
        
        classification = classify_text(data['textBlocks'])
        return jsonify({
            'classification': classification
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/query', methods=['POST'])
def query():
    """API endpoint for question answering"""
    try:
        data = request.get_json()
        if 'question' not in data:
            return jsonify({'error': 'Missing required field: question'}), 400
        
        # Use the global summary for answering the question
        if current_summary == "":
            return jsonify({'error': 'Please generate a summary first.'}), 400
        
        question = data['question']
        answer = ask_general_question(current_summary, question)
        
        return jsonify({
            'question': question,
            'answer': answer
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001, host='0.0.0.0')
