"""
Budget Tracker Flask REST API

This module provides a REST API for the Budget Tracker application.
"""

from flask import Flask, request, jsonify, render_template
from datetime import datetime
from decimal import Decimal
import json
import os
from typing import Dict, Any
from functools import wraps

# Use absolute import for local development compatibility
from budget_tracker import BudgetTracker, Expense
from auth_service import AuthService

# Create Flask application
app = Flask(__name__)

# Create a single instance of BudgetTracker to be used across all requests
budget_tracker = BudgetTracker()

# Initialize authentication service
auth_service = AuthService(
    user_pool_id=os.environ.get('COGNITO_USER_POOL_ID'),
    client_id=os.environ.get('COGNITO_APP_CLIENT_ID'),
    region=os.environ.get('AWS_REGION', 'us-east-1')
)

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

# Authentication decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        if auth_header:
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({'error': 'Authentication token is missing'}), 401
        
        # Verify token
        is_valid, claims = auth_service.verify_token(token)
        if not is_valid:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        # Add user info to request
        request.user = auth_service.get_user_from_token(token)
        
        return f(*args, **kwargs)
    
    return decorated

@app.route('/')
def index():
    """Render the main HTML interface."""
    return render_template('index.html')

@app.route('/signup', methods=['POST'])
def signup():
    """
    Register a new user.
    
    Request body:
    {
        "email": "user@example.com",
        "password": "SecurePassword123"
    }
    """
    data = request.json
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    # Validate required fields
    required_fields = ["email", "password"]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    # Register user
    result = auth_service.register_user(
        email=data["email"],
        password=data["password"]
    )
    
    if result['success']:
        return jsonify({
            "message": result['message'],
            "user_id": result['user_id']
        }), 201
    else:
        return jsonify({"error": result['error']}), 400

@app.route('/verify', methods=['POST'])
def verify():
    """
    Verify a user's email with verification code.
    
    Request body:
    {
        "email": "user@example.com",
        "code": "123456"
    }
    """
    data = request.json
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    # Validate required fields
    required_fields = ["email", "code"]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    # Verify user
    result = auth_service.verify_user(
        email=data["email"],
        verification_code=data["code"]
    )
    
    if result['success']:
        return jsonify({"message": result['message']})
    else:
        return jsonify({"error": result['error']}), 400

@app.route('/login', methods=['POST'])
def login():
    """
    Authenticate a user and get tokens.
    
    Request body:
    {
        "email": "user@example.com",
        "password": "SecurePassword123"
    }
    """
    data = request.json
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    # Validate required fields
    required_fields = ["email", "password"]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    # Login user
    result = auth_service.login(
        email=data["email"],
        password=data["password"]
    )
    
    if result['success']:
        return jsonify({
            "message": result['message'],
            "token": result['id_token'],
            "refresh_token": result['refresh_token'],
            "expires_in": result['expires_in']
        })
    else:
        return jsonify({"error": result['error']}), 401

@app.route('/logout', methods=['POST'])
@token_required
def logout():
    """Log out a user by invalidating their tokens."""
    auth_header = request.headers.get('Authorization')
    access_token = auth_header.split(' ')[1] if auth_header else None
    
    if not access_token:
        return jsonify({"error": "No access token provided"}), 400
    
    result = auth_service.logout(access_token)
    
    if result['success']:
        return jsonify({"message": result['message']})
    else:
        return jsonify({"error": result['error']}), 400

@app.route('/forgot-password', methods=['POST'])
def forgot_password():
    """
    Initiate the forgot password flow.
    
    Request body:
    {
        "email": "user@example.com"
    }
    """
    data = request.json
    
    if not data or 'email' not in data:
        return jsonify({"error": "Email is required"}), 400
    
    result = auth_service.forgot_password(data['email'])
    
    if result['success']:
        return jsonify({"message": result['message']})
    else:
        return jsonify({"error": result['error']}), 400

@app.route('/reset-password', methods=['POST'])
def reset_password():
    """
    Complete the forgot password flow by setting a new password.
    
    Request body:
    {
        "email": "user@example.com",
        "code": "123456",
        "new_password": "NewSecurePassword123"
    }
    """
    data = request.json
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    # Validate required fields
    required_fields = ["email", "code", "new_password"]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    result = auth_service.reset_password(
        email=data['email'],
        code=data['code'],
        new_password=data['new_password']
    )
    
    if result['success']:
        return jsonify({"message": result['message']})
    else:
        return jsonify({"error": result['error']}), 400

@app.route('/expense', methods=['POST'])
@token_required
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
@token_required
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
@token_required
def delete_expense(expense_id):
    """Delete an expense by ID."""
    success = budget_tracker.delete_expense(expense_id)
    
    if not success:
        return jsonify({"error": f"Expense with ID {expense_id} not found"}), 404
    
    return jsonify({"message": f"Expense with ID {expense_id} deleted successfully"})

@app.route('/expense', methods=['GET'])
@token_required
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
@token_required
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
@token_required
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
