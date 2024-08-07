# tests/test_auth.py

"""
Unit tests for user authentication functionality.

This module contains unit tests for user authentication related functions,
including user registration, authentication, and password hashing.

Note:
    These tests are designed to be executed using the unittest framework.

Classes:
    TestAuthentication: A class containing unit tests for authentication.
"""

import unittest
from unittest.mock import patch
from app import app, db
from auth import register_user, authenticate_user
from models import User
from werkzeug.security import check_password_hash

class TestAuthentication(unittest.TestCase):
    """
    A class containing unit tests for user authentication functionality.
    
    This class contains a set of test methods that cover user registration,
    authentication, and password hashing.
    
    Attributes:
        app (Flask): A Flask application instance for testing.
    """

    def setUp(self):
        """
        Set up the test environment.
        
        This method configures the Flask app for testing, creates a separate
        in-memory SQLite database, and prepares a test client for making requests.
        """
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'  # Use a separate test database
        self.app = app.test_client()
        with app.app_context():
            db.create_all()

    def tearDown(self):
        """
        Clean up the test environment.
        
        This method removes the test database and resets the app context after each test.
        """
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_register_user(self):
        """
        Test user registration.
        
        This method tests the registration of a user and verifies that the user
        is correctly added to the database.
        """
        with app.app_context():
            result = register_user('Test', 'User', 'test_password', 'test@example.com')  # Correct arguments
            self.assertIsNotNone(result)
            user = User.query.filter_by(email='test@example.com').first()
            self.assertIsNotNone(user)

    def test_authenticate_user(self):
        """
        Test user authentication.
        
        This method tests the authentication of a registered user and verifies
        that the authentication process returns the correct user object.
        """
        with app.app_context():
            register_user('Test', 'User', 'test_password', 'test4@example.com')
            user = authenticate_user('test4@example.com', 'test_password')
            self.assertIsNotNone(user)
            self.assertEqual(user.email, 'test4@example.com')
            self.assertEqual(user.first_name, 'Test')
            self.assertEqual(user.last_name, 'User')
    
    def test_authenticate_nonexistent_user(self):
        """
        Test authentication with a nonexistent user.
        
        This method tests the scenario where a user attempts to authenticate with
        a username that doesn't exist in the database, and verifies that authentication returns None.
        """
        with app.app_context():
            user = authenticate_user('nonexistent_user', 'test_password')
            self.assertIsNone(user)
    
    def test_password_hashing(self):
        """
        Test password hashing.
        
        This method tests whether the passwords are properly hashed during user registration
        and whether the authentication process correctly verifies hashed passwords.
        """
        with app.app_context():
            password='test_password'
            register_user('Test', 'User', password, 'test@example.com')
            user = User.query.filter_by(email='test@example.com').first() 
            self.assertTrue(check_password_hash(user.password, password))

if __name__ == '__main__':
    unittest.main()
