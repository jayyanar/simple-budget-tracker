"""
Tests for authentication features in Budget Tracker v2
"""

import unittest
import json
from unittest.mock import patch, MagicMock
import sys
import os

# Add the src directory to the path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

# Import modules to test - these will be implemented later
try:
    from auth_service import AuthService
except ImportError:
    # Create a placeholder for testing
    class AuthService:
        pass

class TestAuthentication(unittest.TestCase):
    def setUp(self):
        """Set up test environment before each test"""
        # Mock the Cognito client
        self.cognito_patcher = patch('boto3.client')
        self.mock_cognito = self.cognito_patcher.start()
        self.mock_client = MagicMock()
        self.mock_cognito.return_value = self.mock_client
        
        # Create auth service with mock client
        self.auth_service = AuthService(
            user_pool_id='test-pool-id',
            client_id='test-client-id',
            region='us-east-1'
        )
    
    def tearDown(self):
        """Clean up after each test"""
        self.cognito_patcher.stop()
    
    def test_user_registration(self):
        """Test user registration functionality"""
        # Mock successful registration
        self.mock_client.sign_up.return_value = {
            'UserConfirmed': False,
            'UserSub': 'test-user-id'
        }
        
        # Call the register_user method
        result = self.auth_service.register_user(
            email='user@example.com',
            password='SecurePass123'
        )
        
        # Assert result
        self.assertTrue(result['success'])
        self.assertIn('verification required', result['message'].lower())
        self.assertEqual(result['user_id'], 'test-user-id')
        
        # Verify Cognito client was called correctly
        self.mock_client.sign_up.assert_called_with(
            ClientId='test-client-id',
            Username='user@example.com',
            Password='SecurePass123',
            UserAttributes=[{'Name': 'email', 'Value': 'user@example.com'}]
        )
    
    def test_user_login(self):
        """Test user login functionality"""
        # Mock successful authentication
        self.mock_client.initiate_auth.return_value = {
            'AuthenticationResult': {
                'IdToken': 'mock-id-token',
                'AccessToken': 'mock-access-token',
                'RefreshToken': 'mock-refresh-token',
                'ExpiresIn': 3600
            }
        }
        
        # Call the login method
        result = self.auth_service.login(
            email='user@example.com',
            password='SecurePass123'
        )
        
        # Assert result
        self.assertTrue(result['success'])
        self.assertEqual(result['id_token'], 'mock-id-token')
        self.assertEqual(result['access_token'], 'mock-access-token')
        
        # Verify Cognito client was called correctly
        self.mock_client.initiate_auth.assert_called_with(
            ClientId='test-client-id',
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': 'user@example.com',
                'PASSWORD': 'SecurePass123'
            }
        )
    
    def test_verify_token(self):
        """Test token verification"""
        # This is a simplified test since actual JWT verification is complex
        with patch.object(self.auth_service, '_get_jwks', return_value={'keys': []}):
            with patch('jwt.decode', return_value={'sub': 'user-id', 'email': 'user@example.com'}):
                is_valid, claims = self.auth_service.verify_token('mock-token')
                
                # Assert result
                self.assertTrue(is_valid)
                self.assertEqual(claims['sub'], 'user-id')
                self.assertEqual(claims['email'], 'user@example.com')

if __name__ == '__main__':
    unittest.main()
