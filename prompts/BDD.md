# Behavior-Driven Development (BDD) for Budget Tracker Application

## Prompt

Generate BDD scenarios for a budget tracker app where users can add expenses and summarize by category.

## Response

```gherkin
Feature: Expense Tracking
  As a user
  I want to track my expenses
  So that I can manage my budget effectively

  Scenario: Add a new expense
    Given I am on the expense entry page
    When I enter the expense amount "45.99"
    And I select the category "Groceries"
    And I enter the date "2025-04-02"
    And I enter the description "Weekly grocery shopping"
    And I click the "Add Expense" button
    Then I should see the expense in my expense list
    And the expense details should match my input

  Scenario: Add an expense with invalid amount
    Given I am on the expense entry page
    When I enter the expense amount "abc"
    And I select the category "Groceries"
    And I enter the date "2025-04-02"
    And I click the "Add Expense" button
    Then I should see an error message "Please enter a valid amount"
    And the expense should not be added to my expense list

  Scenario: Add an expense without selecting a category
    Given I am on the expense entry page
    When I enter the expense amount "25.00"
    And I enter the date "2025-04-02"
    And I click the "Add Expense" button
    Then I should see an error message "Please select a category"
    And the expense should not be added to my expense list

  Scenario: Edit an existing expense
    Given I have an expense with amount "30.50" in category "Dining"
    When I select the expense from my expense list
    And I change the amount to "35.75"
    And I change the category to "Entertainment"
    And I save the changes
    Then I should see the updated expense in my expense list
    And the expense should show amount "35.75" and category "Entertainment"

  Scenario: Delete an expense
    Given I have an expense in my expense list
    When I select the expense
    And I click the "Delete" button
    And I confirm the deletion
    Then the expense should be removed from my expense list

Feature: Expense Summary by Category
  As a user
  I want to view my expenses summarized by category
  So that I can understand my spending patterns

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

  Scenario: Filter expense summary by date range
    Given I have expenses from "2025-03-01" to "2025-04-02"
    When I navigate to the "Summary" page
    And I set the date range from "2025-04-01" to "2025-04-02"
    Then I should only see expenses within the selected date range
    And the category totals should reflect only the filtered expenses

  Scenario: Export expense summary
    Given I am viewing my expense summary by category
    When I click the "Export" button
    And I select the format "CSV"
    Then a CSV file should be downloaded
    And the file should contain all my expense summary data

  Scenario: View expense breakdown within a category
    Given I am viewing my expense summary by category
    When I click on the "Groceries" category
    Then I should see a detailed list of all expenses in that category
    And the total should match the category total in the summary view
```

## Implementation Notes

These BDD scenarios outline the core functionality of the budget tracker application:

1. **Expense Management**:
   - Adding new expenses with validation
   - Editing existing expenses
   - Deleting expenses

2. **Expense Summarization**:
   - Viewing expenses grouped by category
   - Filtering expenses by date range
   - Exporting expense data
   - Viewing detailed breakdowns within categories

3. **Data Validation**:
   - Ensuring expense amounts are valid numbers
   - Requiring category selection
   - Proper date formatting

These scenarios can be used to drive the development of both the backend logic and frontend interface of the budget tracker application, ensuring that all user requirements are met.
