#!/bin/bash

# Create a Cognito User Pool
echo "Creating Cognito User Pool..."
aws cognito-idp create-user-pool \
  --pool-name BudgetTrackerUserPool \
  --auto-verify-attributes email \
  --username-attributes email \
  --policies '{"PasswordPolicy":{"MinimumLength":8,"RequireUppercase":true,"RequireLowercase":true,"RequireNumbers":true,"RequireSymbols":false}}' \
  --schema '[{"Name":"email","AttributeDataType":"String","Mutable":true,"Required":true}]' \
  --verification-message-template '{"DefaultEmailOption":"CONFIRM_WITH_CODE","EmailMessage":"Your verification code is {####}","EmailSubject":"Budget Tracker - Verification Code"}' \
  > cognito-user-pool.json

# Extract the User Pool ID
USER_POOL_ID=$(jq -r '.UserPool.Id' cognito-user-pool.json)
echo "User Pool ID: $USER_POOL_ID"

# Create a Cognito User Pool Client
echo "Creating Cognito User Pool Client..."
aws cognito-idp create-user-pool-client \
  --user-pool-id $USER_POOL_ID \
  --client-name BudgetTrackerClient \
  --no-generate-secret \
  --explicit-auth-flows ALLOW_USER_PASSWORD_AUTH ALLOW_REFRESH_TOKEN_AUTH \
  --prevent-user-existence-errors ENABLED \
  --supported-identity-providers COGNITO \
  > cognito-client.json

# Extract the Client ID
CLIENT_ID=$(jq -r '.UserPoolClient.ClientId' cognito-client.json)
echo "Client ID: $CLIENT_ID"

# Create or update .env file with Cognito information
if [ -f .env ]; then
  # Update existing .env file
  sed -i.bak '/COGNITO_USER_POOL_ID=/d' .env
  sed -i.bak '/COGNITO_APP_CLIENT_ID=/d' .env
  sed -i.bak '/AWS_REGION=/d' .env
  rm -f .env.bak
fi

# Add Cognito information to .env file
echo "Updating .env file..."
echo "COGNITO_USER_POOL_ID=$USER_POOL_ID" >> .env
echo "COGNITO_APP_CLIENT_ID=$CLIENT_ID" >> .env
echo "AWS_REGION=$(aws configure get region)" >> .env

echo "Cognito resources created successfully!"
echo "Configuration saved to .env file."
