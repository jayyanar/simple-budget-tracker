import unittest
import json
from unittest.mock import patch, MagicMock
import sys
import os

# Add the src directory to the path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

# Import modules to test
# These will be implemented later based on the tests
from budget_tracker import BudgetTracker

class TestBudgetTrackerV2Features(unittest.TestCase):
    """Test cases for Budget Tracker V2 features including:
    - Data persistence with DynamoDB
    - Export functionality
    - Budget limits and notifications
    """
    
    def setUp(self):
        """Set up test environment before each test"""
        # Mock DynamoDB client
        self.dynamodb_patcher = patch('boto3.resource')
        self.mock_dynamodb = self.dynamodb_patcher.start()
        self.mock_table = MagicMock()
        self.mock_dynamodb.return_value.Table.return_value = self.mock_table
        
        # Initialize BudgetTracker with mocked DynamoDB
        self.budget_tracker = BudgetTracker(db_table_name='test-expenses')
    
    def tearDown(self):
        """Clean up after each test"""
        self.dynamodb_patcher.stop()
    
    # Data Persistence Tests
    def test_add_expense_with_persistence(self):
        """Test adding an expense with DynamoDB persistence"""
        # Arrange
        expense = {
            'amount': 50.0,
            'category': 'Groceries',
            'date': '2025-04-09',
            'description': 'Weekly shopping'
        }
        self.mock_table.put_item.return_value = {'ResponseMetadata': {'HTTPStatusCode': 200}}
        
        # Act
        result = self.budget_tracker.add_expense(expense)
        
        # Assert
        self.assertTrue(result['success'])
        self.assertIn('id', result)
        self.mock_table.put_item.assert_called_once()
        put_item_args = self.mock_table.put_item.call_args[1]
        self.assertEqual(put_item_args['Item']['category'], 'Groceries')
        self.assertEqual(float(put_item_args['Item']['amount']), 50.0)
    
    def test_get_expenses_from_dynamodb(self):
        """Test retrieving expenses from DynamoDB"""
        # Arrange
        mock_items = [
            {
                'id': '123',
                'amount': 50.0,
                'category': 'Groceries',
                'date': '2025-04-09',
                'description': 'Weekly shopping'
            },
            {
                'id': '456',
                'amount': 30.0,
                'category': 'Transportation',
                'date': '2025-04-08',
                'description': 'Bus fare'
            }
        ]
        self.mock_table.scan.return_value = {'Items': mock_items}
        
        # Act
        expenses = self.budget_tracker.get_expenses()
        
        # Assert
        self.assertEqual(len(expenses), 2)
        self.assertEqual(expenses[0]['id'], '123')
        self.assertEqual(expenses[1]['category'], 'Transportation')
        self.mock_table.scan.assert_called_once()
    
    def test_update_expense_in_dynamodb(self):
        """Test updating an expense in DynamoDB"""
        # Arrange
        expense_id = '123'
        updated_expense = {
            'amount': 55.0,
            'category': 'Groceries',
            'date': '2025-04-09',
            'description': 'Updated shopping list'
        }
        self.mock_table.update_item.return_value = {'ResponseMetadata': {'HTTPStatusCode': 200}}
        
        # Act
        result = self.budget_tracker.update_expense(expense_id, updated_expense)
        
        # Assert
        self.assertTrue(result['success'])
        self.mock_table.update_item.assert_called_once()
        update_args = self.mock_table.update_item.call_args[1]
        self.assertEqual(update_args['Key']['id'], expense_id)
        self.assertIn('UpdateExpression', update_args)
        self.assertIn('ExpressionAttributeValues', update_args)
    
    def test_delete_expense_from_dynamodb(self):
        """Test deleting an expense from DynamoDB"""
        # Arrange
        expense_id = '123'
        self.mock_table.delete_item.return_value = {'ResponseMetadata': {'HTTPStatusCode': 200}}
        
        # Act
        result = self.budget_tracker.delete_expense(expense_id)
        
        # Assert
        self.assertTrue(result['success'])
        self.mock_table.delete_item.assert_called_once_with(Key={'id': expense_id})
    
    # Export Functionality Tests
    def test_export_to_csv(self):
        """Test exporting expenses to CSV"""
        # Arrange
        mock_items = [
            {
                'id': '123',
                'amount': 50.0,
                'category': 'Groceries',
                'date': '2025-04-09',
                'description': 'Weekly shopping'
            },
            {
                'id': '456',
                'amount': 30.0,
                'category': 'Transportation',
                'date': '2025-04-08',
                'description': 'Bus fare'
            }
        ]
        self.mock_table.scan.return_value = {'Items': mock_items}
        
        # Act
        with patch('builtins.open', unittest.mock.mock_open()) as mock_file:
            result = self.budget_tracker.export_to_csv('test_export.csv')
        
        # Assert
        self.assertTrue(result['success'])
        mock_file.assert_called_once_with('test_export.csv', 'w', newline='')
        handle = mock_file()
        handle.write.assert_called()
    
    def test_export_to_pdf(self):
        """Test exporting expenses to PDF"""
        # Arrange
        mock_items = [
            {
                'id': '123',
                'amount': 50.0,
                'category': 'Groceries',
                'date': '2025-04-09',
                'description': 'Weekly shopping'
            },
            {
                'id': '456',
                'amount': 30.0,
                'category': 'Transportation',
                'date': '2025-04-08',
                'description': 'Bus fare'
            }
        ]
        self.mock_table.scan.return_value = {'Items': mock_items}
        
        # Act
        with patch('reportlab.platypus.SimpleDocTemplate') as mock_doc:
            result = self.budget_tracker.export_to_pdf('test_export.pdf')
        
        # Assert
        self.assertTrue(result['success'])
        mock_doc.assert_called_once()
    
    # Budget Limits and Notifications Tests
    def test_set_budget_limit(self):
        """Test setting a budget limit for a category"""
        # Arrange
        category = 'Groceries'
        limit = 200.0
        self.mock_table.put_item.return_value = {'ResponseMetadata': {'HTTPStatusCode': 200}}
        
        # Act
        result = self.budget_tracker.set_budget_limit(category, limit)
        
        # Assert
        self.assertTrue(result['success'])
        self.mock_table.put_item.assert_called_once()
        put_item_args = self.mock_table.put_item.call_args[1]
        self.assertEqual(put_item_args['Item']['category'], category)
        self.assertEqual(float(put_item_args['Item']['limit']), limit)
    
    def test_get_budget_limits(self):
        """Test retrieving all budget limits"""
        # Arrange
        mock_limits = [
            {'category': 'Groceries', 'limit': 200.0},
            {'category': 'Entertainment', 'limit': 100.0}
        ]
        self.mock_table.scan.return_value = {'Items': mock_limits}
        
        # Act
        limits = self.budget_tracker.get_budget_limits()
        
        # Assert
        self.assertEqual(len(limits), 2)
        self.assertEqual(limits[0]['category'], 'Groceries')
        self.assertEqual(limits[1]['limit'], 100.0)
    
    def test_check_budget_notification_under_limit(self):
        """Test budget notification when under limit"""
        # Arrange
        category = 'Groceries'
        # Mock current spending for category
        mock_items = [
            {'amount': 50.0, 'category': 'Groceries'},
            {'amount': 30.0, 'category': 'Groceries'}
        ]
        self.mock_table.scan.return_value = {'Items': mock_items}
        # Mock budget limit
        self.mock_table.get_item.return_value = {'Item': {'limit': 200.0}}
        
        # Act
        result = self.budget_tracker.check_budget_status(category)
        
        # Assert
        self.assertEqual(result['status'], 'under_limit')
        self.assertEqual(result['spent'], 80.0)
        self.assertEqual(result['limit'], 200.0)
        self.assertEqual(result['percentage'], 40.0)
    
    def test_check_budget_notification_near_limit(self):
        """Test budget notification when near limit (80%)"""
        # Arrange
        category = 'Groceries'
        # Mock current spending for category
        mock_items = [
            {'amount': 90.0, 'category': 'Groceries'},
            {'amount': 70.0, 'category': 'Groceries'}
        ]
        self.mock_table.scan.return_value = {'Items': mock_items}
        # Mock budget limit
        self.mock_table.get_item.return_value = {'Item': {'limit': 200.0}}
        
        # Act
        result = self.budget_tracker.check_budget_status(category)
        
        # Assert
        self.assertEqual(result['status'], 'near_limit')
        self.assertEqual(result['spent'], 160.0)
        self.assertEqual(result['limit'], 200.0)
        self.assertEqual(result['percentage'], 80.0)
    
    def test_check_budget_notification_over_limit(self):
        """Test budget notification when over limit"""
        # Arrange
        category = 'Groceries'
        # Mock current spending for category
        mock_items = [
            {'amount': 150.0, 'category': 'Groceries'},
            {'amount': 70.0, 'category': 'Groceries'}
        ]
        self.mock_table.scan.return_value = {'Items': mock_items}
        # Mock budget limit
        self.mock_table.get_item.return_value = {'Item': {'limit': 200.0}}
        
        # Act
        result = self.budget_tracker.check_budget_status(category)
        
        # Assert
        self.assertEqual(result['status'], 'over_limit')
        self.assertEqual(result['spent'], 220.0)
        self.assertEqual(result['limit'], 200.0)
        self.assertEqual(result['percentage'], 110.0)

if __name__ == '__main__':
    unittest.main()
