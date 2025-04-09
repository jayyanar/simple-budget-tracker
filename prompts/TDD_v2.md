# Test-Driven Development (TDD) for Budget Tracker v2

## Prompt

```
Create a TDD approach for implementing authentication, data persistence with DynamoDB, and export functionality for the Budget Tracker v2. Include test cases for user registration, login, token validation, and protected routes.
```

## Response

This document outlines the test-driven development approach for the enhanced Budget Tracker application, including authentication, data persistence with DynamoDB, and export functionality.

## Part 1: Authentication Tests

```python
import unittest
import json
from unittest.mock import patch, MagicMock
from src.app import app
from src.auth_service import AuthService
from src.budget_tracker import BudgetTracker

class TestAuthentication(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        # Mock the Cognito client
        self.cognito_patcher = patch('src.auth_service.boto3.client')
        self.mock_cognito = self.cognito_patcher.start()
        self.mock_client = MagicMock()
        self.mock_cognito.return_value = self.mock_client
        
    def tearDown(self):
        self.cognito_patcher.stop()
    
    def test_user_registration(self):
        """Test user registration functionality"""
        # Mock successful registration
        self.mock_client.sign_up.return_value = {
            'UserConfirmed': False,
            'UserSub': 'test-user-id'
        }
        
        response = self.app.post('/auth/register', 
            json={
                'email': 'user@example.com',
                'password': 'SecurePass123'
            }
        )
        
        # Assert response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('message', data)
        self.assertIn('verification required', data['message'].lower())
        
        # Verify Cognito client was called correctly
        self.mock_client.sign_up.assert_called_with(
            ClientId='mock-client-id',
            Username='user@example.com',
            Password='SecurePass123',
            UserAttributes=[{'Name': 'email', 'Value': 'user@example.com'}]
        )
    
    def test_user_registration_weak_password(self):
        """Test registration with weak password"""
        # Mock password policy failure
        self.mock_client.sign_up.side_effect = Exception('Password does not conform to policy')
        
        response = self.app.post('/auth/register', 
            json={
                'email': 'user@example.com',
                'password': 'weak'
            }
        )
        
        # Assert response
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('password', data['error'].lower())
    
    def test_email_verification(self):
        """Test email verification functionality"""
        # Mock successful verification
        self.mock_client.confirm_sign_up.return_value = {}
        
        response = self.app.post('/auth/verify', 
            json={
                'email': 'user@example.com',
                'code': '123456'
            }
        )
        
        # Assert response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('message', data)
        self.assertIn('verified', data['message'].lower())
        
        # Verify Cognito client was called correctly
        self.mock_client.confirm_sign_up.assert_called_with(
            ClientId='mock-client-id',
            Username='user@example.com',
            ConfirmationCode='123456'
        )
    
    def test_user_login(self):
        """Test user login functionality"""
        # Mock successful authentication
        self.mock_client.initiate_auth.return_value = {
            'AuthenticationResult': {
                'IdToken': 'mock-id-token',
                'AccessToken': 'mock-access-token',
                'RefreshToken': 'mock-refresh-token'
            }
        }
        
        response = self.app.post('/auth/login', 
            json={
                'email': 'user@example.com',
                'password': 'SecurePass123'
            }
        )
        
        # Assert response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('token', data)
        self.assertEqual(data['token'], 'mock-id-token')
        
        # Verify Cognito client was called correctly
        self.mock_client.initiate_auth.assert_called_with(
            ClientId='mock-client-id',
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': 'user@example.com',
                'PASSWORD': 'SecurePass123'
            }
        )
    
    def test_failed_login(self):
        """Test failed login attempt"""
        # Mock authentication failure
        self.mock_client.initiate_auth.side_effect = Exception('Incorrect username or password')
        
        response = self.app.post('/auth/login', 
            json={
                'email': 'user@example.com',
                'password': 'WrongPassword'
            }
        )
        
        # Assert response
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('invalid', data['error'].lower())
    
    def test_password_reset_request(self):
        """Test password reset request"""
        # Mock successful reset request
        self.mock_client.forgot_password.return_value = {}
        
        response = self.app.post('/auth/forgot-password', 
            json={
                'email': 'user@example.com'
            }
        )
        
        # Assert response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('message', data)
        self.assertIn('reset code', data['message'].lower())
        
        # Verify Cognito client was called correctly
        self.mock_client.forgot_password.assert_called_with(
            ClientId='mock-client-id',
            Username='user@example.com'
        )
    
    def test_password_reset_confirmation(self):
        """Test password reset confirmation"""
        # Mock successful reset confirmation
        self.mock_client.confirm_forgot_password.return_value = {}
        
        response = self.app.post('/auth/reset-password', 
            json={
                'email': 'user@example.com',
                'code': '123456',
                'new_password': 'NewSecurePass123'
            }
        )
        
        # Assert response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('message', data)
        self.assertIn('reset successful', data['message'].lower())
        
        # Verify Cognito client was called correctly
        self.mock_client.confirm_forgot_password.assert_called_with(
            ClientId='mock-client-id',
            Username='user@example.com',
            ConfirmationCode='123456',
            Password='NewSecurePass123'
        )
    
    def test_protected_route_with_valid_token(self):
        """Test accessing protected route with valid token"""
        # Mock token verification
        with patch('src.auth_service.AuthService.verify_token', return_value=True):
            with patch('src.auth_service.AuthService.get_user_from_token', return_value={'email': 'user@example.com'}):
                response = self.app.get('/expense', 
                    headers={'Authorization': 'Bearer mock-token'}
                )
                
                # Assert response
                self.assertEqual(response.status_code, 200)
    
    def test_protected_route_with_invalid_token(self):
        """Test accessing protected route with invalid token"""
        # Mock token verification failure
        with patch('src.auth_service.AuthService.verify_token', return_value=False):
            response = self.app.get('/expense', 
                headers={'Authorization': 'Bearer invalid-token'}
            )
            
            # Assert response
            self.assertEqual(response.status_code, 401)
            data = json.loads(response.data)
            self.assertIn('error', data)
            self.assertIn('unauthorized', data['error'].lower())
    
    def test_logout(self):
        """Test user logout functionality"""
        # Mock successful logout
        self.mock_client.global_sign_out.return_value = {}
        
        response = self.app.post('/auth/logout', 
            headers={'Authorization': 'Bearer mock-token'}
        )
        
        # Assert response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('message', data)
        self.assertIn('logged out', data['message'].lower())
```

## Implementation Notes for Authentication

The authentication tests focus on:

1. **User Registration and Verification**:
   - Testing the sign-up process with valid credentials
   - Handling weak passwords
   - Verifying email with confirmation code

2. **Login and Session Management**:
   - Testing successful login with correct credentials
   - Handling failed login attempts
   - Protecting routes with token verification

3. **Password Management**:
   - Testing password reset request flow
   - Confirming password reset with verification code

4. **Security**:
   - Ensuring protected routes require valid authentication
   - Proper logout functionality

These tests will drive the implementation of the `AuthService` class that will integrate with Amazon Cognito for secure user authentication.
