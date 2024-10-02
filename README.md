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
- [License](#license)

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

