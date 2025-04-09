# BudgetTracker v2 Implementation

This document outlines the implementation of BudgetTracker v2 features based on the test cases defined in TDD_v2.md and TDD_v2_create_testcase.md.

## Implementation Plan

The implementation will add the following features to the existing BudgetTracker:

1. **Data Persistence with DynamoDB**
   - Replace in-memory storage with AWS DynamoDB
   - Maintain backward compatibility with existing code

2. **Export Functionality**
   - Enhance existing CSV export
   - Add PDF export capability

3. **Budget Limits and Notifications**
   - Add ability to set budget limits by category
   - Implement notification system for approaching/exceeding limits

## Implementation Approach

We'll extend the existing BudgetTracker class to maintain backward compatibility while adding new features. This will be done through:

1. Optional parameters in the constructor to support both in-memory and DynamoDB modes
2. Extending existing methods to work with both storage mechanisms
3. Adding new methods for the new features

## Implementation Steps

### Step 1: Extend BudgetTracker Constructor for DynamoDB Support

```python
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
    
    # Set up DynamoDB if table name is provided
    if db_table_name:
        import boto3
        dynamodb = boto3.resource('dynamodb', region_name=region_name)
        self._db_table = dynamodb.Table(db_table_name)
        
        # Create budget limits table name by appending '-limits'
        budget_limits_table_name = f"{db_table_name}-limits"
        self._budget_limits_table = dynamodb.Table(budget_limits_table_name)
```

### Step 2: Update CRUD Operations for DynamoDB

Modify the existing methods to work with both storage mechanisms:

```python
def add_expense(self, expense_data):
    """
    Add a new expense to the tracker.
    
    Args:
        expense_data: Dictionary containing expense details or
                     parameters for amount, category, date, description
    
    Returns:
        Dictionary with success status and expense ID
    """
    # Handle both dictionary input and individual parameters
    if isinstance(expense_data, dict):
        amount = expense_data.get('amount')
        category = expense_data.get('category')
        date_str = expense_data.get('date')
        description = expense_data.get('description', '')
        
        # Convert date string to datetime if needed
        if isinstance(date_str, str):
            from datetime import datetime
            date = datetime.strptime(date_str, '%Y-%m-%d')
        else:
            date = date_str
    else:
        # Assume old-style parameters
        amount, category, date, description = expense_data
    
    # Validate inputs as before
    try:
        from decimal import Decimal
        if not isinstance(amount, Decimal):
            amount = Decimal(str(amount))
    except:
        return {'success': False, 'error': 'Invalid amount'}
    
    if not category:
        return {'success': False, 'error': 'Category is required'}
    
    # Generate ID
    import uuid
    expense_id = str(uuid.uuid4())
    
    # Create expense object for in-memory storage
    from datetime import datetime
    if isinstance(date, str):
        date = datetime.strptime(date, '%Y-%m-%d')
    
    expense = {
        'id': expense_id,
        'amount': amount,
        'category': category,
        'date': date.strftime('%Y-%m-%d'),
        'description': description
    }
    
    # Store in DynamoDB if available, otherwise in memory
    if self._db_table:
        self._db_table.put_item(Item=expense)
    else:
        from decimal import Decimal
        from datetime import datetime
        # Create Expense object for in-memory storage
        from budget_tracker import Expense
        expense_obj = Expense(
            amount=amount,
            category=category,
            date=date,
            description=description,
            expense_id=expense_id
        )
        self._expenses.append(expense_obj)
    
    return {'success': True, 'id': expense_id}
```

### Step 3: Implement Export Functionality

Enhance the existing CSV export and add PDF export:

```python
def export_to_csv(self, filename):
    """
    Export expenses to CSV file.
    
    Args:
        filename: Path to save the CSV file
    
    Returns:
        Dictionary with success status
    """
    try:
        import csv
        
        # Get all expenses
        expenses = self.get_expenses()
        
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write header
            writer.writerow(['ID', 'Amount', 'Category', 'Date', 'Description'])
            
            # Write expense data
            for expense in expenses:
                if isinstance(expense, dict):
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
            if isinstance(expense, dict):
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
```

### Step 4: Implement Budget Limits and Notifications

Add methods for setting and checking budget limits:

```python
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
        from decimal import Decimal
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
            # Store in memory if no DynamoDB
            if not hasattr(self, '_budget_limits'):
                self._budget_limits = {}
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
        # Return from memory if no DynamoDB
        if not hasattr(self, '_budget_limits'):
            return []
        
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
            limit = response['Item'].get('limit')
    else:
        # Get from memory if no DynamoDB
        if hasattr(self, '_budget_limits') and category in self._budget_limits:
            limit = self._budget_limits[category]
    
    if limit is None:
        return {
            'status': 'no_limit',
            'message': f'No budget limit set for {category}'
        }
    
    # Calculate total spent in this category
    from decimal import Decimal
    total_spent = Decimal('0')
    
    expenses = self.get_expenses_by_category(category)
    for expense in expenses:
        if isinstance(expense, dict):
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
        'percentage': percentage
    }
```

## Reasoning and Decisions

1. **Backward Compatibility**
   - Maintained the original in-memory storage option
   - Added DynamoDB as an optional storage mechanism
   - Ensured all methods work with both storage types

2. **Storage Strategy**
   - Used two DynamoDB tables: one for expenses and one for budget limits
   - Named the budget limits table by appending "-limits" to the expenses table name

3. **Error Handling**
   - Added comprehensive error handling for all operations
   - Returned consistent response objects with success/error information

4. **Data Conversion**
   - Added logic to handle both dictionary and object representations of expenses
   - Ensured proper type conversion between string dates and datetime objects

5. **PDF Generation**
   - Used ReportLab for PDF generation as it's a robust and widely-used library
   - Included both detailed expense list and category summary in the PDF

6. **Budget Notifications**
   - Implemented a three-tier notification system: under_limit, near_limit (80%), over_limit
   - Included detailed information in the notification response for UI flexibility

## Testing Considerations

1. The implementation is designed to pass all test cases in budget_tracker_v02_feature.py
2. Additional dependencies (boto3, reportlab) will need to be added to requirements.txt
3. For local testing without AWS, the in-memory mode can be used

## Next Steps

1. Update the Flask API to expose the new functionality
2. Enhance the UI to support budget limits and notifications
3. Add authentication to protect user data
4. Implement actual AWS DynamoDB tables through CloudFormation/SAM
