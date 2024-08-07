# tests/test_transactions.py

import unittest
from app import app, db
from transactions import add_income, add_expense, create_budget
from models import User, IncomeType, Income, Expense, Budget, BudgetExpense, CashOut
from datetime import datetime

class TestTransactions(unittest.TestCase):

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

    def test_add_income(self):
        """
        Test adding an income transaction.

        This test creates a user, an income type, and then adds an income transaction for the user.
        It checks if the income transaction was added correctly to the database.

        """
        with app.app_context():
            # Add a user and an income type
            user = User(first_name='test_user', last_name='test_user', password='test_password', email='test@example.com')
            db.session.add(user)
            db.session.commit()
            income_type = IncomeType(name="Salary")
            db.session.add(income_type)
            db.session.commit()

            # Add an income transaction
            result = add_income(user.id, "Monthly Salary", income_type.id)
            self.assertTrue(result)

            # Check if the income transaction was added
            income = Income.query.first()
            self.assertIsNotNone(income)
            self.assertEqual(income.name, "Monthly Salary")
            self.assertEqual(income.income_type_id, income_type.id)

    def test_add_expense(self):
        """
        Test adding an expense transaction.

        This test creates a user and then adds an expense transaction for the user.
        It checks if the expense transaction was added correctly to the database.

        """
        with app.app_context():
        # Add a user
            user = User(first_name='test_user', last_name='test_user', password='test_password', email='test@example.com')
            db.session.add(user)
            db.session.commit()

            # Add an expense transaction
            result = add_expense(user.id, "Groceries")
            self.assertTrue(result)

            # Check if the expense transaction was added
            expense = Expense.query.first()
            self.assertIsNotNone(expense)
        self.assertEqual(expense.name, "Groceries")

    def test_create_budget(self):
        """
        Test creating a budget for a user.
        """
        with app.app_context():
            # Add a user
            user = User(first_name='test_user', last_name='test_user', password='test_password', email='test@example.com')
            db.session.add(user)
            db.session.commit()

            # Create a budget for the user
            result = create_budget(user.id, 2023, 8)
            self.assertIsInstance(result, Budget)

            # Check if the budget was created
            budget = Budget.query.first()
            self.assertIsNotNone(budget)
            self.assertEqual(budget.user_id, user.id)
            self.assertEqual(budget.year, 2023)
            self.assertEqual(budget.month, 8)

            # Attempt to create a duplicate budget for the same month
            result_duplicate = create_budget(user.id, 2023, 8)
            self.assertEqual(result_duplicate, 'A budget already exists for this year and month.')


if __name__ == "__main__":
    unittest.main()
