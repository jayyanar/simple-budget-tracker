# Behavior-Driven Development (BDD) for Budget Tracker Application v2

## Prompt

```
Create a comprehensive BDD specification for Budget Tracker v2 that includes both the original core features and new features for authentication, data persistence with DynamoDB, export functionality, budget limits, and recurring expenses.
```

## Response

# Behavior-Driven Development (BDD) for Budget Tracker Application v2

## Core Features and Enhancements

This document outlines the behavior-driven development specifications for the Budget Tracker application, including the original core features and new enhancements for authentication, data persistence, and export functionality.

```gherkin
# CORE FEATURES
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

# NEW FEATURES

Feature: User Authentication
  As a user
  I want secure access to my expense tracker
  So that my financial data remains confidential

  Scenario: User signs up for a new account
    Given I am on the signup page
    When I enter my email "user@example.com"
    And I create a password "SecurePass123"
    And I confirm my password "SecurePass123"
    And I click the "Sign Up" button
    Then I should receive a verification email

  Scenario: User logs in successfully
    Given I have an existing account
    When I enter my email "user@example.com"
    And I enter my password "SecurePass123"
    And I click the "Login" button
    Then I should see the dashboard

  Scenario: User fails login due to incorrect password
    Given I have an existing account
    When I enter my email "user@example.com"
    And I enter an incorrect password "WrongPass"
    And I click the "Login" button
    Then I should see an error message "Invalid username or password"

  Scenario: User logs out
    Given I am logged in
    When I click the "Logout" button
    Then I should be redirected to the login page
    And I should not have access to my expense data

  Scenario: User resets forgotten password
    Given I am on the login page
    When I click the "Forgot Password" link
    And I enter my email "user@example.com"
    And I click the "Reset Password" button
    Then I should receive a password reset email
    And I should be able to set a new password

Feature: Data Persistence
  As a user
  I want my expense data stored persistently
  So that my data is securely saved and retrievable anytime

  Scenario: Expense data saved to DynamoDB
    Given I am logged in and add a new expense
    When I save the expense
    Then the expense details should be stored in DynamoDB

  Scenario: Retrieve stored expenses
    Given I have previously saved expenses
    When I log in and view my expense list
    Then I should see all my previously stored expenses

  Scenario: Update stored expense
    Given I am logged in and viewing my expense list
    When I edit an existing expense
    And I save the changes
    Then the updated expense should be stored in DynamoDB
    And I should see the updated expense in my list

  Scenario: Delete stored expense
    Given I am logged in and viewing my expense list
    When I delete an expense
    Then the expense should be removed from DynamoDB
    And the expense should no longer appear in my list

  Scenario: Data synchronization across devices
    Given I have added expenses on one device
    When I log in from another device
    Then I should see the same expense data on both devices

Feature: Data Export
  As a user
  I want to export my expenses
  So that I can analyze them externally

  Scenario: Export expenses to CSV
    Given I am viewing my expense summary
    When I click the "Export CSV" button
    Then a CSV file containing my expenses should be downloaded

  Scenario: Export expenses to PDF
    Given I am viewing my expense summary
    When I click the "Export PDF" button
    Then a PDF file containing my expenses should be downloaded

  Scenario: Export filtered expenses
    Given I am viewing my expense summary
    When I apply filters for date range and categories
    And I click the "Export CSV" button
    Then a CSV file containing only the filtered expenses should be downloaded

  Scenario: Export with custom fields
    Given I am on the export page
    When I select specific fields to include in the export
    And I click the "Export CSV" button
    Then a CSV file containing only the selected fields should be downloaded

Feature: Budget Setting and Alerts
  As a user
  I want to set budget limits for different categories
  So that I can be alerted when I approach or exceed my limits

  Scenario: Set category budget
    Given I am logged in
    When I navigate to the "Budgets" page
    And I select the category "Groceries"
    And I set a monthly budget of "300.00"
    And I save the budget
    Then the budget should be saved
    And I should see "Groceries: $300.00" in my budget list

  Scenario: Receive budget alert
    Given I have set a monthly budget of "300.00" for "Groceries"
    And I have spent "270.00" on "Groceries" this month
    When I add a new expense of "40.00" in category "Groceries"
    Then I should receive an alert "Budget Exceeded: Groceries"
    And the alert should show I am "$10.00 over budget"

  Scenario: View budget progress
    Given I have set budgets for multiple categories
    When I navigate to the "Dashboard" page
    Then I should see a visual representation of my budget usage
    And I should see the percentage of budget used for each category

Feature: Recurring Expenses
  As a user
  I want to set up recurring expenses
  So that I don't have to manually enter regular payments

  Scenario: Create monthly recurring expense
    Given I am logged in
    When I navigate to the "Recurring Expenses" page
    And I click "Add Recurring Expense"
    And I enter the amount "15.99"
    And I select the category "Subscriptions"
    And I enter the description "Streaming Service"
    And I select frequency "Monthly"
    And I set the start date "2025-05-01"
    And I click "Save"
    Then the recurring expense should be saved
    And I should see it listed in my recurring expenses

  Scenario: Auto-generation of recurring expenses
    Given I have a monthly recurring expense of "15.99" for "Streaming Service"
    When the system processes recurring expenses for "2025-05-01"
    Then a new expense should be automatically created
    And the expense should have amount "15.99"
    And the expense should be in category "Subscriptions"
    And the expense should have description "Streaming Service (Recurring)"

  Scenario: Edit recurring expense
    Given I have a recurring expense set up
    When I edit the recurring expense
    And I save the changes
    Then the changes should apply to future occurrences only
    And past generated expenses should remain unchanged

  Scenario: Delete recurring expense
    Given I have a recurring expense set up
    When I delete the recurring expense
    Then no future expenses should be generated from this recurring expense
    And I should be asked if I want to delete past generated expenses
```

## Implementation Notes

This enhanced BDD specification outlines both the core functionality and new features for the Budget Tracker application:

### Core Features
1. **Expense Management**: Adding, editing, and deleting expenses with validation
2. **Expense Summarization**: Viewing and filtering expenses by category and date

### New Features
1. **User Authentication with Amazon Cognito**:
   - User registration with email verification
   - Secure login/logout functionality
   - Password reset capabilities

2. **Data Persistence with DynamoDB**:
   - Cloud storage of expense data
   - User-specific data association
   - Cross-device synchronization

3. **Budget Setting and Alerts**:
   - Category-specific budget limits
   - Alerts when approaching or exceeding budgets
   - Visual budget progress tracking

4. **Data Export**:
   - CSV export for spreadsheet analysis
   - PDF export with formatted reports
   - Filtered exports by date and category
   - Custom field selection

5. **Recurring Expenses**:
   - Setup of regular payments
   - Automatic expense generation
   - Management of recurring expense series

These scenarios will drive the development of both the backend and frontend components, ensuring that all user requirements are met in a testable, verifiable manner. The implementation will leverage AWS services including Amazon Cognito for authentication and DynamoDB for data persistence.
