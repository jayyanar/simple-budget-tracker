"""
Tests for budget limits and notifications in Budget Tracker v2
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
        
        def get_expenses_by_category(self, category):
            return []

class TestBudgetLimits(unittest.TestCase):
    def setUp(self):
        """Set up test environment before each test"""
        # Mock DynamoDB resource
        self.dynamodb_patcher = patch('boto3.resource')
        self.mock_dynamodb = self.dynamodb_patcher.start()
        self.mock_table = MagicMock()
        self.mock_limits_table = MagicMock()
        
        # Configure the mock to return different tables
        def get_table(table_name):
            if table_name == 'test-expenses':
                return self.mock_table
            elif table_name == 'test-expenses-limits':
                return self.mock_limits_table
            return MagicMock()
        
        self.mock_dynamodb.return_value.Table.side_effect = get_table
        
        # Initialize BudgetTracker with mocked DynamoDB
        self.budget_tracker = BudgetTrackerV2(db_table_name='test-expenses')
    
    def tearDown(self):
        """Clean up after each test"""
        self.dynamodb_patcher.stop()
    
    def test_set_budget_limit(self):
        """Test setting a budget limit for a category"""
        # Arrange
        category = 'Groceries'
        limit = Decimal('200.0')
        self.mock_limits_table.put_item.return_value = {'ResponseMetadata': {'HTTPStatusCode': 200}}
        
        # Act
        result = self.budget_tracker.set_budget_limit(category, limit)
        
        # Assert
        self.assertTrue(result['success'])
        self.mock_limits_table.put_item.assert_called_once()
        put_item_args = self.mock_limits_table.put_item.call_args[1]
        self.assertEqual(put_item_args['Item']['category'], category)
        self.assertEqual(put_item_args['Item']['limit'], limit)
    
    def test_get_budget_limits(self):
        """Test retrieving all budget limits"""
        # Arrange
        mock_limits = [
            {'category': 'Groceries', 'limit': Decimal('200.0')},
            {'category': 'Entertainment', 'limit': Decimal('100.0')}
        ]
        self.mock_limits_table.scan.return_value = {'Items': mock_limits}
        
        # Act
        limits = self.budget_tracker.get_budget_limits()
        
        # Assert
        self.assertEqual(len(limits), 2)
        self.assertEqual(limits[0]['category'], 'Groceries')
        self.assertEqual(limits[1]['limit'], Decimal('100.0'))
    
    def test_check_budget_notification_under_limit(self):
        """Test budget notification when under limit"""
        # Arrange
        category = 'Groceries'
        # Mock current spending for category
        mock_expenses = [
            {'amount': Decimal('50.0'), 'category': 'Groceries'},
            {'amount': Decimal('30.0'), 'category': 'Groceries'}
        ]
        
        with patch.object(self.budget_tracker, 'get_expenses_by_category', return_value=mock_expenses):
            # Mock budget limit
            self.mock_limits_table.get_item.return_value = {'Item': {'limit': Decimal('200.0')}}
            
            # Act
            result = self.budget_tracker.check_budget_status(category)
            
            # Assert
            self.assertEqual(result['status'], 'under_limit')
            self.assertEqual(result['spent'], Decimal('80.0'))
            self.assertEqual(result['limit'], Decimal('200.0'))
            self.assertEqual(result['percentage'], Decimal('40.0'))
    
    def test_check_budget_notification_near_limit(self):
        """Test budget notification when near limit (80%)"""
        # Arrange
        category = 'Groceries'
        # Mock current spending for category
        mock_expenses = [
            {'amount': Decimal('90.0'), 'category': 'Groceries'},
            {'amount': Decimal('70.0'), 'category': 'Groceries'}
        ]
        
        with patch.object(self.budget_tracker, 'get_expenses_by_category', return_value=mock_expenses):
            # Mock budget limit
            self.mock_limits_table.get_item.return_value = {'Item': {'limit': Decimal('200.0')}}
            
            # Act
            result = self.budget_tracker.check_budget_status(category)
            
            # Assert
            self.assertEqual(result['status'], 'near_limit')
            self.assertEqual(result['spent'], Decimal('160.0'))
            self.assertEqual(result['limit'], Decimal('200.0'))
            self.assertEqual(result['percentage'], Decimal('80.0'))
    
    def test_check_budget_notification_over_limit(self):
        """Test budget notification when over limit"""
        # Arrange
        category = 'Groceries'
        # Mock current spending for category
        mock_expenses = [
            {'amount': Decimal('150.0'), 'category': 'Groceries'},
            {'amount': Decimal('70.0'), 'category': 'Groceries'}
        ]
        
        with patch.object(self.budget_tracker, 'get_expenses_by_category', return_value=mock_expenses):
            # Mock budget limit
            self.mock_limits_table.get_item.return_value = {'Item': {'limit': Decimal('200.0')}}
            
            # Act
            result = self.budget_tracker.check_budget_status(category)
            
            # Assert
            self.assertEqual(result['status'], 'over_limit')
            self.assertEqual(result['spent'], Decimal('220.0'))
            self.assertEqual(result['limit'], Decimal('200.0'))
            self.assertEqual(result['percentage'], Decimal('110.0'))

if __name__ == '__main__':
    unittest.main()
