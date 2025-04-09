"""
Tests for DynamoDB persistence features in Budget Tracker v2
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os
from decimal import Decimal

# Add the src directory to the path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

# Import modules to test - these will be implemented later
try:
    from budget_tracker_v2 import BudgetTrackerV2
except ImportError:
    # Create a placeholder for testing
    class BudgetTrackerV2:
        def __init__(self, db_table_name=None, region_name='us-east-1'):
            self._db_table = None if db_table_name is None else MagicMock()
            self._budget_limits_table = None if db_table_name is None else MagicMock()
            self._expenses = []
            self._budget_limits = {}

class TestDynamoDBPersistence(unittest.TestCase):
    def setUp(self):
        """Set up test environment before each test"""
        # Mock DynamoDB resource
        self.dynamodb_patcher = patch('boto3.resource')
        self.mock_dynamodb = self.dynamodb_patcher.start()
        self.mock_table = MagicMock()
        self.mock_dynamodb.return_value.Table.return_value = self.mock_table
        
        # Initialize BudgetTracker with mocked DynamoDB
        self.budget_tracker = BudgetTrackerV2(db_table_name='test-expenses')
    
    def tearDown(self):
        """Clean up after each test"""
        self.dynamodb_patcher.stop()
    
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

if __name__ == '__main__':
    unittest.main()
