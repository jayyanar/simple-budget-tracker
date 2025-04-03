# Test-Driven Development (TDD) for Budget Tracker Application

## Prompt

Generate Python unit tests from provided BDD scenarios for BudgetTracker functionality - refer /Users/jayyanar/simple-budget-tracker/prompts/BDD.md and store the response under tests/test_budget_tracker.py
can you store the prompt under prompts folder used for TDD as TDD.md

## Response

The TDD approach involves creating tests first, before implementing the actual functionality. For the Budget Tracker application, we've created comprehensive unit tests based on the BDD scenarios defined earlier.

The test file is structured as follows:

```python
import unittest
from datetime import datetime
from decimal import Decimal
from unittest.mock import MagicMock, patch

# Import the modules to be tested
# These imports will need to be updated based on your actual implementation
# from budget_tracker.models import BudgetTracker, Expense, Category


class TestExpenseTracking(unittest.TestCase):
    """
    Test cases for the Expense Tracking feature based on BDD scenarios.
    """
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Initialize the BudgetTracker instance for testing
        # self.budget_tracker = BudgetTracker()
        
        # For now, we'll use a mock since we don't have the actual implementation
        self.budget_tracker = MagicMock()
        self.budget_tracker.get_expenses.return_value = []
    
    def test_add_new_expense(self):
        """
        Test adding a new expense with valid data.
        
        Scenario: Add a new expense
            Given I am on the expense entry page
            When I enter the expense amount "45.99"
            And I select the category "Groceries"
            And I enter the date "2025-04-02"
            And I enter the description "Weekly grocery shopping"
            And I click the "Add Expense" button
            Then I should see the expense in my expense list
            And the expense details should match my input
        """
        # Test implementation...
    
    def test_add_expense_with_invalid_amount(self):
        """
        Test adding an expense with an invalid amount.
        
        Scenario: Add an expense with invalid amount
            Given I am on the expense entry page
            When I enter the expense amount "abc"
            And I select the category "Groceries"
            And I enter the date "2025-04-02"
            And I click the "Add Expense" button
            Then I should see an error message "Please enter a valid amount"
            And the expense should not be added to my expense list
        """
        # Test implementation...
    
    # Additional test methods...


class TestExpenseSummaryByCategory(unittest.TestCase):
    """
    Test cases for the Expense Summary by Category feature based on BDD scenarios.
    """
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Initialize the BudgetTracker instance for testing
        # self.budget_tracker = BudgetTracker()
        
        # For now, we'll use a mock since we don't have the actual implementation
        self.budget_tracker = MagicMock()
        
        # Create sample expenses for testing
        self.sample_expenses = [
            # Sample expense objects...
        ]
    
    def test_view_expense_summary_by_category(self):
        """
        Test viewing expense summary by category.
        
        Scenario: View expense summary by category
            Given I have the following expenses:
              | Amount | Category      | Date       | Description      |
              | 45.99  | Groceries     | 2025-04-01 | Weekly groceries |
              | 12.50  | Transportation| 2025-04-01 | Bus fare         |
              | 30.00  | Dining        | 2025-04-02 | Lunch with team  |
              | 25.75  | Groceries     | 2025-04-02 | Fruits and snacks|
            When I navigate to the "Summary" page
            Then I should see the following category totals:
              | Category      | Total Amount |
              | Groceries     | 71.74        |
              | Transportation| 12.50        |
              | Dining        | 30.00        |
            And the total expenses should be "114.24"
        """
        # Test implementation...
    
    # Additional test methods...
```

## Implementation Notes

The test suite follows these TDD principles:

1. **Tests First**: All tests are written before the actual implementation.

2. **Comprehensive Coverage**: Tests cover all the functionality described in the BDD scenarios.

3. **Mocking**: Since the actual implementation doesn't exist yet, we use mocks to simulate the expected behavior.

4. **Clear Documentation**: Each test includes a docstring that references the original BDD scenario.

5. **Validation Testing**: Tests include validation of inputs and error handling.

6. **Edge Cases**: Tests cover various scenarios including invalid inputs and boundary conditions.

The next step in the TDD process would be to implement the actual `BudgetTracker` class and related functionality to make these tests pass. The implementation should include:

1. An `Expense` class with properties for amount, category, date, and description
2. A `BudgetTracker` class with methods for:
   - Adding, updating, and deleting expenses
   - Retrieving expenses and filtering by category or date
   - Calculating summaries by category
   - Exporting data

Once the implementation is complete, the tests can be updated to use the actual classes instead of mocks.
