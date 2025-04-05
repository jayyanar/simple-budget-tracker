# Simple Budget Tracker

A comprehensive expense tracking application with a Flask REST API backend and a responsive HTML/CSS/JavaScript frontend, built entirely using Amazon Q through an iterative prompt-based approach.

> **NEW**: Check out [MYPROMPT.md](MYPROMPT.md) for the complete set of prompts used to build this application with Amazon Q. Follow these prompts to recreate the entire development process yourself!

![Workflow Diagram](img/workflow_diagram.png)

## Table of Contents

- [Features](#features)
- [Development with Amazon Q](#development-with-amazon-q)
- [Project Structure](#project-structure)
- [Development Workflow](#development-workflow)
- [Installation](#installation)
- [Running Locally](#running-locally)
- [API Documentation](#api-documentation)
- [Docker Deployment](#docker-deployment)
- [AWS Fargate Deployment](#aws-fargate-deployment)
- [Testing](#testing)
- [Future Enhancements](#future-enhancements)

## Features

- **Expense Tracking**: Add, update, and delete expenses with amount, category, date, and description
- **Category Management**: Organize expenses by categories
- **Summary Reports**: View expense summaries by category with visual charts
- **Balance Tracking**: Monitor your total expenses
- **Date Filtering**: Filter expenses, balances, and summaries by date range
- **Responsive UI**: User-friendly interface that works on desktop and mobile devices
- **RESTful API**: Well-structured API for programmatic access
- **Docker Support**: Containerized deployment for consistency across environments
- **AWS Fargate Deployment**: Cloud deployment with auto-scaling capabilities

## Development with Amazon Q

This project was built entirely using Amazon Q through an iterative prompt-based approach. No manual coding was required - all code was generated and refined through prompts to Amazon Q.

Key resources:
- [MYPROMPT.md](MYPROMPT.md): Complete set of prompts used to build and deploy the application
- [Story.md](Story.md): An intuitive story explaining the iterative development process with Amazon Q
- [prompts/](prompts/): Detailed documentation of each development step

## Project Structure

```
simple-budget-tracker/
├── src/
│   ├── app.py                 # Flask application with API endpoints
│   ├── budget_tracker.py      # Core budget tracking functionality
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css      # Custom CSS styles
│   │   └── js/
│   │       └── app.js         # Frontend JavaScript
│   └── templates/
│       ├── layout.html        # Base HTML template
│       └── index.html         # Main application page
├── testing_api/
│   └── postmancollection.json # Postman collection for API testing
├── tests/
│   └── test_budget_tracker.py # Unit tests for core functionality
├── prompts/
│   ├── BDD.md                 # Behavior-Driven Development specification
│   ├── TDD.md                 # Test-Driven Development approach
│   ├── greencode.md           # Core functionality implementation
│   ├── greencode_app_flask.md # Flask API implementation
│   ├── flask_ui_html.md       # HTML UI implementation
│   ├── docker_local.md        # Docker implementation
│   ├── sam_fargate.md         # AWS SAM/Fargate deployment
├── img/
│   ├── workflow_diagram.png   # Application workflow diagram
│   └── sculptor_and_robot.png # Illustration for the development story
├── Dockerfile                 # Docker configuration
├── template.yaml              # AWS SAM template for Fargate deployment
├── MYPROMPT.md                # Complete set of prompts used with Amazon Q
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## Development Workflow

Our development process followed these steps, all guided by Amazon Q:

1. **Requirements Analysis**: Created BDD specifications for the application
2. **Test-Driven Development**: Developed tests before implementation
3. **Core Functionality**: Implemented the `BudgetTracker` class with expense management features
4. **REST API Development**: Created a Flask API with endpoints for expense operations
5. **API Testing**: Developed and tested API endpoints using Postman
6. **Frontend Development**: Built a responsive HTML/CSS/JS interface
7. **Containerization**: Dockerized the application for consistent deployment
8. **Cloud Deployment**: Deployed to AWS Fargate with auto-scaling
9. **Documentation**: Created comprehensive documentation for all components

### Development Steps and Documentation

The following table outlines each development step and links to the corresponding documentation:

| Development Step | Description | Documentation |
|-----------------|-------------|---------------|
| Requirements Analysis | Behavior-Driven Development approach | [BDD.md](prompts/BDD.md) |
| Test-Driven Development | Testing strategy and implementation | [TDD.md](prompts/TDD.md) |
| Core Implementation | Budget tracker core functionality | [greencode.md](prompts/greencode.md) |
| REST API Development | Flask API implementation | [greencode_app_flask.md](prompts/greencode_app_flask.md) |
| Frontend Development | HTML/CSS/JS interface | [flask_ui_html.md](prompts/flask_ui_html.md) |
| Containerization | Docker implementation | [docker_local.md](prompts/docker_local.md) |
| Cloud Deployment | AWS Fargate deployment with SAM | [sam_fargate.md](prompts/sam_fargate.md) |
| Development Story | Narrative about iterative development | [Story.md](Story.md) |

## Installation

### Prerequisites

- Python 3.8+
- Docker (optional, for containerized deployment)
- AWS CLI and SAM CLI (optional, for AWS deployment)

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/simple-budget-tracker.git
   cd simple-budget-tracker
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running Locally

### Running the Flask Application

```bash
cd simple-budget-tracker
python src/app.py
```

The application will be available at http://localhost:5000

### Running with Docker

1. Build the Docker image:
   ```bash
   docker build -t budget-tracker .
   ```

2. Run the container:
   ```bash
   docker run -p 5000:5000 budget-tracker
   ```

The application will be available at http://localhost:5000

## API Documentation

### Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/expense` | POST | Add a new expense |
| `/expense` | GET | Get all expenses (with optional filtering) |
| `/expense/<expense_id>` | PUT | Update an existing expense |
| `/expense/<expense_id>` | DELETE | Delete an expense |
| `/balance` | GET | Get the total balance (with optional filtering) |
| `/summary` | GET | Get expense summary by category (with optional filtering) |

### Example Requests

#### Add an Expense

```bash
curl -X POST http://localhost:5000/expense \
  -H "Content-Type: application/json" \
  -d '{
    "amount": "45.99",
    "category": "Groceries",
    "date": "2025-04-02",
    "description": "Weekly grocery shopping"
  }'
```

#### Get Balance

```bash
curl -X GET http://localhost:5000/balance
```

#### Get Summary

```bash
curl -X GET http://localhost:5000/summary
```

For more detailed API documentation, refer to the Postman collection in `testing_api/postmancollection.json`.

## Docker Deployment

The application is containerized using Docker for consistent deployment across environments.

### Dockerfile Features

- Based on Python 3.11 slim image with platform specification for compatibility
- Optimized for size and performance
- Properly handles Python module imports
- Compatible with both local development and cloud deployment

### Building and Running

```bash
# Build the image
docker build -t budget-tracker .

# Run the container
docker run -p 5000:5000 budget-tracker
```

## AWS Fargate Deployment

The application can be deployed to AWS Fargate using the provided SAM template.

### Deployment Steps

1. Deploy the SAM template:
   ```bash
   sam deploy --template-file template.yaml --stack-name budget-tracker --capabilities CAPABILITY_IAM
   ```

2. Build and push the Docker image to ECR:
   ```bash
   # Login to ECR
   aws ecr get-login-password --region <region> | docker login --username AWS --password-stdin <account-id>.dkr.ecr.<region>.amazonaws.com
   
   # Build and tag the image
   docker build -t budget-tracker:latest .
   docker tag budget-tracker:latest <account-id>.dkr.ecr.<region>.amazonaws.com/budget-tracker:latest
   
   # Push the image to ECR
   docker push <account-id>.dkr.ecr.<region>.amazonaws.com/budget-tracker:latest
   ```

3. Access the application using the LoadBalancer DNS name from the stack outputs

### Auto-Scaling Configuration

The Fargate deployment includes auto-scaling capabilities:
- Minimum of 1 container to minimize costs
- Maximum of 5 containers to handle high demand
- Scales based on CPU utilization (70% threshold)

## Testing

### Unit Testing

Run the unit tests with pytest:

```bash
pytest tests/
```

### API Testing with Postman

A comprehensive Postman collection is provided in `testing_api/postmancollection.json` for testing all API endpoints.

To use the collection:
1. Import the collection into Postman
2. Set the `baseUrl` variable to your API's base URL (default is http://localhost:5000)
3. Run the requests to test the API functionality

## Future Enhancements

- **User Authentication**: Add user accounts and authentication
- **Data Persistence**: Implement database storage (PostgreSQL, MongoDB)
- **Budget Setting**: Allow users to set budget limits by category
- **Recurring Expenses**: Support for recurring expense entries
- **Data Export**: Export expense data to CSV/PDF
- **Mobile App**: Develop native mobile applications
- **CI/CD Pipeline**: Implement continuous integration and deployment

---

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
