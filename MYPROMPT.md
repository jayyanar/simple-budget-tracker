# Building a Budget Tracker Application with Amazon Q: End-to-End Prompts

This document contains the complete set of prompts used to build and deploy the Simple Budget Tracker application using Amazon Q. By following these prompts in sequence, you can recreate the entire application development process.

## 1. Requirements Analysis with BDD

```
Create a behavior-driven development (BDD) specification for a simple budget tracker application that allows users to track expenses.
```

## 2. Test-Driven Development Approach

```
Create a test-driven development approach for implementing the budget tracker based on the BDD specification.
```

## 3. Core Implementation

```
Implement the core BudgetTracker class based on the test cases, with functionality for adding, updating, and deleting expenses, as well as getting summaries and balances.
```

## 4. Flask API Development

```
Create a Flask REST API using the BudgetTracker class with endpoints: POST /expense, GET /balance, and GET /summary. Store the code under src/app.py.
```

## 5. API Testing with Postman

```
Create a Postman Collection to validate all usecase and store the response testing_api/postmancollection.json.
```

## 6. Frontend Development

```
Create a Flask REST API using the BudgetTracker class with endpoints: POST /expense, GET /balance, and GET /summary. Store the code under src/app.py. Add a nice HTML interface to display the Expense Tracker application.
```

## 7. Containerization with Docker

```
Write a Dockerfile to containerize this Flask application.
```

## 8. Fixing Module Import Error

```
Update the docker file since it is missing ModuleNotFoundError: No module named 'budget_tracker'
```

## 9. AWS SAM Template for Fargate Deployment

```
Generate AWS SAM template to deploy the containerized BudgetTracker Flask API to AWS Fargate. Ask me as input for VPC and Subnet Settings.
```

When prompted for VPC and subnet information:
```
1. Do you have an existing VPC you'd like to use, or should I create a new one in the template? - I have existing one
2. If using an existing VPC, what is the VPC ID? - vpc-e326b89e
3. Do you have specific subnets you want to use for the Fargate service? If so, what are the subnet IDs? - subnet-92602df4 and subnet-59343357
4. Do you need public or private subnets for your Fargate service? - Public
5. Do you have a specific security group to use, or should I create one? - Create one
```

## 10. Fixing IAM Policy Error

```
Update the Role to arn:aws:iam::aws:policy/AmazonECS_FullAccess
```

## 11. Fixing Docker Execution Error

```
getting error while running exec /usr/local/bin/gunicorn: exec format error
```

## 12. Handling Existing ECR Repository

```
getting error Resource handler returned message: "Resource of type 'AWS::ECR::Repository' with identifier 'budget-tracker' already exists." - Update the template accordinly
```

## 13. Fixing Architecture Mismatch Error

```
while running fargate getting below error "exec /usr/local/bin/python: exec format error"
```

## 14. Implementing Auto-Scaling

```
currently we have 2 fargate is running, I want reduce it to 1 - scale maximum of 5 in case of more request. Give me update template and Yaml file need to be update
```

## Tips for Using These Prompts

1. **Follow the Sequence**: These prompts build upon each other, with each step depending on the output of previous steps.

2. **Be Specific**: When you encounter errors or need modifications, be specific about what you need.

3. **Provide Context**: If Amazon Q asks for additional information (like VPC IDs), provide it clearly.

4. **Iterative Refinement**: Don't expect perfect results from the first prompt. Be prepared to refine and iterate.

5. **No-Touch Coding**: Try to follow the "no-touch coding" approach where you rely on Amazon Q to generate and fix code based on your prompts, without manually editing files yourself.

6. **Learn from Errors**: Pay attention to the errors and how they're fixed - this is valuable learning about cloud deployment.

By following these prompts, you'll experience firsthand how Amazon Q can assist in building and deploying a complete application through an iterative, conversational approach.
