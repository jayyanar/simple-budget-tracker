"""
Authentication Service for Budget Tracker

This module provides authentication functionality using AWS Cognito.
"""

import os
import boto3
import json
import base64
import time
from typing import Dict, Any, Optional, Tuple
import jwt
from jwt.algorithms import RSAAlgorithm
import requests
from functools import lru_cache

class AuthService:
    """
    Service for handling user authentication with AWS Cognito.
    """
    
    def __init__(self, user_pool_id=None, client_id=None, region=None):
        """
        Initialize the authentication service.
        
        Args:
            user_pool_id: Cognito User Pool ID (defaults to environment variable)
            client_id: Cognito App Client ID (defaults to environment variable)
            region: AWS Region (defaults to environment variable)
        """
        self.user_pool_id = user_pool_id or os.environ.get('COGNITO_USER_POOL_ID')
        self.client_id = client_id or os.environ.get('COGNITO_APP_CLIENT_ID')
        self.region = region or os.environ.get('AWS_REGION', 'us-east-1')
        
        if not self.user_pool_id or not self.client_id:
            raise ValueError("Cognito User Pool ID and App Client ID must be provided")
        
        self.cognito_client = boto3.client('cognito-idp', region_name=self.region)
        self.jwks_url = f"https://cognito-idp.{self.region}.amazonaws.com/{self.user_pool_id}/.well-known/jwks.json"
    
    def register_user(self, email: str, password: str) -> Dict[str, Any]:
        """
        Register a new user in the Cognito User Pool.
        
        Args:
            email: User's email address
            password: User's password
            
        Returns:
            Dictionary with registration result
        """
        try:
            response = self.cognito_client.sign_up(
                ClientId=self.client_id,
                Username=email,
                Password=password,
                UserAttributes=[
                    {
                        'Name': 'email',
                        'Value': email
                    }
                ]
            )
            
            return {
                'success': True,
                'message': 'User registration successful. Verification required.',
                'user_id': response['UserSub'],
                'user_confirmed': response['UserConfirmed']
            }
        except self.cognito_client.exceptions.UsernameExistsException:
            return {
                'success': False,
                'error': 'User with this email already exists'
            }
        except self.cognito_client.exceptions.InvalidPasswordException as e:
            return {
                'success': False,
                'error': str(e)
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def verify_user(self, email: str, verification_code: str) -> Dict[str, Any]:
        """
        Verify a user's email with the verification code.
        
        Args:
            email: User's email address
            verification_code: Verification code sent to the user's email
            
        Returns:
            Dictionary with verification result
        """
        try:
            self.cognito_client.confirm_sign_up(
                ClientId=self.client_id,
                Username=email,
                ConfirmationCode=verification_code
            )
            
            return {
                'success': True,
                'message': 'Email verified successfully'
            }
        except self.cognito_client.exceptions.CodeMismatchException:
            return {
                'success': False,
                'error': 'Invalid verification code'
            }
        except self.cognito_client.exceptions.ExpiredCodeException:
            return {
                'success': False,
                'error': 'Verification code has expired'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def login(self, email: str, password: str) -> Dict[str, Any]:
        """
        Authenticate a user and get tokens.
        
        Args:
            email: User's email address
            password: User's password
            
        Returns:
            Dictionary with authentication result and tokens
        """
        try:
            response = self.cognito_client.initiate_auth(
                ClientId=self.client_id,
                AuthFlow='USER_PASSWORD_AUTH',
                AuthParameters={
                    'USERNAME': email,
                    'PASSWORD': password
                }
            )
            
            auth_result = response.get('AuthenticationResult', {})
            
            return {
                'success': True,
                'message': 'Login successful',
                'id_token': auth_result.get('IdToken'),
                'access_token': auth_result.get('AccessToken'),
                'refresh_token': auth_result.get('RefreshToken'),
                'expires_in': auth_result.get('ExpiresIn')
            }
        except self.cognito_client.exceptions.NotAuthorizedException:
            return {
                'success': False,
                'error': 'Invalid username or password'
            }
        except self.cognito_client.exceptions.UserNotConfirmedException:
            return {
                'success': False,
                'error': 'User is not confirmed. Please verify your email.'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def logout(self, access_token: str) -> Dict[str, Any]:
        """
        Log out a user by invalidating their tokens.
        
        Args:
            access_token: User's access token
            
        Returns:
            Dictionary with logout result
        """
        try:
            self.cognito_client.global_sign_out(
                AccessToken=access_token
            )
            
            return {
                'success': True,
                'message': 'Logged out successfully'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def forgot_password(self, email: str) -> Dict[str, Any]:
        """
        Initiate the forgot password flow.
        
        Args:
            email: User's email address
            
        Returns:
            Dictionary with forgot password result
        """
        try:
            self.cognito_client.forgot_password(
                ClientId=self.client_id,
                Username=email
            )
            
            return {
                'success': True,
                'message': 'Password reset code sent to email'
            }
        except self.cognito_client.exceptions.UserNotFoundException:
            return {
                'success': False,
                'error': 'User not found'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def reset_password(self, email: str, code: str, new_password: str) -> Dict[str, Any]:
        """
        Complete the forgot password flow by setting a new password.
        
        Args:
            email: User's email address
            code: Password reset code sent to the user's email
            new_password: New password to set
            
        Returns:
            Dictionary with password reset result
        """
        try:
            self.cognito_client.confirm_forgot_password(
                ClientId=self.client_id,
                Username=email,
                ConfirmationCode=code,
                Password=new_password
            )
            
            return {
                'success': True,
                'message': 'Password reset successful'
            }
        except self.cognito_client.exceptions.CodeMismatchException:
            return {
                'success': False,
                'error': 'Invalid reset code'
            }
        except self.cognito_client.exceptions.ExpiredCodeException:
            return {
                'success': False,
                'error': 'Reset code has expired'
            }
        except self.cognito_client.exceptions.InvalidPasswordException as e:
            return {
                'success': False,
                'error': str(e)
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    @lru_cache(maxsize=1)
    def _get_jwks(self) -> Dict[str, Any]:
        """
        Get the JSON Web Key Set (JWKS) from Cognito.
        
        Returns:
            Dictionary containing the JWKS
        """
        response = requests.get(self.jwks_url)
        return response.json()
    
    def verify_token(self, token: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Verify a JWT token from Cognito.
        
        Args:
            token: JWT token to verify
            
        Returns:
            Tuple of (is_valid, claims)
        """
        try:
            # Get the key ID from the token header
            header = jwt.get_unverified_header(token)
            kid = header['kid']
            
            # Find the corresponding public key in the JWKS
            jwks = self._get_jwks()
            key = None
            for k in jwks['keys']:
                if k['kid'] == kid:
                    key = k
                    break
            
            if not key:
                return False, None
            
            # Convert the JWK to a PEM format that PyJWT can use
            public_key = RSAAlgorithm.from_jwk(json.dumps(key))
            
            # Verify the token
            claims = jwt.decode(
                token,
                public_key,
                algorithms=['RS256'],
                options={
                    'verify_signature': True,
                    'verify_exp': True,
                    'verify_iat': True,
                    'verify_aud': False,  # Skip audience verification
                },
                issuer=f"https://cognito-idp.{self.region}.amazonaws.com/{self.user_pool_id}"
            )
            
            return True, claims
        except jwt.ExpiredSignatureError:
            return False, {'error': 'Token has expired'}
        except jwt.InvalidTokenError:
            return False, {'error': 'Invalid token'}
        except Exception as e:
            return False, {'error': str(e)}
    
    def get_user_from_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Extract user information from a verified token.
        
        Args:
            token: JWT token
            
        Returns:
            Dictionary with user information or None if token is invalid
        """
        is_valid, claims = self.verify_token(token)
        
        if not is_valid or not claims:
            return None
        
        # Extract relevant user information
        return {
            'user_id': claims.get('sub'),
            'email': claims.get('email'),
            'email_verified': claims.get('email_verified', False)
        }
