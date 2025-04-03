import unittest
from datetime import datetime
from decimal import Decimal
from unittest.mock import MagicMock, patch

# Import the modules to be tested
from src.budget_tracker import BudgetTracker, Expense


class TestExpenseTracking(unittest.TestCase):
    """
    Test cases for the Expense Tracking feature based on BDD scenarios.
    """
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Initialize the BudgetTracker instance for testing
        self.budget_tracker = BudgetTracker()
    
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
        # Execute the action: add a new expense
        expense = self.budget_tracker.add_expense(
            amount=Decimal("45.99"),
            category="Groceries",
            date=datetime(2025, 4, 2),
            description="Weekly grocery shopping"
        )
        
        # Verify the expense was added to the list
        expenses = self.budget_tracker.get_expenses()
        self.assertIn(expense, expenses)
        
        # Verify the expense details match the input
        self.assertEqual(expense.amount, Decimal("45.99"))
        self.assertEqual(expense.category, "Groceries")
        self.assertEqual(expense.date, datetime(2025, 4, 2))
        self.assertEqual(expense.description, "Weekly grocery shopping")
    
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
        # Execute the action and verify it raises the expected exception
        with self.assertRaises(ValueError) as context:
            self.budget_tracker.add_expense(
                amount="abc",  # Invalid amount
                category="Groceries",
                date=datetime(2025, 4, 2),
                description=""
            )
        
        # Verify the error message
        self.assertEqual(str(context.exception), "Please enter a valid amount")
        
        # Verify no expense was added
        expenses = self.budget_tracker.get_expenses()
        self.assertEqual(len(expenses), 0)
    
    def test_add_expense_without_category(self):
        """
        Test adding an expense without selecting a category.
        
        Scenario: Add an expense without selecting a category
            Given I am on the expense entry page
            When I enter the expense amount "25.00"
            And I enter the date "2025-04-02"
            And I click the "Add Expense" button
            Then I should see an error message "Please select a category"
            And the expense should not be added to my expense list
        """
        # Execute the action and verify it raises the expected exception
        with self.assertRaises(ValueError) as context:
            self.budget_tracker.add_expense(
                amount=Decimal("25.00"),
                category=None,  # Missing category
                date=datetime(2025, 4, 2),
                description=""
            )
        
        # Verify the error message
        self.assertEqual(str(context.exception), "Please select a category")
        
        # Verify no expense was added
        expenses = self.budget_tracker.get_expenses()
        self.assertEqual(len(expenses), 0)
    
    def test_edit_existing_expense(self):
        """
        Test editing an existing expense.
        
        Scenario: Edit an existing expense
            Given I have an expense with amount "30.50" in category "Dining"
            When I select the expense from my expense list
            And I change the amount to "35.75"
            And I change the category to "Entertainment"
            And I save the changes
            Then I should see the updated expense in my expense list
            And the expense should show amount "35.75" and category "Entertainment"
        """
        # Create an original expense
        original_expense = self.budget_tracker.add_expense(
            amount=Decimal("30.50"),
            category="Dining",
            date=datetime(2025, 4, 2),
            description="Lunch"
        )
        
        # Execute the action: update the expense
        updated_expense = self.budget_tracker.update_expense(
            expense_id=original_expense.id,
            amount=Decimal("35.75"),
            category="Entertainment",
            date=original_expense.date,
            description=original_expense.description
        )
        
        # Verify the expense was updated in the list
        expenses = self.budget_tracker.get_expenses()
        self.assertIn(updated_expense, expenses)
        
        # Verify the expense details were updated
        self.assertEqual(updated_expense.amount, Decimal("35.75"))
        self.assertEqual(updated_expense.category, "Entertainment")
    
    def test_delete_expense(self):
        """
        Test deleting an expense.
        
        Scenario: Delete an expense
            Given I have an expense in my expense list
            When I select the expense
            And I click the "Delete" button
            And I confirm the deletion
            Then the expense should be removed from my expense list
        """
        # Create an expense to be deleted
        expense = self.budget_tracker.add_expense(
            amount=Decimal("45.99"),
            category="Groceries",
            date=datetime(2025, 4, 2),
            description="Weekly grocery shopping"
        )
        
        # Get the expense ID
        expense_id = expense.id
        
        # Execute the action: delete the expense
        self.budget_tracker.delete_expense(expense_id)
        
        # Verify the expense was removed from the list
        expenses = self.budget_tracker.get_expenses()
        self.assertNotIn(expense, expenses)


class TestExpenseSummaryByCategory(unittest.TestCase):
    """
    Test cases for the Expense Summary by Category feature based on BDD scenarios.
    """
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Initialize the BudgetTracker instance for testing
        self.budget_tracker = BudgetTracker()
        
        # Create sample expenses for testing
        self.budget_tracker.add_expense(
            amount=Decimal("45.99"),
            category="Groceries",
            date=datetime(2025, 4, 1),
            description="Weekly groceries"
        )
        self.budget_tracker.add_expense(
            amount=Decimal("12.50"),
            category="Transportation",
            date=datetime(2025, 4, 1),
            description="Bus fare"
        )
        self.budget_tracker.add_expense(
            amount=Decimal("30.00"),
            category="Dining",
            date=datetime(2025, 4, 2),
            description="Lunch with team"
        )
        self.budget_tracker.add_expense(
            amount=Decimal("25.75"),
            category="Groceries",
            date=datetime(2025, 4, 2),
            description="Fruits and snacks"
        )
    
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
        # Execute the action: get the category summary
        summary = self.budget_tracker.get_category_summary()
        
        # Verify the category totals
        expected_summary = {
            "Groceries": Decimal("71.74"),
            "Transportation": Decimal("12.50"),
            "Dining": Decimal("30.00")
        }
        self.assertEqual(summary, expected_summary)
        
        # Verify the total expenses
        total = self.budget_tracker.get_total_expenses()
        self.assertEqual(total, Decimal("114.24"))
    
    def test_filter_expense_summary_by_date_range(self):
        """
        Test filtering expense summary by date range.
        
        Scenario: Filter expense summary by date range
            Given I have expenses from "2025-03-01" to "2025-04-02"
            When I navigate to the "Summary" page
            And I set the date range from "2025-04-01" to "2025-04-02"
            Then I should only see expenses within the selected date range
            And the category totals should reflect only the filtered expenses
        """
        # Add an expense from March
        self.budget_tracker.add_expense(
            amount=Decimal("50.00"),
            category="Entertainment",
            date=datetime(2025, 3, 15),
            description="Movie tickets"
        )
        
        # Execute the action: get the filtered category summary
        start_date = datetime(2025, 4, 1)
        end_date = datetime(2025, 4, 2)
        filtered_summary = self.budget_tracker.get_category_summary(
            start_date=start_date,
            end_date=end_date
        )
        
        # Verify the filtered category totals
        expected_filtered_summary = {
            "Groceries": Decimal("71.74"),
            "Transportation": Decimal("12.50"),
            "Dining": Decimal("30.00")
        }
        self.assertEqual(filtered_summary, expected_filtered_summary)
        
        # Verify the filtered total expenses
        filtered_total = self.budget_tracker.get_total_expenses(
            start_date=start_date,
            end_date=end_date
        )
        self.assertEqual(filtered_total, Decimal("114.24"))
    
    @patch('builtins.open', create=True)
    def test_export_expense_summary(self, mock_open):
        """
        Test exporting expense summary.
        
        Scenario: Export expense summary
            Given I am viewing my expense summary by category
            When I click the "Export" button
            And I select the format "CSV"
            Then a CSV file should be downloaded
            And the file should contain all my expense summary data
        """
        # Execute the action: export the summary
        filename = "expense_summary.csv"
        self.budget_tracker.export_summary(format="CSV", filename=filename)
        
        # Verify the file was opened for writing
        mock_open.assert_called_once_with(filename, 'w', newline='')
    
    def test_view_expense_breakdown_within_category(self):
        """
        Test viewing expense breakdown within a category.
        
        Scenario: View expense breakdown within a category
            Given I am viewing my expense summary by category
            When I click on the "Groceries" category
            Then I should see a detailed list of all expenses in that category
            And the total should match the category total in the summary view
        """
        # Execute the action: get expenses for a specific category
        category_expenses = self.budget_tracker.get_expenses_by_category("Groceries")
        
        # Verify we got the right number of expenses
        self.assertEqual(len(category_expenses), 2)
        
        # Calculate the total and verify it matches the expected value
        category_total = sum(expense.amount for expense in category_expenses)
        self.assertEqual(category_total, Decimal("71.74"))
        
        # Verify the expense descriptions
        descriptions = [expense.description for expense in category_expenses]
        self.assertIn("Weekly groceries", descriptions)
        self.assertIn("Fruits and snacks", descriptions)


if __name__ == '__main__':
    unittest.main()
