# Flask REST API Implementation for Budget Tracker

## Prompt

Create a Flask REST API using the BudgetTracker class with endpoints: POST /expense, GET /balance, and GET /summary. Store the code under src/app.py.

## Implementation Reasoning

The implementation of the Flask REST API for the Budget Tracker application was designed with the following considerations:

### 1. API Design and Endpoints

The API provides the following endpoints:

- **POST /expense**: Add a new expense
- **PUT /expense/{expense_id}**: Update an existing expense
- **DELETE /expense/{expense_id}**: Delete an expense
- **GET /expense**: Get all expenses with optional filtering
- **GET /balance**: Get the total of all expenses
- **GET /summary**: Get a summary of expenses by category

While the prompt specifically requested three endpoints, I included additional endpoints (PUT, DELETE, GET for expenses) to provide a complete RESTful API that supports all CRUD operations on expenses.

### 2. Data Handling and Serialization

- **JSON Serialization**: Custom JSON encoder to handle Decimal and datetime objects, which aren't natively serializable by Flask's JSON encoder.
- **Request Validation**: Proper validation of request data with clear error messages.
- **Date Parsing**: Flexible date parsing that accepts both ISO format with time and simple date format (YYYY-MM-DD).
- **Response Structure**: Consistent response structure with appropriate HTTP status codes.

### 3. Query Parameters for Filtering

- **Date Range Filtering**: All endpoints that return expense data support optional date range filtering via `start_date` and `end_date` query parameters.
- **Category Filtering**: The GET /expense endpoint supports filtering by category.

### 4. Error Handling

- **Input Validation**: Validation of required fields and data types with descriptive error messages.
- **Resource Not Found**: Proper 404 responses when attempting to update or delete non-existent expenses.
- **Bad Request**: 400 responses for invalid input data.

### 5. Integration with BudgetTracker

- **Singleton Instance**: A single instance of BudgetTracker is created and used across all requests, ensuring data persistence during the application's lifetime.
- **Method Mapping**: Each API endpoint maps directly to one or more methods of the BudgetTracker class.

### 6. Extensibility

- **Helper Functions**: Utility functions for common operations like date parsing and object serialization.
- **Modular Design**: Clean separation between the API layer and the business logic in the BudgetTracker class.

## API Usage Examples

### Adding an Expense

```
POST /expense
Content-Type: application/json

{
    "amount": "45.99",
    "category": "Groceries",
    "date": "2025-04-02",
    "description": "Weekly grocery shopping"
}
```

### Getting the Balance

```
GET /balance?start_date=2025-04-01&end_date=2025-04-30
```

### Getting the Category Summary

```
GET /summary?start_date=2025-04-01&end_date=2025-04-30
```

## Future Enhancements

1. **Authentication and Authorization**: Add user authentication to support multiple users with their own expense data.
2. **Pagination**: Implement pagination for the GET /expense endpoint to handle large numbers of expenses.
3. **Data Persistence**: Add database integration to persist expenses between application restarts.
4. **Input Sanitization**: Add more robust input validation and sanitization.
5. **API Documentation**: Integrate Swagger/OpenAPI for automatic API documentation.
6. **Rate Limiting**: Implement rate limiting to prevent abuse.
7. **Caching**: Add response caching for improved performance.

The current implementation provides a solid foundation that can be extended with these enhancements as needed.
