"""
Budget Tracker V2 Module

This module extends the original BudgetTracker with DynamoDB persistence,
export functionality, and budget limits/notifications.
"""

from datetime import datetime
from decimal import Decimal, InvalidOperation
import uuid
import csv
from typing import Dict, List, Optional, Union, Any

# Import original BudgetTracker for backward compatibility
from budget_tracker import Expense

class BudgetTrackerV2:
    """
    Enhanced version of BudgetTracker with DynamoDB persistence,
    export functionality, and budget limits.
    """
    
    def __init__(self, db_table_name=None, region_name='us-east-1'):
        """
        Initialize a new BudgetTracker with either in-memory storage or DynamoDB.
        
        Args:
            db_table_name: Optional DynamoDB table name for persistence
            region_name: AWS region for DynamoDB (default: us-east-1)
        """
        self._expenses = []
        self._db_table = None
        self._budget_limits_table = None
        self._budget_limits = {}  # In-memory storage for budget limits
        
        # Set up DynamoDB if table name is provided
        if db_table_name:
            import boto3
            dynamodb = boto3.resource('dynamodb', region_name=region_name)
            self._db_table = dynamodb.Table(db_table_name)
            
            # Create budget limits table name by appending '-limits'
            budget_limits_table_name = f"{db_table_name}-limits"
            self._budget_limits_table = dynamodb.Table(budget_limits_table_name)
    
    def add_expense(self, expense_data):
        """
        Add a new expense to the tracker.
        
        Args:
            expense_data: Dictionary containing expense details or
                         parameters for amount, category, date, description
        
        Returns:
            Dictionary with success status and expense ID
        """
        try:
            # Handle both dictionary input and individual parameters
            if isinstance(expense_data, dict):
                amount = expense_data.get('amount')
                category = expense_data.get('category')
                date_str = expense_data.get('date')
                description = expense_data.get('description', '')
                
                # Convert date string to datetime if needed
                if isinstance(date_str, str):
                    date = datetime.strptime(date_str, '%Y-%m-%d')
                else:
                    date = date_str
            else:
                # Assume old-style parameters
                amount, category, date, description = expense_data
            
            # Validate inputs
            if not isinstance(amount, Decimal):
                amount = Decimal(str(amount))
            
            if not category:
                return {'success': False, 'error': 'Category is required'}
            
            # Generate ID
            expense_id = str(uuid.uuid4())
            
            # Create expense object for storage
            if isinstance(date, str):
                date = datetime.strptime(date, '%Y-%m-%d')
            
            expense_dict = {
                'id': expense_id,
                'amount': amount,
                'category': category,
                'date': date.strftime('%Y-%m-%d'),
                'description': description
            }
            
            # Store in DynamoDB if available, otherwise in memory
            if self._db_table:
                self._db_table.put_item(Item=expense_dict)
            else:
                # Create Expense object for in-memory storage
                expense_obj = Expense(
                    amount=amount,
                    category=category,
                    date=date,
                    description=description,
                    expense_id=expense_id
                )
                self._expenses.append(expense_obj)
            
            return {'success': True, 'id': expense_id}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_expenses(self, start_date=None, end_date=None):
        """
        Get all expenses, optionally filtered by date range.
        
        Args:
            start_date: Optional start date for filtering
            end_date: Optional end date for filtering
            
        Returns:
            List of expenses
        """
        if self._db_table:
            # Get from DynamoDB
            response = self._db_table.scan()
            expenses = response.get('Items', [])
            
            # Apply date filtering if needed
            if start_date or end_date:
                filtered_expenses = []
                for expense in expenses:
                    expense_date = datetime.strptime(expense['date'], '%Y-%m-%d')
                    if start_date and expense_date < start_date:
                        continue
                    if end_date and expense_date > end_date:
                        continue
                    filtered_expenses.append(expense)
                return filtered_expenses
            return expenses
        else:
            # Get from in-memory storage
            if start_date is None and end_date is None:
                return self._expenses.copy()
            
            filtered_expenses = []
            for expense in self._expenses:
                if start_date and expense.date < start_date:
                    continue
                if end_date and expense.date > end_date:
                    continue
                filtered_expenses.append(expense)
            
            return filtered_expenses
    
    def get_expenses_by_category(self, category):
        """
        Get all expenses in a specific category.
        
        Args:
            category: The category to filter by
            
        Returns:
            List of expenses in the specified category
        """
        expenses = self.get_expenses()
        
        if self._db_table:
            # Filter DynamoDB results
            return [expense for expense in expenses if expense['category'] == category]
        else:
            # Filter in-memory results
            return [expense for expense in expenses if expense.category == category]
    
    def update_expense(self, expense_id, updated_expense=None, **kwargs):
        """
        Update an existing expense.
        
        Args:
            expense_id: The ID of the expense to update
            updated_expense: Dictionary with updated values or
            **kwargs: Individual fields to update
            
        Returns:
            Dictionary with success status
        """
        try:
            # Handle both dictionary and kwargs
            if updated_expense is None:
                updated_expense = kwargs
            
            if self._db_table:
                # Update in DynamoDB
                update_expression_parts = []
                expression_values = {}
                
                for key, value in updated_expense.items():
                    if key != 'id':  # Don't update the ID
                        update_expression_parts.append(f"#{key} = :{key}")
                        expression_values[f":{key}"] = value
                        
                if not update_expression_parts:
                    return {'success': False, 'error': 'No fields to update'}
                
                update_expression = "SET " + ", ".join(update_expression_parts)
                
                # Create attribute name mapping
                expression_names = {f"#{key}": key for key in updated_expense if key != 'id'}
                
                self._db_table.update_item(
                    Key={'id': expense_id},
                    UpdateExpression=update_expression,
                    ExpressionAttributeNames=expression_names,
                    ExpressionAttributeValues=expression_values
                )
                
                return {'success': True}
            else:
                # Update in memory
                for i, expense in enumerate(self._expenses):
                    if expense.id == expense_id:
                        # Update fields
                        if 'amount' in updated_expense:
                            amount = updated_expense['amount']
                            if not isinstance(amount, Decimal):
                                amount = Decimal(str(amount))
                            expense.amount = amount
                        
                        if 'category' in updated_expense:
                            expense.category = updated_expense['category']
                        
                        if 'date' in updated_expense:
                            date = updated_expense['date']
                            if isinstance(date, str):
                                date = datetime.strptime(date, '%Y-%m-%d')
                            expense.date = date
                        
                        if 'description' in updated_expense:
                            expense.description = updated_expense['description']
                        
                        return {'success': True}
                
                return {'success': False, 'error': 'Expense not found'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def delete_expense(self, expense_id):
        """
        Delete an expense by ID.
        
        Args:
            expense_id: The ID of the expense to delete
            
        Returns:
            Dictionary with success status
        """
        try:
            if self._db_table:
                # Delete from DynamoDB
                self._db_table.delete_item(Key={'id': expense_id})
                return {'success': True}
            else:
                # Delete from memory
                for i, expense in enumerate(self._expenses):
                    if expense.id == expense_id:
                        del self._expenses[i]
                        return {'success': True}
                return {'success': False, 'error': 'Expense not found'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_category_summary(self, start_date=None, end_date=None):
        """
        Get a summary of expenses by category, optionally filtered by date range.
        
        Args:
            start_date: Optional start date for filtering
            end_date: Optional end date for filtering
            
        Returns:
            Dictionary mapping category names to total amounts
        """
        expenses = self.get_expenses(start_date, end_date)
        summary = {}
        
        for expense in expenses:
            if self._db_table:
                # DynamoDB format
                category = expense['category']
                amount = Decimal(str(expense['amount']))
            else:
                # In-memory format
                category = expense.category
                amount = expense.amount
            
            if category not in summary:
                summary[category] = Decimal('0')
            summary[category] += amount
        
        return summary
    
    def get_total_expenses(self, start_date=None, end_date=None):
        """
        Get the total of all expenses, optionally filtered by date range.
        
        Args:
            start_date: Optional start date for filtering
            end_date: Optional end date for filtering
            
        Returns:
            Total amount as a Decimal
        """
        expenses = self.get_expenses(start_date, end_date)
        total = Decimal('0')
        
        for expense in expenses:
            if self._db_table:
                # DynamoDB format
                total += Decimal(str(expense['amount']))
            else:
                # In-memory format
                total += expense.amount
        
        return total
    
    def export_to_csv(self, filename):
        """
        Export expenses to CSV file.
        
        Args:
            filename: Path to save the CSV file
        
        Returns:
            Dictionary with success status
        """
        try:
            # Get all expenses
            expenses = self.get_expenses()
            
            with open(filename, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write header
                writer.writerow(['ID', 'Amount', 'Category', 'Date', 'Description'])
                
                # Write expense data
                for expense in expenses:
                    if self._db_table:
                        # DynamoDB format
                        writer.writerow([
                            expense['id'],
                            str(expense['amount']),
                            expense['category'],
                            expense['date'],
                            expense['description']
                        ])
                    else:
                        # In-memory format (Expense object)
                        writer.writerow([
                            expense.id,
                            str(expense.amount),
                            expense.category,
                            expense.date.strftime('%Y-%m-%d'),
                            expense.description
                        ])
            
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def export_to_pdf(self, filename):
        """
        Export expenses to PDF file.
        
        Args:
            filename: Path to save the PDF file
        
        Returns:
            Dictionary with success status
        """
        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
            from reportlab.lib.styles import getSampleStyleSheet
            
            # Get all expenses
            expenses = self.get_expenses()
            
            # Create PDF document
            doc = SimpleDocTemplate(filename, pagesize=letter)
            elements = []
            
            # Add title
            styles = getSampleStyleSheet()
            elements.append(Paragraph("Expense Report", styles['Title']))
            
            # Create table data
            data = [['ID', 'Amount', 'Category', 'Date', 'Description']]
            
            # Add expense data
            for expense in expenses:
                if self._db_table:
                    # DynamoDB format
                    data.append([
                        expense['id'],
                        str(expense['amount']),
                        expense['category'],
                        expense['date'],
                        expense['description']
                    ])
                else:
                    # In-memory format (Expense object)
                    data.append([
                        expense.id,
                        str(expense.amount),
                        expense.category,
                        expense.date.strftime('%Y-%m-%d'),
                        expense.description
                    ])
            
            # Create table
            table = Table(data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(table)
            
            # Add summary
            summary = self.get_category_summary()
            summary_data = [['Category', 'Total']]
            for category, total in summary.items():
                summary_data.append([category, str(total)])
            
            elements.append(Paragraph("Expense Summary by Category", styles['Heading2']))
            summary_table = Table(summary_data)
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(summary_table)
            
            # Build PDF
            doc.build(elements)
            
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def set_budget_limit(self, category, limit):
        """
        Set a budget limit for a specific category.
        
        Args:
            category: The expense category
            limit: The budget limit amount
        
        Returns:
            Dictionary with success status
        """
        try:
            if not isinstance(limit, Decimal):
                limit = Decimal(str(limit))
            
            budget_item = {
                'category': category,
                'limit': limit
            }
            
            # Store in DynamoDB if available, otherwise in memory
            if self._budget_limits_table:
                self._budget_limits_table.put_item(Item=budget_item)
            else:
                # Store in memory
                self._budget_limits[category] = limit
            
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_budget_limits(self):
        """
        Get all budget limits.
        
        Returns:
            List of budget limits by category
        """
        if self._budget_limits_table:
            response = self._budget_limits_table.scan()
            return response.get('Items', [])
        else:
            # Return from memory
            return [{'category': cat, 'limit': limit} for cat, limit in self._budget_limits.items()]
    
    def check_budget_status(self, category):
        """
        Check the budget status for a specific category.
        
        Args:
            category: The expense category to check
        
        Returns:
            Dictionary with budget status information
        """
        # Get the budget limit for the category
        limit = None
        
        if self._budget_limits_table:
            response = self._budget_limits_table.get_item(Key={'category': category})
            if 'Item' in response:
                limit = Decimal(str(response['Item'].get('limit')))
        else:
            # Get from memory
            limit = self._budget_limits.get(category)
        
        if limit is None:
            return {
                'status': 'no_limit',
                'message': f'No budget limit set for {category}'
            }
        
        # Calculate total spent in this category
        total_spent = Decimal('0')
        
        expenses = self.get_expenses_by_category(category)
        for expense in expenses:
            if self._db_table:
                # DynamoDB format
                total_spent += Decimal(str(expense['amount']))
            else:
                # In-memory format (Expense object)
                total_spent += expense.amount
        
        # Calculate percentage of limit
        percentage = (total_spent / limit) * 100
        
        # Determine status
        if percentage >= 100:
            status = 'over_limit'
            message = f'Budget exceeded for {category}! Spent {total_spent} of {limit} ({percentage:.1f}%)'
        elif percentage >= 80:
            status = 'near_limit'
            message = f'Approaching budget limit for {category}. Spent {total_spent} of {limit} ({percentage:.1f}%)'
        else:
            status = 'under_limit'
            message = f'Budget for {category} is on track. Spent {total_spent} of {limit} ({percentage:.1f}%)'
        
        return {
            'status': status,
            'message': message,
            'spent': total_spent,
            'limit': limit,
            'percentage': float(percentage)
        }
