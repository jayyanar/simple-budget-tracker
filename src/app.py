"""
Budget Tracker Flask REST API

This module provides a REST API for the Budget Tracker application.
"""

from flask import Flask, request, jsonify, render_template
from datetime import datetime
from decimal import Decimal
import json
from typing import Dict, Any

# Use absolute import for local development compatibility
from budget_tracker import BudgetTracker, Expense

# Create Flask application
app = Flask(__name__)

# Create a single instance of BudgetTracker to be used across all requests
budget_tracker = BudgetTracker()

# Custom JSON encoder to handle Decimal and datetime objects
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

app.json_encoder = CustomJSONEncoder

# Helper function to parse date strings
def parse_date(date_str: str) -> datetime:
    """Parse a date string in ISO format."""
    try:
        return datetime.fromisoformat(date_str)
    except ValueError:
        # Try to parse as just a date (without time)
        try:
            return datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            raise ValueError(f"Invalid date format: {date_str}. Use ISO format (YYYY-MM-DD).")

# Helper function to convert Expense object to dictionary
def expense_to_dict(expense: Expense) -> Dict[str, Any]:
    """Convert an Expense object to a dictionary for JSON serialization."""
    return {
        "id": expense.id,
        "amount": str(expense.amount),
        "category": expense.category,
        "date": expense.date.isoformat(),
        "description": expense.description
    }

@app.route('/')
def index():
    """Render the main HTML interface."""
    return render_template('index.html')

@app.route('/expense', methods=['POST'])
def add_expense():
    """
    Add a new expense.
    
    Request body:
    {
        "amount": "45.99",
        "category": "Groceries",
        "date": "2025-04-02",
        "description": "Weekly grocery shopping"
    }
    """
    data = request.json
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    # Validate required fields
    required_fields = ["amount", "category", "date"]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    try:
        # Parse the date
        date = parse_date(data["date"])
        
        # Add the expense
        expense = budget_tracker.add_expense(
            amount=data["amount"],
            category=data["category"],
            date=date,
            description=data.get("description", "")
        )
        
        # Return the created expense
        return jsonify({
            "message": "Expense added successfully",
            "expense": expense_to_dict(expense)
        }), 201
    
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@app.route('/expense/<expense_id>', methods=['PUT'])
def update_expense(expense_id):
    """
    Update an existing expense.
    
    Request body:
    {
        "amount": "35.75",
        "category": "Entertainment",
        "date": "2025-04-02",
        "description": "Movie tickets"
    }
    """
    data = request.json
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    try:
        # Parse the date if provided
        date = None
        if "date" in data:
            date = parse_date(data["date"])
        
        # Update the expense
        expense = budget_tracker.update_expense(
            expense_id=expense_id,
            amount=data.get("amount"),
            category=data.get("category"),
            date=date,
            description=data.get("description")
        )
        
        if expense is None:
            return jsonify({"error": f"Expense with ID {expense_id} not found"}), 404
        
        # Return the updated expense
        return jsonify({
            "message": "Expense updated successfully",
            "expense": expense_to_dict(expense)
        })
    
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@app.route('/expense/<expense_id>', methods=['DELETE'])
def delete_expense(expense_id):
    """Delete an expense by ID."""
    success = budget_tracker.delete_expense(expense_id)
    
    if not success:
        return jsonify({"error": f"Expense with ID {expense_id} not found"}), 404
    
    return jsonify({"message": f"Expense with ID {expense_id} deleted successfully"})

@app.route('/expense', methods=['GET'])
def get_expenses():
    """
    Get all expenses, optionally filtered by date range.
    
    Query parameters:
    - start_date: Optional start date for filtering (ISO format)
    - end_date: Optional end date for filtering (ISO format)
    - category: Optional category for filtering
    """
    # Parse date filters if provided
    start_date = None
    end_date = None
    category = request.args.get('category')
    
    if 'start_date' in request.args:
        try:
            start_date = parse_date(request.args['start_date'])
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
    
    if 'end_date' in request.args:
        try:
            end_date = parse_date(request.args['end_date'])
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
    
    # Get expenses with optional date filtering
    if category:
        # If category is provided, filter by category
        expenses = budget_tracker.get_expenses_by_category(category)
        # Apply date filtering if needed
        if start_date or end_date:
            expenses = [e for e in expenses if 
                       (start_date is None or e.date >= start_date) and
                       (end_date is None or e.date <= end_date)]
    else:
        # Otherwise, get all expenses with optional date filtering
        expenses = budget_tracker.get_expenses(start_date, end_date)
    
    # Convert expenses to dictionaries for JSON serialization
    expenses_dict = [expense_to_dict(expense) for expense in expenses]
    
    return jsonify({"expenses": expenses_dict})

@app.route('/balance', methods=['GET'])
def get_balance():
    """
    Get the current balance (total expenses).
    
    Query parameters:
    - start_date: Optional start date for filtering (ISO format)
    - end_date: Optional end date for filtering (ISO format)
    """
    # Parse date filters if provided
    start_date = None
    end_date = None
    
    if 'start_date' in request.args:
        try:
            start_date = parse_date(request.args['start_date'])
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
    
    if 'end_date' in request.args:
        try:
            end_date = parse_date(request.args['end_date'])
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
    
    # Get total expenses with optional date filtering
    total = budget_tracker.get_total_expenses(start_date, end_date)
    
    return jsonify({
        "balance": str(total),
        "filters": {
            "start_date": start_date.isoformat() if start_date else None,
            "end_date": end_date.isoformat() if end_date else None
        }
    })

@app.route('/summary', methods=['GET'])
def get_summary():
    """
    Get a summary of expenses by category.
    
    Query parameters:
    - start_date: Optional start date for filtering (ISO format)
    - end_date: Optional end date for filtering (ISO format)
    """
    # Parse date filters if provided
    start_date = None
    end_date = None
    
    if 'start_date' in request.args:
        try:
            start_date = parse_date(request.args['start_date'])
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
    
    if 'end_date' in request.args:
        try:
            end_date = parse_date(request.args['end_date'])
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
    
    # Get category summary with optional date filtering
    summary = budget_tracker.get_category_summary(start_date, end_date)
    
    # Convert Decimal values to strings for JSON serialization
    summary_dict = {category: str(amount) for category, amount in summary.items()}
    
    # Get total expenses
    total = budget_tracker.get_total_expenses(start_date, end_date)
    
    return jsonify({
        "summary": summary_dict,
        "total": str(total),
        "filters": {
            "start_date": start_date.isoformat() if start_date else None,
            "end_date": end_date.isoformat() if end_date else None
        }
    })

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
