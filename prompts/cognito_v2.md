# Implementing AWS Cognito Authentication for Budget Tracker

## Prompt

```
Implement Login Feature 
Add an AWS Cognito User Pool and User Pool Client via AWS SAM for user authentication. Enable email-based signup and verification.
Create a Flask API endpoint /signup that registers a user to the Cognito User Pool using boto3.
Create a Flask API endpoint /login that authenticates a user using the Cognito User Pool and returns an ID token.
Update existing expense-related API endpoints to require a valid Cognito JWT token in the Authorization header.
```

## Response

I've implemented the login feature with AWS Cognito integration for the Budget Tracker application. Here's what I've done:

### 1. Updated the SAM Template with Cognito Resources

Added AWS Cognito User Pool and User Pool Client to the template.yaml file:
- Created a Cognito User Pool with email verification
- Added a User Pool Client for application authentication
- Updated IAM permissions to allow the application to interact with Cognito
- Added environment variables to pass Cognito configuration to the container

### 2. Created an Authentication Service

Implemented `auth_service.py` with the following features:
- User registration with email verification
- Login functionality that returns JWT tokens
- Token verification and validation
- Password reset flow
- Logout functionality

### 3. Added Authentication Endpoints to the Flask API

Added new endpoints to handle authentication:
- `/signup` - Register a new user
- `/verify` - Verify email with confirmation code
- `/login` - Authenticate and get tokens
- `/logout` - Invalidate tokens
- `/forgot-password` - Request password reset
- `/reset-password` - Set new password with reset code

### 4. Protected Existing Endpoints

Added token validation to all expense-related endpoints:
- Created a `@token_required` decorator that:
  - Extracts the JWT token from the Authorization header
  - Verifies the token's signature and expiration
  - Adds user information to the request object
  - Returns 401 Unauthorized if the token is invalid

### 5. Updated Dependencies

Added required packages to requirements.txt:
- pyjwt - For JWT token validation
- cryptography - For handling RSA keys
- requests - For fetching JWKS (JSON Web Key Set)

## Implementation Details

### 1. AWS SAM Template Updates

The AWS SAM template was updated to include:

- **Cognito User Pool**: Configured with email verification and secure password policies
- **Cognito User Pool Client**: Set up for user authentication with appropriate OAuth flows
- **IAM Permissions**: Added necessary permissions for the application to interact with Cognito
- **Environment Variables**: Passed Cognito configuration to the container

```yaml
# Cognito User Pool
BudgetTrackerUserPool:
  Type: AWS::Cognito::UserPool
  Properties:
    UserPoolName: !Ref UserPoolName
    AutoVerifiedAttributes:
      - email
    UsernameAttributes:
      - email
    VerificationMessageTemplate:
      DefaultEmailOption: CONFIRM_WITH_CODE
      EmailMessage: 'Your verification code is {####}'
      EmailSubject: 'Budget Tracker - Verification Code'
    # ... additional configuration ...

# Cognito User Pool Client
BudgetTrackerUserPoolClient:
  Type: AWS::Cognito::UserPoolClient
  Properties:
    ClientName: !Ref UserPoolClientName
    UserPoolId: !Ref BudgetTrackerUserPool
    GenerateSecret: false
    ExplicitAuthFlows:
      - ALLOW_USER_PASSWORD_AUTH
      - ALLOW_REFRESH_TOKEN_AUTH
    # ... additional configuration ...
```

### 2. Authentication Service Implementation

Created a dedicated `auth_service.py` module to handle all authentication-related functionality:

```python
class AuthService:
    """
    Service for handling user authentication with AWS Cognito.
    """
    
    def __init__(self, user_pool_id=None, client_id=None, region=None):
        # Initialize with configuration from environment variables or parameters
        
    def register_user(self, email: str, password: str) -> Dict[str, Any]:
        # Register a new user in Cognito
        
    def verify_user(self, email: str, verification_code: str) -> Dict[str, Any]:
        # Verify a user's email with the verification code
        
    def login(self, email: str, password: str) -> Dict[str, Any]:
        # Authenticate a user and get tokens
        
    def verify_token(self, token: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
        # Verify a JWT token from Cognito
        
    # ... additional authentication methods ...
```

### 3. Flask API Authentication Endpoints

Added new endpoints to the Flask application for user authentication:

```python
@app.route('/signup', methods=['POST'])
def signup():
    # Register a new user
    
@app.route('/verify', methods=['POST'])
def verify():
    # Verify a user's email with verification code
    
@app.route('/login', methods=['POST'])
def login():
    # Authenticate a user and get tokens
    
@app.route('/logout', methods=['POST'])
@token_required
def logout():
    # Log out a user by invalidating their tokens
    
@app.route('/forgot-password', methods=['POST'])
def forgot_password():
    # Initiate the forgot password flow
    
@app.route('/reset-password', methods=['POST'])
def reset_password():
    # Complete the forgot password flow
```

### 4. Token Validation Decorator

Implemented a decorator to protect API endpoints:

```python
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        if auth_header:
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({'error': 'Authentication token is missing'}), 401
        
        # Verify token
        is_valid, claims = auth_service.verify_token(token)
        if not is_valid:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        # Add user info to request
        request.user = auth_service.get_user_from_token(token)
        
        return f(*args, **kwargs)
    
    return decorated
```

### 5. Securing Existing Endpoints

Applied the `@token_required` decorator to all expense-related endpoints:

```python
@app.route('/expense', methods=['POST'])
@token_required
def add_expense():
    # ...

@app.route('/expense/<expense_id>', methods=['PUT'])
@token_required
def update_expense(expense_id):
    # ...

@app.route('/expense/<expense_id>', methods=['DELETE'])
@token_required
def delete_expense(expense_id):
    # ...

@app.route('/expense', methods=['GET'])
@token_required
def get_expenses():
    # ...

@app.route('/balance', methods=['GET'])
@token_required
def get_balance():
    # ...

@app.route('/summary', methods=['GET'])
@token_required
def get_summary():
    # ...
```

## Implementation Decisions and Reasoning

### 1. Using AWS Cognito

AWS Cognito was chosen for authentication because:
- It provides a fully managed user directory
- Handles secure password storage and management
- Offers built-in features like email verification and password reset
- Integrates well with other AWS services
- Scales automatically with the application

### 2. JWT Token Validation

JWT tokens were chosen for API authentication because:
- They are stateless, reducing backend storage requirements
- They contain user information that can be verified without database lookups
- They have built-in expiration mechanisms
- They are an industry standard for API authentication

### 3. Token Verification Process

The token verification process:
1. Extracts the JWT from the Authorization header
2. Verifies the token signature using Cognito's JSON Web Key Set (JWKS)
3. Validates token expiration and issuer
4. Extracts user information from the token claims

### 4. Security Considerations

Several security best practices were implemented:
- Email verification is required for new accounts
- Strong password policies are enforced
- Tokens have a limited lifetime
- All authentication endpoints use HTTPS
- Failed login attempts are handled securely
- User IDs are not exposed in URLs or responses

## Testing the Authentication System

To test the authentication system:

1. **User Registration**:
   ```bash
   curl -X POST http://localhost:5000/signup \
     -H "Content-Type: application/json" \
     -d '{
       "email": "user@example.com",
       "password": "SecurePassword123"
     }'
   ```

2. **Email Verification**:
   ```bash
   curl -X POST http://localhost:5000/verify \
     -H "Content-Type: application/json" \
     -d '{
       "email": "user@example.com",
       "code": "123456"
     }'
   ```

3. **User Login**:
   ```bash
   curl -X POST http://localhost:5000/login \
     -H "Content-Type: application/json" \
     -d '{
       "email": "user@example.com",
       "password": "SecurePassword123"
     }'
   ```

4. **Using the Token**:
   ```bash
   curl -X GET http://localhost:5000/expense \
     -H "Authorization: Bearer YOUR_TOKEN_HERE"
   ```

## Next Steps

1. **User Management UI**: Develop frontend components for registration, login, and password reset
2. **Role-Based Access Control**: Implement different user roles (admin, regular user)
3. **Social Login**: Add support for login with Google, Facebook, etc.
4. **Multi-Factor Authentication**: Enhance security with MFA options
5. **User Profile Management**: Allow users to update their profile information
