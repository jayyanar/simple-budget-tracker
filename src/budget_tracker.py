"""
Budget Tracker Module

This module provides classes for tracking expenses and generating summaries by category.
"""

from datetime import datetime
from decimal import Decimal, InvalidOperation
import uuid
import csv
from typing import Dict, List, Optional, Union


class Expense:
    """
    Represents an individual expense with amount, category, date, and description.
    """
    
    def __init__(self, amount: Decimal, category: str, date: datetime, 
                 description: str = "", expense_id: str = None):
        """
        Initialize a new Expense.
        
        Args:
            amount: The expense amount as a Decimal
            category: The expense category
            date: The date of the expense
            description: Optional description of the expense
            expense_id: Optional unique identifier (generated if not provided)
        """
        self.id = expense_id if expense_id else str(uuid.uuid4())
        self.amount = amount
        self.category = category
        self.date = date
        self.description = description
    
    def __eq__(self, other):
        """
        Compare two expenses for equality.
        
        Args:
            other: Another Expense object to compare with
            
        Returns:
            True if the expenses have the same ID, False otherwise
        """
        if not isinstance(other, Expense):
            return False
        return self.id == other.id


class BudgetTracker:
    """
    Manages expenses and provides methods for tracking and summarizing expenses.
    """
    
    def __init__(self):
        """Initialize a new BudgetTracker with an empty list of expenses."""
        self._expenses = []
    
    def add_expense(self, amount: Union[Decimal, str], category: str, 
                   date: datetime, description: str = "") -> Expense:
        """
        Add a new expense to the tracker.
        
        Args:
            amount: The expense amount (Decimal or string that can be converted to Decimal)
            category: The expense category
            date: The date of the expense
            description: Optional description of the expense
            
        Returns:
            The newly created Expense object
            
        Raises:
            ValueError: If amount is invalid or category is missing
        """
        # Validate amount
        try:
            if not isinstance(amount, Decimal):
                amount = Decimal(str(amount))
        except (InvalidOperation, ValueError):
            raise ValueError("Please enter a valid amount")
        
        # Validate category
        if not category:
            raise ValueError("Please select a category")
        
        # Create and add the expense
        expense = Expense(amount, category, date, description)
        self._expenses.append(expense)
        return expense
    
    def update_expense(self, expense_id: str, amount: Decimal = None, 
                      category: str = None, date: datetime = None, 
                      description: str = None) -> Optional[Expense]:
        """
        Update an existing expense.
        
        Args:
            expense_id: The ID of the expense to update
            amount: The new amount (optional)
            category: The new category (optional)
            date: The new date (optional)
            description: The new description (optional)
            
        Returns:
            The updated Expense object, or None if not found
            
        Raises:
            ValueError: If amount is invalid or category is empty
        """
        for expense in self._expenses:
            if expense.id == expense_id:
                # Validate amount if provided
                if amount is not None:
                    try:
                        if not isinstance(amount, Decimal):
                            amount = Decimal(str(amount))
                        expense.amount = amount
                    except (InvalidOperation, ValueError):
                        raise ValueError("Please enter a valid amount")
                
                # Validate category if provided
                if category is not None:
                    if not category:
                        raise ValueError("Please select a category")
                    expense.category = category
                
                # Update other fields if provided
                if date is not None:
                    expense.date = date
                
                if description is not None:
                    expense.description = description
                
                return expense
        
        return None
    
    def delete_expense(self, expense_id: str) -> bool:
        """
        Delete an expense by ID.
        
        Args:
            expense_id: The ID of the expense to delete
            
        Returns:
            True if the expense was deleted, False if not found
        """
        for i, expense in enumerate(self._expenses):
            if expense.id == expense_id:
                del self._expenses[i]
                return True
        return False
    
    def get_expenses(self, start_date: datetime = None, 
                    end_date: datetime = None) -> List[Expense]:
        """
        Get all expenses, optionally filtered by date range.
        
        Args:
            start_date: Optional start date for filtering
            end_date: Optional end date for filtering
            
        Returns:
            List of Expense objects
        """
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
    
    def get_expenses_by_category(self, category: str) -> List[Expense]:
        """
        Get all expenses in a specific category.
        
        Args:
            category: The category to filter by
            
        Returns:
            List of Expense objects in the specified category
        """
        return [expense for expense in self._expenses if expense.category == category]
    
    def get_category_summary(self, start_date: datetime = None, 
                           end_date: datetime = None) -> Dict[str, Decimal]:
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
            if expense.category not in summary:
                summary[expense.category] = Decimal('0')
            summary[expense.category] += expense.amount
        
        return summary
    
    def get_total_expenses(self, start_date: datetime = None, 
                         end_date: datetime = None) -> Decimal:
        """
        Get the total of all expenses, optionally filtered by date range.
        
        Args:
            start_date: Optional start date for filtering
            end_date: Optional end date for filtering
            
        Returns:
            Total amount as a Decimal
        """
        expenses = self.get_expenses(start_date, end_date)
        return sum(expense.amount for expense in expenses)
    
    def export_summary(self, format: str = "CSV", filename: str = "expense_summary.csv"):
        """
        Export the expense summary to a file.
        
        Args:
            format: The export format (currently only "CSV" is supported)
            filename: The name of the file to export to
            
        Raises:
            ValueError: If the format is not supported
        """
        if format.upper() != "CSV":
            raise ValueError(f"Export format '{format}' is not supported")
        
        self.export_to_csv(filename)
    
    def export_to_csv(self, filename: str):
        """
        Export the expense data to a CSV file.
        
        Args:
            filename: The name of the file to export to
        """
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write header
            writer.writerow(['ID', 'Amount', 'Category', 'Date', 'Description'])
            
            # Write expense data
            for expense in self._expenses:
                writer.writerow([
                    expense.id,
                    str(expense.amount),
                    expense.category,
                    expense.date.strftime('%Y-%m-%d'),
                    expense.description
                ])
