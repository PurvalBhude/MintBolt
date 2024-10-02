# MintBolt
![Vada_Pav](https://github.com/user-attachments/assets/58c1b22a-c9a4-42b5-a6d7-7dad47e07f32)

## Overview

This Kotlin application features a chatbot designed to assist users with various financial and document-related tasks. The chatbot leverages local APIs for functionality related to transaction management, document processing, payment and invoicing, budgeting and finance management, and general queries.

## Table of Contents
- [Features](#features)
- [Technologies Used](#technologies-used)
- [API Endpoints](#api-endpoints)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)

## Features

### Transaction Management & Analysis
- **Summarise My Expenses**: Get a summary of your expenses.
- **Analyse Trends & Expenditure Patterns**: Analyze your spending trends and patterns.
- **Expense Tracking**: Track and manage your expenses effectively.
- **Data Export to CSV**: Export your expense data to a CSV file.

### Document Processing & Analysis
- **Named Entity Recognition**: Extract named entities from documents.
- **AI Driven Document Classification**: Classify documents using AI algorithms.
- **Searching & Querying Document Data**: Search through documents and query specific data.
- **Digitise Document (PDF/PNG)**: Convert scanned documents into digital formats.

### Payment & Invoicing
- **Invoice Ingestion**: Upload and process invoices.
- **Debt & Loan Management**: Manage debts and loans effectively.
- **Payment History**: View payment history for better tracking.

### Budgeting & Finance Management
- **Net Worth**: Calculate and track your net worth.
- **CTC Breakdown**: Get a breakdown of your Cost to Company (CTC).
- **Set Monthly Budget**: Set and manage your monthly budget.

### General Queries
- **Start General Query Mode**: Ask general questions to the chatbot.

## Technologies Used

- Kotlin
- Flask (for API)
- Pandas (for data handling)
- Matplotlib (for data visualization)
- Google Gemini API (for AI capabilities)
- OpenCV (for image processing)
- Pandas (for data manipulation)

## API Endpoints

### Local API Endpoints

1. **/chat**
   - **Method**: `POST`
   - **Description**: Interact with the chatbot for transaction management and analysis.
   - **Request Body**: 
     ```json
     {
       "employee_id": "123",
       "user_input": "Summarise my expenses"
     }
     ```
   - **Response**: Returns a response from the chatbot.

2. **/invoices**
   - **Method**: `POST`
   - **Description**: Retrieve invoices for the last month for a specific employee.
   - **Request Body**: 
     ```json
     {
       "emp_id": "123"
     }
     ```
   - **Response**: Returns an image of the invoice table in base64 format.

3. **/manage_debt**
   - **Method**: `POST`
   - **Description**: Manage debt for an employee.
   - **Request Body**: 
     ```json
     {
       "emp_id": "123",
       "debt_amount": 5000
     }
     ```
   - **Response**: Returns details about the debt management process.

4. **/extract_invoice**
   - **Method**: `POST`
   - **Description**: Extract invoice details from OCR text.
   - **Request Body**: 
     ```json
     {
       "textBlocks": [
         {
           "blockText": "Example block text..."
         }
       ]
     }
     ```
   - **Response**: Returns extracted invoice details.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/your-repo-name.git
## Install Required Libraries
Make sure you have Python installed. If not, install it from the official Python website.

Once you have Python installed, you can install the required libraries for your Flask app by using pip. Assuming you already have a requirements.txt file or want to manually install each dependency, follow these steps:

# Flask Application Setup Guide

## Install Required Libraries

Make sure you have Python installed. If not, install it from the official Python website.

Once you have Python installed, you can install the required libraries for your Flask app by using `pip`. Assuming you already have a `requirements.txt` file or want to manually install each dependency, follow these steps:

### Option 1: Using `requirements.txt`

If you have a `requirements.txt` file that lists all the dependencies for your Flask application, simply run the following command to install them:

```bash
pip install -r requirements.txt
```

### Option 2: Manually Installing Dependencies

You can manually install each required library as listed below:

* **Flask**: For creating the web app.
  ```bash
  pip install Flask
  ```

* **pandas**: For handling data (used for CSV or Excel file processing).
  ```bash
  pip install pandas
  ```

* **matplotlib**: For generating graphs or tables in your Flask app.
  ```bash
  pip install matplotlib
  ```

* **openpyxl**: For reading and writing Excel files (optional if you're working with `.xlsx` files).
  ```bash
  pip install openpyxl
  ```

* **io**: This is a built-in Python library, so you don't need to install it separately.
* **base64**: Also a built-in Python library, no need to install.
* **re**: A built-in module for working with regular expressions.

## SSH for Port Tunneling

You don't need to install anything for SSH port tunneling as it's built into most Unix-based systems like Linux and macOS. For Windows, you can use tools like PuTTY or install OpenSSH.

## How to set up Port Tunneling

To set up the API on localhost for my Android app, I first created five separate files, each designed to handle different chatbot queries. These files run on different ports to manage specific requests. It’s crucial that both the mobile device running the Android app and the laptop running the API files are connected to the same local network, such as Wi-Fi. To start the API servers on the laptop, I ran each file on its designated port using commands like python chatbot_query1.py --port 5001 and so on for the other files. In the Android app, I configured the API base URL to point to the laptop’s local IP address and the respective ports. For instance, if the laptop’s IP address is 192.168.1.100, the base URL for the first chatbot query would be http://192.168.1.100:5001. Finally, I tested the setup by running the Android app to ensure it could successfully make API calls to the localhost servers on the laptop, verifying that each chatbot query was handled correctly by the respective API file.

## Usage
Interact with the chatbot via the provided API endpoints.
Use Postman or any HTTP client to send requests to the local API.

## Contributing
Contributions are welcome! Please fork the repository and submit a pull request for any changes or improvements.
