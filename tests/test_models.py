# tests/test_models.py

"""
Unit tests for database models.

This module contains a collection of unit tests that cover various aspects of the database models
used in the CashFlow application. The tests ensure the correctness and reliability of all models.

Note:
    These tests are designed to be executed using the unittest framework.

Classes:
    TestModels: A class containing unit tests for database models.
"""

import unittest
from app import app, db
from models import *
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, timedelta, time


class TestModels(unittest.TestCase):
    """
    A class containing unit tests for database models.

    This class contains a set of test methods that cover various aspects of the database models,
    including User, IncomeType, Income, Expense, CashIn, and CashOut.

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
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
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

    def test_user_model(self):
        """
        Test User model.

        This method creates a User instance, adds it to the database, and then retrieves it.
        It also checks whether the password is hashed correctly and can be verified.
        """
        with app.app_context():
            first_name='test_user'
            last_name='test_user'
            password = 'test_password'
            email = 'test@example.com'
            password_hash = generate_password_hash(password)

            user = User(first_name=first_name, last_name=last_name, password=password_hash, email=email)
            db.session.add(user)
            db.session.commit()

            retrieved_user = User.query.filter_by(email=email).first()
            self.assertIsNotNone(retrieved_user)
            self.assertEqual(retrieved_user.first_name, 'test_user')
            self.assertEqual(retrieved_user.last_name, 'test_user')
            self.assertEqual(retrieved_user.email, 'test@example.com')
            self.assertEqual(retrieved_user.password, password_hash)
            self.assertTrue(check_password_hash(retrieved_user.password, password))

    def test_income_type_model(self):
        """
        Test IncomeType model.

        This method creates an IncomeType instance, adds it to the database, and then retrieves it.
        """
        with app.app_context():
            income_type = IncomeType(name='Salary')
            db.session.add(income_type)
            db.session.commit()

            retrieved_income_type = IncomeType.query.filter_by(name='Salary').first()
            self.assertIsNotNone(retrieved_income_type)
            self.assertEqual(retrieved_income_type.name, 'Salary')
            

    def test_income_model(self):
        """
        Test Income model.

        This method creates an Income instance, adds it to the database, and then retrieves it.
        """
        with app.app_context():
            user = User(first_name='user1', last_name='user1', password='password1', email='user1@example.com')
            db.session.add(user)
            db.session.commit()

            income_type = IncomeType(name='Salary')
            db.session.add(income_type)
            db.session.commit()

            income = Income(user_id=user.id, name='Monthly Salary', income_type_id=income_type.id)
            db.session.add(income)
            db.session.commit()

            retrieved_income = Income.query.filter_by(name='Monthly Salary').first()
            self.assertIsNotNone(retrieved_income)
            self.assertEqual(retrieved_income.name, 'Monthly Salary')
            

    def test_expense_model(self):
        """
        Test Expense model.

        This method creates an Expense instance, adds it to the database, and then retrieves it.
        """
        with app.app_context():
            user = User(first_name='user2', last_name='user2', password='password2', email='user2@example.com')
            db.session.add(user)
            db.session.commit()

            expense = Expense(user_id=user.id, name='Rent')
            db.session.add(expense)
            db.session.commit()

            retrieved_expense = Expense.query.filter_by(name='Rent').first()
            self.assertIsNotNone(retrieved_expense)
            self.assertEqual(retrieved_expense.name, 'Rent')

    def test_cash_in_model(self):
        """
        Test CashIn model.

        This method creates a CashIn instance, adds it to the database, and then retrieves it.
        """
        with app.app_context():
            user = User(first_name='user3', last_name='user3', password='password3', email='user3@example.com')
            db.session.add(user)
            db.session.commit()

            income_type = IncomeType(name='Salary')
            db.session.add(income_type)
            db.session.commit()

            income = Income(user_id=user.id, name='Monthly Salary', income_type_id=income_type.id)
            db.session.add(income)
            db.session.commit()

            cash_in = CashIn(user_id=user.id, income_id=income.id, amount=1000.00, date=datetime(2023, 10, 2))
            db.session.add(cash_in)
            db.session.commit()

            retrieved_cash_in = CashIn.query.filter_by(amount=1000.00).first()
            self.assertIsNotNone(retrieved_cash_in)
            self.assertEqual(retrieved_cash_in.user_id, user.id)
            self.assertEqual(retrieved_cash_in.income_id, income.id)
            self.assertEqual(retrieved_cash_in.amount, 1000.00)
            #self.assertEqual(retrieved_cash_in.date.date(), datetime(2023, 10, 2).date())

    def test_cash_out_model(self):
        """
        Test CashOut model.

        This method creates a CashOut instance, adds it to the database, and then retrieves it.
        """
        with app.app_context():
            user = User(first_name='user4', last_name='user4', password='password4', email='user4@example.com')
            db.session.add(user)
            db.session.commit()

            expense = Expense(user_id=user.id, name='Groceries')
            db.session.add(expense)
            db.session.commit()

            cash_out = CashOut(user_id=user.id, amount=150.00, expense_id=expense.id, date=datetime(2023, 10, 2))
            db.session.add(cash_out)
            db.session.commit()

            retrieved_cash_out = CashOut.query.filter_by(amount=150.00).first()
            self.assertIsNotNone(retrieved_cash_out)
            self.assertEqual(retrieved_cash_out.user_id, user.id)
            self.assertEqual(retrieved_cash_out.expense_id, expense.id)
            self.assertEqual(retrieved_cash_out.amount, 150.00)
            #self.assertEqual(retrieved_cash_out.date.date(), datetime(2023, 10, 2).date())

    def test_budget_model(self):
        """
        Test the Budget model and its relationships.

        - Create a Budget and retrieve it.
        - Verify the Budget Expenses relationship.
        - Deleting an Expense deletes the corresponding BudgetExpense.
        - Deleting a Budget does not delete the associated User.
        - Verify the string representation of Budget.
        - Create multiple Budgets for different months.
        """
        with app.app_context():
            user = User(first_name='user5', last_name='user5', password='password5', email='user5@example.com')
            db.session.add(user)
            db.session.commit()

            # Test 1: Create a Budget and Retrieve it
            budget = Budget(user_id=user.id, year=2023, month=8)
            db.session.add(budget)
            db.session.commit()

            retrieved_budget = Budget.query.filter_by(year=2023, month=8).first()
            self.assertIsNotNone(retrieved_budget)

            # Test 3: Verify Budget Expenses Relationship
            expense1 = Expense(user_id=user.id, name='Expense 1')
            db.session.add(expense1)
            db.session.commit()

            budget_expense1 = BudgetExpense(budget_id=budget.id, expense_id=expense1.id, expected_amount=500.00)
            db.session.add(budget_expense1)
            db.session.commit()

            self.assertEqual(len(budget.expenses), 1)

            # Test 4: Deleting an Expense Deletes Corresponding BudgetExpense
            db.session.delete(expense1)
            db.session.commit()

            self.assertEqual(len(budget.expenses), 0)

            # Test 5: Deleting a Budget Does Not Delete Associated User
            user_id = budget.user_id
            db.session.delete(budget)
            db.session.commit()

            retrieved_user = db.session.get(User, user_id)
            self.assertIsNotNone(retrieved_user)

            # Test 6: Verifying String Representation of Budget
            expected_repr = f"<Budget 2023-8 for User {user_id}>"
            self.assertEqual(retrieved_budget.__repr__(), expected_repr)

            # Test 7: Creating Multiple Budgets for Different Months
            budget2 = Budget(user_id=user.id, year=2023, month=9)
            db.session.add(budget2)
            budget3 = Budget(user_id=user.id, year=2023, month=10)
            db.session.add(budget3)
            db.session.commit()

            retrieved_budget2 = Budget.query.filter_by(year=2023, month=9).first()
            retrieved_budget3 = Budget.query.filter_by(year=2023, month=10).first()
            self.assertIsNotNone(retrieved_budget2)
            self.assertIsNotNone(retrieved_budget3)


    def test_budget_expense_model(self):
        """
        Test the BudgetExpense model and its relationships.

        - Create a Budget, Expense, and BudgetExpense.
        - Retrieving a BudgetExpense.
        - Creating multiple Expenses for a Budget.
        - Create BudgetExpense instances for different Budgets.
        - Updating spent_amount for a BudgetExpense.
        - Cascading Delete on Expense Instance.
        - Cascading Delete on Budget Instance.
        """
        with app.app_context():
            user = User(first_name='user6', last_name='user6', password='password6', email='user6@example.com')
            db.session.add(user)
            db.session.commit()

            budget = Budget(user_id=user.id, year=2023, month=8)
            db.session.add(budget)
            db.session.commit()

            expense = Expense(user_id=user.id, name='Rent')
            db.session.add(expense)
            db.session.commit()

            budget_expense = BudgetExpense(budget_id=budget.id, expense_id=expense.id, expected_amount=1000.00)
            db.session.add(budget_expense)
            db.session.commit()

            # Test: Retrieving BudgetExpense
            retrieved_budget_expense = BudgetExpense.query.filter_by(budget_id=budget.id, expense_id=expense.id,expected_amount=1000.00).first()
            self.assertIsNotNone(retrieved_budget_expense)

            # Test: Creating Multiple Expenses for a Budget
            expense2 = Expense(user_id=user.id, name='Utilities')
            db.session.add(expense2)
            db.session.commit()

            budget_expense2 = BudgetExpense(budget_id=budget.id, expense_id=expense2.id, expected_amount=800.00)
            db.session.add(budget_expense2)
            db.session.commit()

            self.assertEqual(len(budget.expenses), 2)

            # Test: Create BudgetExpense Instances for Different Budgets
            budget2 = Budget(user_id=user.id, year=2023, month=9)
            db.session.add(budget2)
            db.session.commit()

            budget5 = Budget(user_id=user.id, year=2023, month=11)
            db.session.add(budget5)
            db.session.commit()

            expense9 = Expense(user_id=user.id, name='Entertainment')
            db.session.add(expense9)
            db.session.commit()

            budget_expense3 = BudgetExpense(budget_id=budget2.id, expense_id=expense9.id, expected_amount=600.00)
            db.session.add(budget_expense3)
            db.session.commit()

            budget_expense5 = BudgetExpense(budget_id=budget5.id, expense_id=expense9.id, expected_amount=200.00)
            db.session.add(budget_expense5)
            db.session.commit()

            self.assertEqual(len(expense9.budget_expenses), 2)

            # Test: Updating spent_amount for a BudgetExpense
            budget_expense.spent_amount = 600.00
            db.session.commit()

            updated_budget_expense = db.session.get(BudgetExpense, budget_expense.id)
            self.assertEqual(updated_budget_expense.spent_amount, 600.00)

            # Test: Cascading Delete on Expense Instance
            expense4 = Expense(user_id=user.id, name='Expense 4')
            db.session.add(expense4)
            db.session.commit()

            budget_expense4 = BudgetExpense(budget_id=budget.id, expense_id=expense4.id, expected_amount=400.00)
            db.session.add(budget_expense4)
            db.session.commit()

            db.session.delete(expense4)
            db.session.commit()

            retrieved_budget_expense4 = db.session.get(BudgetExpense, budget_expense4.id)
            self.assertIsNone(retrieved_budget_expense4)

            # Test: Cascading Delete on Budget Instance
            db.session.delete(budget)
            db.session.commit()

            retrieved_budget_expense = db.session.get(BudgetExpense, budget_expense.id)
            self.assertIsNone(retrieved_budget_expense)

    def test_debt_model(self):
        """
        Test Debt model.

        This method creates a Debt instance, adds it to the database, and then retrieves it.
        """

        from models import Debt
        with app.app_context():
            user = User(first_name='user7', last_name='user7', password='password7', email='user7@example.com')
            db.session.add(user)
            db.session.commit()

            due_date = datetime.utcnow() + timedelta(days=30)  # Set due date to 30 days from now

            debt = Debt(user_id=user.id, creditor='Lender Inc.', amount=1000.00, date_taken=datetime.utcnow(),
                        description='Loan for car', date_due=due_date)
            db.session.add(debt)
            db.session.commit()

            retrieved_debt = Debt.query.filter_by(creditor='Lender Inc.', user_id=user.id).first()
            self.assertIsNotNone(retrieved_debt)

    def test_credit_model(self):
        """
        Test Credit model.

        This method creates a Credit instance, adds it to the database, and then retrieves it.
        """
        from models import Credit
        with app.app_context():
            user = User(first_name='user8', last_name='user8', password='password8', email='user8@example.com')
            db.session.add(user)
            db.session.commit()

            due_date = datetime.utcnow() + timedelta(days=30)  # Set due date to 30 days from now

            credit = Credit(user_id=user.id, debtor='Cardholder Ltd.', amount=500.00, date_taken=datetime.utcnow(),
                            description='Payment for services', date_due=due_date)
            db.session.add(credit)
            db.session.commit()

            retrieved_credit = Credit.query.filter_by(debtor='Cardholder Ltd.', user_id=user.id).first()
            self.assertIsNotNone(retrieved_credit)

    def test_creditor_payment_model(self):
        """
        Test CreditorPayment model.
        """
        with app.app_context():
            user = User(first_name='user9', last_name='user9', password='password9', email='user9@example.com')
            db.session.add(user)
            db.session.commit()

            debt = Debt(user_id=user.id, creditor='Lender Inc.', amount=1000.00, date_taken=datetime.utcnow())
            db.session.add(debt)
            db.session.commit()

            creditor_payment = CreditorPayment(debt_id=debt.id, amount=500.00, date=datetime(2023, 10, 2))
            db.session.add(creditor_payment)
            db.session.commit()

            retrieved_creditor_payment = CreditorPayment.query.filter_by(amount=500.00).first()
            self.assertIsNotNone(retrieved_creditor_payment)
            self.assertEqual(retrieved_creditor_payment.debt_id, debt.id)

    def test_debtor_payment_model(self):
        """
        Test DebtorPayment model.
        """
        with app.app_context():
            user = User(first_name='user10', last_name='user10', password='password10', email='user10@example.com')
            db.session.add(user)
            db.session.commit()

            credit = Credit(user_id=user.id, debtor='Cardholder Ltd.', amount=500.00, date_taken=datetime.utcnow())
            db.session.add(credit)
            db.session.commit()

            debtor_payment = DebtorPayment(credit_id=credit.id, amount=250.00, date=datetime(2023, 10, 2))
            db.session.add(debtor_payment)
            db.session.commit()

            retrieved_debtor_payment = DebtorPayment.query.filter_by(amount=250.00).first()
            self.assertIsNotNone(retrieved_debtor_payment)
            self.assertEqual(retrieved_debtor_payment.credit_id, credit.id)

if __name__ == '__main__':
    unittest.main()
