# tests/ test_calculations.py
"""
Unit tests for calculation functions.

This module contains unit tests for the calculation functions used in the FinancialTracker application.
The tests cover various calculations related to income, expenses, and financial summaries.

Note:
    These tests are designed to be executed using the unittest framework.

Classes:
    TestCalculation: A class containing unit tests for calculation functions.
"""

import unittest
from sqlalchemy.orm.exc import NoResultFound
from decimal import Decimal, ROUND_HALF_UP
from datetime import date, timedelta
from app import app, db
from calculations import (
    calculate_total_income_between_dates,
    calculate_total_expenses_between_dates,
    calculate_total_income,
    calculate_total_expenses,
    calculate_savings_between_dates,
    calculate_expense_percentage_of_income,
)
from models import User, IncomeType, Income, Expense, CashIn, CashOut
from auth import register_user, authenticate_user

class TestCalculation(unittest.TestCase):
    """
    A class containing unit tests for calculation functions.

    This class contains a set of test methods that cover the calculation functions used in the
    FinancialTracker application.

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

    def test_calculate_total_income_between_dates(self):
        """
        Test the calculate_total_income_between_dates function.

        This method tests whether the function accurately calculates the total income for a user within specified dates,
        and also verifies the correctness of individual income transactions returned by the function.
        """
        with app.app_context():
            # Step 1: Add a User
            user = User(first_name='test_user', last_name='test_user', password='test_password', email='test@example.com')
            db.session.add(user)
            db.session.commit()

            # Step 2: Add IncomeTypes and Incomes
            income_type1 = IncomeType(name='Salary')
            income_type2 = IncomeType(name='Freelance')
            db.session.add_all([income_type1, income_type2])
            db.session.commit()

            income1 = Income(user_id=user.id, name='Monthly Salary', income_type_id=income_type1.id)
            income2 = Income(user_id=user.id, name='Project Payment', income_type_id=income_type2.id)
            db.session.add_all([income1, income2])
            db.session.commit()

            # Step 3: Add CashIn entries over a period of time from different Incomes
            today = date.today()
            cash_in1 = CashIn(user_id=user.id, income_id=income1.id, amount=1000.00, date=today - timedelta(days=10))
            cash_in2 = CashIn(user_id=user.id, income_id=income2.id, amount=500.00, date=today - timedelta(days=5))
            cash_in3 = CashIn(user_id=user.id, income_id=income1.id, amount=750.00, date=today - timedelta(days=2))
            db.session.add_all([cash_in1, cash_in2, cash_in3])
            db.session.commit()

            # Step 4: Test with specified dates
            start_date = today - timedelta(days=7)
            end_date = today
            cash_incomes = CashIn.query.filter(
                CashIn.user_id == user.id,
                CashIn.date >= start_date,
                CashIn.date <= end_date
            ).all()

            total_income = sum(cash_in.amount for cash_in in cash_incomes)
            total_income = Decimal(total_income).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

            calculated_total_income, individual_incomes = calculate_total_income_between_dates(user.id, start_date, end_date)
            
            # Check the calculated total income
            self.assertEqual(calculated_total_income, total_income)

            # Check individual incomes
            self.assertEqual(len(individual_incomes), len(cash_incomes))
            for calculated_income, original_cash_in in zip(individual_incomes, cash_incomes):
                # Retrieve the associated income for the cash_in
                income = db.session.get(Income, original_cash_in.income_id)
                
                self.assertEqual(calculated_income['amount'], original_cash_in.amount)
                self.assertEqual(calculated_income['date'], original_cash_in.date)
                self.assertEqual(calculated_income['name'], income.name)
                
                # Retrieve the associated income type for the income
                income_type = db.session.get(IncomeType, income.income_type_id)
                self.assertEqual(calculated_income['income_type'], income_type.name)

            # Step 5: Test with None dates
            today = date.today()
            start_date_none = date(today.year, today.month, 1)
            end_date_none = today
            cash_incomes_none = CashIn.query.filter(
                CashIn.user_id == user.id,
                CashIn.date >= start_date_none,
                CashIn.date <= end_date_none
            ).all()

            total_income_none = sum(cash_in.amount for cash_in in cash_incomes_none)
            total_income_none = Decimal(total_income_none).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

            calculated_total_income_none, individual_incomes_none = calculate_total_income_between_dates(user.id, None, None)

            # Check the calculated total income
            self.assertEqual(calculated_total_income_none, total_income_none)

            # Check individual incomes
            self.assertEqual(len(individual_incomes_none), len(cash_incomes_none))
            for calculated_income, original_cash_in in zip(individual_incomes_none, cash_incomes_none):
                # Retrieve the associated income for the cash_in
                income = db.session.get(Income, original_cash_in.income_id)
                
                self.assertEqual(calculated_income['amount'], original_cash_in.amount)
                self.assertEqual(calculated_income['date'], original_cash_in.date)
                self.assertEqual(calculated_income['name'], income.name)
                
                # Retrieve the associated income type for the income
                income_type = db.session.get(IncomeType, income.income_type_id)
                self.assertEqual(calculated_income['income_type'], income_type.name)

            # Test with no transactions within specified dates
            calculated_total_income_empty, individual_incomes_empty = calculate_total_income_between_dates(user.id, today, today)
            self.assertEqual(calculated_total_income_empty, Decimal('0.00'))
            self.assertEqual(len(individual_incomes_empty), 0)

            # Test transactions exactly on start and end dates
            cash_in_same_day = CashIn(user_id=user.id, income_id=income1.id, amount=200.00, date=today)
            db.session.add(cash_in_same_day)
            db.session.commit()
            calculated_total_income_same_day, individual_incomes_same_day = calculate_total_income_between_dates(user.id, today, today)
            self.assertEqual(calculated_total_income_same_day, Decimal('200.00'))
            self.assertEqual(len(individual_incomes_same_day), 1)
            self.assertEqual(individual_incomes_same_day[0]['amount'], cash_in_same_day.amount)
            self.assertEqual(individual_incomes_same_day[0]['date'], cash_in_same_day.date)

            # Test multiple transactions on the same date
            cash_in_same_day_2 = CashIn(user_id=user.id, income_id=income1.id, amount=300.00, date=today)
            db.session.add(cash_in_same_day_2)
            db.session.commit()
            calculated_total_income_multiple, individual_incomes_multiple = calculate_total_income_between_dates(user.id, today, today)
            expected_total_income_multiple = cash_in_same_day.amount + cash_in_same_day_2.amount
            self.assertEqual(calculated_total_income_multiple, expected_total_income_multiple)
            self.assertEqual(len(individual_incomes_multiple), 2)
            self.assertEqual(individual_incomes_multiple[0]['amount'], cash_in_same_day.amount)
            self.assertEqual(individual_incomes_multiple[0]['date'], cash_in_same_day.date)
            self.assertEqual(individual_incomes_multiple[1]['amount'], cash_in_same_day_2.amount)
            self.assertEqual(individual_incomes_multiple[1]['date'], cash_in_same_day_2.date)

            # Test with invalid inputs (non-existent user ID)
            calculated_total_income_invalid_user, _ = calculate_total_income_between_dates(-1, start_date, end_date)
            self.assertEqual(calculated_total_income_invalid_user, Decimal('0.00'))

            # Test with invalid inputs (end date before start date)
            start_date = date(2023, 1, 15)
            end_date = date(2023, 1, 10)
            calculated_total_income_invalid_dates, _ = calculate_total_income_between_dates(user.id, start_date, end_date)
            self.assertEqual(calculated_total_income_invalid_dates, Decimal('0.00'))

            '''# Test for Negative Amounts
            cash_in_negative = CashIn(user_id=user.id, income_id=income1.id, amount=-200.00, date=today)
            db.session.add(cash_in_negative)
            db.session.commit()
            calculated_total_income_negative, _ = calculate_total_income_between_dates(user.id, today, today)
            self.assertEqual(calculated_total_income_negative, Decimal('0.00'))'''
 
    def test_calculate_total_expenses_between_dates(self):
        """
        Test the calculate_total_expenses_between_dates function.

        This method tests whether the function accurately calculates the total expenses for a user within specified dates,
        and also verifies the correctness of individual expense transactions returned by the function.
        """
        with app.app_context():
            # Step 1: Add a User
            user = User(first_name='test_user', last_name='test_user', password='test_password', email='test@example.com')
            db.session.add(user)
            db.session.commit()

            # Step 2: Add Expenses
            expense1 = Expense(user_id=user.id, name='Rent')
            expense2 = Expense(user_id=user.id, name='Groceries')
            db.session.add_all([expense1, expense2])
            db.session.commit()

            # Step 3: Add CashOut entries over a period of time for different Expenses
            today = date.today()
            cash_out1 = CashOut(user_id=user.id, amount=100.00, expense_id=expense1.id, date=today - timedelta(days=10))
            cash_out2 = CashOut(user_id=user.id, amount=50.00, expense_id=expense2.id, date=today - timedelta(days=5))
            cash_out3 = CashOut(user_id=user.id, amount=75.00, expense_id=expense1.id, date=today - timedelta(days=2))
            db.session.add_all([cash_out1, cash_out2, cash_out3])
            db.session.commit()

            # Step 4: Test with specified dates
            start_date = today - timedelta(days=7)
            end_date = today
            cash_outflows = CashOut.query.filter(
                CashOut.user_id == user.id,
                CashOut.date >= start_date,
                CashOut.date <= end_date
            ).all()

            total_expenses = sum(cash_out.amount for cash_out in cash_outflows)
            total_expenses = Decimal(total_expenses).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

            calculated_total_expenses, individual_expenses = calculate_total_expenses_between_dates(user.id, start_date, end_date)
            
            # Check the calculated total expenses
            self.assertEqual(calculated_total_expenses, total_expenses)

            # Check individual expenses
            self.assertEqual(len(individual_expenses), len(cash_outflows))
            for calculated_expense, original_cash_out in zip(individual_expenses, cash_outflows):
                self.assertEqual(calculated_expense['amount'], original_cash_out.amount)
                self.assertEqual(calculated_expense['date'], original_cash_out.date)
                expense = db.session.get(Expense, original_cash_out.expense_id)
                self.assertEqual(calculated_expense['name'], expense.name)

            # Step 5: Test with None dates
            today = date.today()
            start_date_none = date(today.year, today.month, 1)
            end_date_none = today
            cash_outflows_none = CashOut.query.filter(
                CashOut.user_id == user.id,
                CashOut.date >= start_date_none,
                CashOut.date <= end_date_none
            ).all()

            total_expenses_none = sum(cash_out.amount for cash_out in cash_outflows_none)
            total_expenses_none = Decimal(total_expenses_none).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

            calculated_total_expenses_none, individual_expenses_none = calculate_total_expenses_between_dates(user.id, None, None)

            # Check the calculated total expenses
            self.assertEqual(calculated_total_expenses_none, total_expenses_none)

            # Check individual expenses
            self.assertEqual(len(individual_expenses_none), len(cash_outflows_none))
            for calculated_expense, original_cash_out in zip(individual_expenses_none, cash_outflows_none):
                self.assertEqual(calculated_expense['amount'], original_cash_out.amount)
                self.assertEqual(calculated_expense['date'], original_cash_out.date)
                expense = db.session.query(Expense).join(CashOut, CashOut.expense_id == Expense.id).filter(CashOut.id == original_cash_out.id).first()
                self.assertEqual(calculated_expense['name'], expense.name)

            # Test with no transactions within specified dates
            calculated_total_expenses_empty, individual_expenses_empty = calculate_total_expenses_between_dates(user.id, today, today)
            self.assertEqual(calculated_total_expenses_empty, Decimal('0.00'))
            self.assertEqual(len(individual_expenses_empty), 0)

            # Test transactions exactly on start and end dates
            cash_out_same_day = CashOut(user_id=user.id, expense_id=expense1.id, amount=50.00, date=today)
            db.session.add(cash_out_same_day)
            db.session.commit()
            calculated_total_expenses_same_day, individual_expenses_same_day = calculate_total_expenses_between_dates(user.id, today, today)
            self.assertEqual(calculated_total_expenses_same_day, Decimal('50.00'))
            self.assertEqual(len(individual_expenses_same_day), 1)
            self.assertEqual(individual_expenses_same_day[0]['amount'], cash_out_same_day.amount)
            self.assertEqual(individual_expenses_same_day[0]['date'], cash_out_same_day.date)

            # Test multiple transactions on the same date
            cash_out_same_day_2 = CashOut(user_id=user.id, expense_id=expense1.id, amount=30.00, date=today)
            db.session.add(cash_out_same_day_2)
            db.session.commit()
            calculated_total_expenses_multiple, individual_expenses_multiple = calculate_total_expenses_between_dates(user.id, today, today)
            expected_total_expenses_multiple = cash_out_same_day.amount + cash_out_same_day_2.amount
            self.assertEqual(calculated_total_expenses_multiple, expected_total_expenses_multiple)
            self.assertEqual(len(individual_expenses_multiple), 2)
            self.assertEqual(individual_expenses_multiple[0]['amount'], cash_out_same_day.amount)
            self.assertEqual(individual_expenses_multiple[0]['date'], cash_out_same_day.date)
            self.assertEqual(individual_expenses_multiple[1]['amount'], cash_out_same_day_2.amount)
            self.assertEqual(individual_expenses_multiple[1]['date'], cash_out_same_day_2.date)

            # Test with invalid inputs (non-existent user ID)
            calculated_total_expenses_invalid_user, individual_expenses_invalid_user = calculate_total_expenses_between_dates(-1, start_date, end_date)
            self.assertEqual(calculated_total_expenses_invalid_user, Decimal('0.00'))
            self.assertEqual(len(individual_expenses_invalid_user), 0)

            # Test with invalid inputs (end date before start date)
            calculated_total_expenses_invalid_dates, individual_expenses_invalid_dates = calculate_total_expenses_between_dates(user.id, end_date, start_date)
            self.assertEqual(calculated_total_expenses_invalid_dates, Decimal('0.00'))
            self.assertEqual(len(individual_expenses_invalid_dates), 0)

            '''# Test for Negative Amounts
            negative_cash_out = CashOut(user_id=user.id, expense_id=expense2.id, amount=-25.00, date=today - timedelta(days=1))
            db.session.add(negative_cash_out)
            db.session.commit()
            calculated_total_expenses_negative, individual_expenses_negative = calculate_total_expenses_between_dates(user.id, start_date, end_date)
            expected_total_expenses_negative = total_expenses + Decimal(negative_cash_out.amount).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            self.assertEqual(calculated_total_expenses_negative, expected_total_expenses_negative)
            self.assertEqual(len(individual_expenses_negative), len(cash_outflows) + 1)
            for calculated_expense, original_cash_out in zip(individual_expenses_negative, cash_outflows):
                self.assertEqual(calculated_expense['amount'], original_cash_out.amount)
                self.assertEqual(calculated_expense['date'], original_cash_out.date)
                expense = db.session.get(Expense, original_cash_out.expense_id)
                self.assertEqual(calculated_expense['name'], expense.name)
            self.assertEqual(individual_expenses_negative[-1]['amount'], negative_cash_out.amount)
            self.assertEqual(individual_expenses_negative[-1]['date'], negative_cash_out.date)
            expense = db.session.get(Expense, negative_cash_out.expense_id)
            self.assertEqual(individual_expenses_negative[-1]['name'], expense.name)'''


    def test_calculate_total_income(self):
        """
        Test the calculate_total_income function.

        This method tests whether the function accurately calculates the total income for a user.
        """
        with app.app_context():
            # Step 1: Add a User
            user = User(first_name='test_user', last_name='test_user', password='test_password', email='test@example.com')
            db.session.add(user)
            db.session.commit()

            # Step 2: Add IncomeTypes and Incomes
            income_type1 = IncomeType(name='Salary')
            income_type2 = IncomeType(name='Freelance')
            db.session.add_all([income_type1, income_type2])
            db.session.commit()

            income1 = Income(user_id=user.id, name='Monthly Salary', income_type_id=income_type1.id)
            income2 = Income(user_id=user.id, name='Project Payment', income_type_id=income_type2.id)
            db.session.add_all([income1, income2])
            db.session.commit()

            # Test with No Incomes
            calculated_total_income_no_incomes = calculate_total_income(user.id)
            self.assertEqual(calculated_total_income_no_incomes, Decimal('0.00'))

            # Step 3: Add CashIn entries for different Incomes
            cash_in1 = CashIn(user_id=user.id, income_id=income1.id, amount=1000.00, date=date.today())
            cash_in2 = CashIn(user_id=user.id, income_id=income2.id, amount=500.00, date=date.today())
            cash_in3 = CashIn(user_id=user.id, income_id=income1.id, amount=750.00, date=date.today())
            db.session.add_all([cash_in1, cash_in2, cash_in3])
            db.session.commit()

            # Step 4: Calculate total income
            total_income = sum(cash_in.amount for cash_in in [cash_in1, cash_in2, cash_in3])
            total_income = Decimal(total_income).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

            calculated_total_income = calculate_total_income(user.id)

            # Check the calculated total income
            self.assertEqual(calculated_total_income, total_income)

            # Step 5: Add a new CashIn entry and recalculate total income
            new_cash_in = CashIn(user_id=user.id, income_id=income1.id, amount=250.00, date=date.today())
            db.session.add(new_cash_in)
            db.session.commit()

            total_income += new_cash_in.amount
            calculated_total_income = calculate_total_income(user.id)

            # Check the updated calculated total income
            self.assertEqual(calculated_total_income, total_income)

            # Step 6: Add a CashIn entry with negative amount and recalculate total income
            negative_cash_in = CashIn(user_id=user.id, income_id=income2.id, amount=-50.00, date=date.today())
            db.session.add(negative_cash_in)
            db.session.commit()

            total_income += negative_cash_in.amount  # Since it's negative, it would reduce the total income
            calculated_total_income = calculate_total_income(user.id)

            # Check the updated calculated total income
            self.assertEqual(calculated_total_income, total_income)

            # Test with Non-Existent User ID
            calculated_total_income_invalid_user = calculate_total_income(-1)
            self.assertEqual(calculated_total_income_invalid_user, Decimal('0.00'))


    def test_calculate_total_expenses(self):
        """
        Test the calculate_total_expenses function.

        This method tests whether the function accurately calculates the total expenses for a user.
        """
        with app.app_context():
            # Step 1: Add a User
            user = User(first_name='test_user', last_name='test_user', password='test_password', email='test@example.com')
            db.session.add(user)
            db.session.commit()

            # Step 2: Add Expenses
            expense1 = Expense(user_id=user.id, name='Rent')
            expense2 = Expense(user_id=user.id, name='Groceries')
            db.session.add_all([expense1, expense2])
            db.session.commit()

            # Test with No Expenses
            calculated_total_expenses_no_expenses = calculate_total_expenses(user.id)
            self.assertEqual(calculated_total_expenses_no_expenses, Decimal('0.00'))

            # Step 3: Add CashOut entries for different Expenses
            cash_out1 = CashOut(user_id=user.id, amount=100.00, expense_id=expense1.id, date=date.today())
            cash_out2 = CashOut(user_id=user.id, amount=50.00, expense_id=expense2.id, date=date.today())
            cash_out3 = CashOut(user_id=user.id, amount=75.00, expense_id=expense1.id, date=date.today())
            db.session.add_all([cash_out1, cash_out2, cash_out3])
            db.session.commit()

            # Step 4: Calculate total expenses
            total_expenses = sum(cash_out.amount for cash_out in [cash_out1, cash_out2, cash_out3])
            total_expenses = Decimal(total_expenses).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

            calculated_total_expenses = calculate_total_expenses(user.id)

            # Check the calculated total expenses
            self.assertEqual(calculated_total_expenses, total_expenses)

            # Step 5: Add a new CashOut entry and recalculate total expenses
            new_cash_out = CashOut(user_id=user.id, expense_id=expense1.id, amount=30.00, date=date.today())
            db.session.add(new_cash_out)
            db.session.commit()

            total_expenses += new_cash_out.amount
            calculated_total_expenses = calculate_total_expenses(user.id)

            # Check the updated calculated total expenses
            self.assertEqual(calculated_total_expenses, total_expenses)

            # Step 6: Add a CashOut entry with negative amount and recalculate total expenses
            negative_cash_out = CashOut(user_id=user.id, expense_id=expense2.id, amount=-20.00, date=date.today())
            db.session.add(negative_cash_out)
            db.session.commit()

            total_expenses += negative_cash_out.amount  # Since it's negative, it would reduce the total expenses
            calculated_total_expenses = calculate_total_expenses(user.id)

            # Check the updated calculated total expenses
            self.assertEqual(calculated_total_expenses, total_expenses)

            # Test with Non-Existent User ID
            calculated_total_expenses_invalid_user = calculate_total_expenses(-1)
            self.assertEqual(calculated_total_expenses_invalid_user, Decimal('0.00'))


    def test_calculate_savings_between_dates(self):
        """
        Test the calculate_savings_between_dates function.

        This method tests whether the function accurately calculates the savings (total income - total expenses)
        and the percentage of savings for a user within specified dates.
        """
        with app.app_context():
            # Step 1: Add a User
            user = User(first_name='test_user', last_name='test_user', password='test_password', email='test@example.com')
            db.session.add(user)
            db.session.commit()

            # Step 2: Add IncomeTypes and Incomes
            income_type1 = IncomeType(name='Salary')
            income_type2 = IncomeType(name='Freelance')
            db.session.add_all([income_type1, income_type2])
            db.session.commit()

            income1 = Income(user_id=user.id, name='Monthly Salary', income_type_id=income_type1.id)
            income2 = Income(user_id=user.id, name='Project Payment', income_type_id=income_type2.id)
            db.session.add_all([income1, income2])
            db.session.commit()

            # Step 3: Add CashIn and CashOut entries for different Incomes and Expenses
            today = date.today()
            cash_in1 = CashIn(user_id=user.id, income_id=income1.id, amount=1000.00, date=today - timedelta(days=10))
            cash_in2 = CashIn(user_id=user.id, income_id=income2.id, amount=500.00, date=today - timedelta(days=5))
            cash_in3 = CashIn(user_id=user.id, income_id=income1.id, amount=750.00, date=today - timedelta(days=2))
            db.session.add_all([cash_in1, cash_in2, cash_in3])
            db.session.commit()

            expense1 = Expense(user_id=user.id, name='Rent')
            expense2 = Expense(user_id=user.id, name='Groceries')
            db.session.add_all([expense1, expense2])
            db.session.commit()

            cash_out1 = CashOut(user_id=user.id, amount=100.00, expense_id=expense1.id, date=today - timedelta(days=10))
            cash_out2 = CashOut(user_id=user.id, amount=50.00, expense_id=expense2.id, date=today - timedelta(days=5))
            cash_out3 = CashOut(user_id=user.id, amount=75.00, expense_id=expense1.id, date=today - timedelta(days=2))
            db.session.add_all([cash_out1, cash_out2, cash_out3])
            db.session.commit()

            # Test with specified dates
            start_date = today - timedelta(days=10)
            end_date = today

            total_income = sum(cash_in.amount for cash_in in [cash_in1, cash_in2, cash_in3])
            total_expenses = sum(cash_out.amount for cash_out in [cash_out1, cash_out2, cash_out3])
            total_savings = total_income - total_expenses
            total_savings = Decimal(total_savings).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            total_percentage_savings = (total_savings / total_income) * 100 if total_income != 0 else 0
            total_percentage_savings = Decimal(total_percentage_savings).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

            calculated_total_savings, calculated_percentage_savings = calculate_savings_between_dates(user.id, start_date, end_date)

            # Check the calculated total savings and percentage savings
            self.assertEqual(calculated_total_savings, total_savings)
            self.assertEqual(calculated_percentage_savings, total_percentage_savings)


            # Test with no transactions within specified dates
            calculated_total_savings_empty, calculated_percentage_savings_empty = calculate_savings_between_dates(user.id, today, today)
            self.assertEqual(calculated_total_savings_empty, Decimal('0.00'))
            self.assertEqual(calculated_percentage_savings_empty, Decimal('0.00'))

            # Test transactions exactly on start and end dates
            cash_in_same_day = CashIn(user_id=user.id, income_id=income1.id, amount=200.00, date=today)
            cash_out_same_day = CashOut(user_id=user.id, expense_id=expense1.id, amount=50.00, date=today)
            db.session.add(cash_in_same_day)
            db.session.add(cash_out_same_day)
            db.session.commit()

            expected_total_savings_same_day = cash_in_same_day.amount - cash_out_same_day.amount
            expected_percentage_savings_same_day = (expected_total_savings_same_day / cash_in_same_day.amount) * 100
            expected_percentage_savings_same_day = Decimal(expected_percentage_savings_same_day).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

            calculated_total_savings_same_day, calculated_percentage_savings_same_day = calculate_savings_between_dates(user.id, today, today)

            self.assertEqual(calculated_total_savings_same_day, expected_total_savings_same_day)
            self.assertEqual(calculated_percentage_savings_same_day, expected_percentage_savings_same_day)

            # Test multiple transactions on the same date
            cash_in_same_day_2 = CashIn(user_id=user.id, income_id=income1.id, amount=300.00, date=today)
            cash_out_same_day_2 = CashOut(user_id=user.id, expense_id=expense1.id, amount=70.00, date=today)
            db.session.add(cash_in_same_day_2)
            db.session.add(cash_out_same_day_2)
            db.session.commit()

            expected_total_savings_multiple = (
                cash_in_same_day.amount + cash_in_same_day_2.amount
            ) - (cash_out_same_day.amount + cash_out_same_day_2.amount)
            expected_percentage_savings_multiple = (expected_total_savings_multiple / (cash_in_same_day.amount + cash_in_same_day_2.amount)) * 100
            expected_percentage_savings_multiple = Decimal(expected_percentage_savings_multiple).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

            calculated_total_savings_multiple, calculated_percentage_savings_multiple = calculate_savings_between_dates(user.id, today, today)

            self.assertEqual(calculated_total_savings_multiple, expected_total_savings_multiple)
            self.assertEqual(calculated_percentage_savings_multiple, expected_percentage_savings_multiple)

            # Test with invalid inputs (non-existent user ID)
            calculated_total_savings_invalid_user, calculated_percentage_savings_invalid_user = calculate_savings_between_dates(-1, start_date, end_date)
            self.assertEqual(calculated_total_savings_invalid_user, Decimal('0.00'))
            self.assertEqual(calculated_percentage_savings_invalid_user, Decimal('0.00'))

            # Test with invalid inputs (end date before start date)
            start_date = date(2023, 1, 15)
            end_date = date(2023, 1, 10)
            calculated_total_savings_invalid_dates, calculated_percentage_savings_invalid_dates = calculate_savings_between_dates(user.id, start_date, end_date)
            self.assertEqual(calculated_total_savings_invalid_dates, Decimal('0.00'))
            self.assertEqual(calculated_percentage_savings_invalid_dates, Decimal('0.00'))

            # Test scenarios involving rounding in savings amount
            cash_in_fractional = CashIn(user_id=user.id, income_id=income1.id, amount=100.01, date=today - timedelta(days=20))
            cash_out_fractional = CashOut(user_id=user.id, expense_id=expense1.id, amount=49.99, date=today - timedelta(days=20))
            db.session.add(cash_in_fractional)
            db.session.add(cash_out_fractional)
            db.session.commit()

            expected_total_savings_fractional = cash_in_fractional.amount - cash_out_fractional.amount
            expected_percentage_savings_fractional = (expected_total_savings_fractional / cash_in_fractional.amount) * 100
            expected_percentage_savings_fractional = Decimal(expected_percentage_savings_fractional).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

            calculated_total_savings_fractional, calculated_percentage_savings_fractional = calculate_savings_between_dates(user.id, today - timedelta(days=20), today - timedelta(days=20))

            self.assertEqual(calculated_total_savings_fractional, expected_total_savings_fractional)
            self.assertEqual(calculated_percentage_savings_fractional, expected_percentage_savings_fractional)

            # Test scenarios involving rounding in savings percentage
            cash_in_low_amount = CashIn(user_id=user.id, income_id=income1.id, amount=10.00, date=today - timedelta(days=25))
            cash_out_low_amount = CashOut(user_id=user.id, expense_id=expense1.id, amount=2.13, date=today - timedelta(days=25))
            db.session.add(cash_in_low_amount)
            db.session.add(cash_out_low_amount)
            db.session.commit()

            expected_total_savings_low_amount = cash_in_low_amount.amount - cash_out_low_amount.amount
            expected_percentage_savings_low_amount = (expected_total_savings_low_amount / cash_in_low_amount.amount) * 100
            expected_percentage_savings_low_amount = Decimal(expected_percentage_savings_low_amount).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

            calculated_total_savings_low_amount, calculated_percentage_savings_low_amount = calculate_savings_between_dates(user.id, today - timedelta(days=25), today - timedelta(days=25))

            self.assertEqual(calculated_total_savings_low_amount, expected_total_savings_low_amount)
            self.assertEqual(calculated_percentage_savings_low_amount, expected_percentage_savings_low_amount)

            # Test cases with negative savings (indicating loss)
            #cash_in_loss = CashIn(user_id=user.id, income_id=income1.id, amount=3.50, date=today - timedelta(days=24))
            cash_out_loss = CashOut(user_id=user.id, expense_id=expense1.id, amount=20.00, date=today - timedelta(days=25))

            db.session.add(cash_out_loss)
            db.session.commit()

            expected_total_savings_loss = cash_in_low_amount.amount - (cash_out_loss.amount + cash_out_low_amount.amount)
            expected_percentage_savings_loss = (expected_total_savings_loss / cash_in_low_amount.amount) * 100
            expected_percentage_savings_loss = Decimal(expected_percentage_savings_loss).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

            calculated_total_savings_loss, calculated_percentage_savings_loss = calculate_savings_between_dates(user.id, today - timedelta(days=25), today - timedelta(days=25))

            self.assertEqual(calculated_total_savings_loss, expected_total_savings_loss)
            self.assertEqual(calculated_percentage_savings_loss, expected_percentage_savings_loss)



    def test_calculate_expense_percentage_of_income(self):
        """
        Test the calculate_expense_percentage_of_income function.

        This method tests whether the function accurately calculates the percentage of income that each expense takes within specified dates.
        """
        with app.app_context():
            today = date.today()
            
            # Step 1: Add a User
            user = User(first_name='test_user', last_name='test_user', password='test_password', email='test@example.com')
            db.session.add(user)
            db.session.commit()

            # Step 2: Add IncomeTypes, Incomes, Expenses, and Transactions
            income_type1 = IncomeType(name='Salary')
            income_type2 = IncomeType(name='Freelance')
            db.session.add_all([income_type1, income_type2])
            db.session.commit()

            income1 = Income(user_id=user.id, name='Monthly Salary', income_type_id=income_type1.id)
            income2 = Income(user_id=user.id, name='Project Payment', income_type_id=income_type2.id)
            db.session.add_all([income1, income2])
            db.session.commit()

            expense1 = Expense(user_id=user.id, name='Rent')
            expense2 = Expense(user_id=user.id, name='Groceries')
            db.session.add_all([expense1, expense2])
            db.session.commit()

            # Add CashOut transactions with unique combinations of expense and date
            cash_out1 = CashOut(user_id=user.id, amount=100.00, expense_id=expense1.id, date=today - timedelta(days=10))
            cash_out2 = CashOut(user_id=user.id, amount=50.00, expense_id=expense2.id, date=today - timedelta(days=5))
            cash_out3 = CashOut(user_id=user.id, amount=75.00, expense_id=expense1.id, date=today - timedelta(days=2))
            db.session.add_all([cash_out1, cash_out2, cash_out3])

            cash_in1 = CashIn(user_id=user.id, income_id=income1.id, amount=1000.00, date=today - timedelta(days=10))
            cash_in2 = CashIn(user_id=user.id, income_id=income2.id, amount=500.00, date=today - timedelta(days=5))
            cash_in3 = CashIn(user_id=user.id, income_id=income1.id, amount=750.00, date=today - timedelta(days=2))
            db.session.add_all([cash_in1, cash_in2, cash_in3])

            db.session.commit()

            # Test with specified dates
            start_date = today - timedelta(days=10)
            end_date = today

            from collections import defaultdict

            # # Calculate the expected expense percentages
            total_income = sum(cash_in.amount for cash_in in [cash_in1, cash_in2, cash_in3])
            total_income = float(total_income)
            expected_expense_percentages = []

            # Define the test data directly
            test_data = [
                {'name': 'Rent', 'amount': 100.00, 'income_category_id': expense1.id},
                {'name': 'Groceries', 'amount': 50.00, 'income_category_id': expense2.id},
                {'name': 'Rent', 'amount': 75.00, 'income_category_id': expense1.id},
            ]

            # Group expenses by category and calculate total amount for each category
            grouped_expenses = {}
            for expense_data in test_data:
                category_id = expense_data['income_category_id']
                if category_id not in grouped_expenses:
                    grouped_expenses[category_id] = {
                        'name': expense_data['name'],
                        'total_amount': 0.0
                    }
                grouped_expenses[category_id]['total_amount'] += expense_data['amount']

            # Calculate the expected expense percentages
            for category_id, category_data in grouped_expenses.items():
                expense_percent = (category_data['total_amount'] / total_income) * 100 if total_income != 0 else 0
                expected_expense_percentages.append({
                    'expense_id': category_id,
                    'expense_name': category_data['name'],
                    'total_amount': Decimal(category_data['total_amount']),
                    'percentage': round(Decimal(expense_percent), 2)  # Round the percentage to 2 decimal places
                })

            total_expense_percent_of_income = (sum(category_data['total_amount'] for category_data in grouped_expenses.values()) / total_income) * 100 if total_income != 0 else 0
            total_expense_percent_of_income = round(total_expense_percent_of_income, 2)

            # Calculate the expected result using the function and round the percentages
            calculated_expense_percentages = calculate_expense_percentage_of_income(user.id, start_date, end_date)
            for expense in calculated_expense_percentages:
                expense['percentage'] = round(expense['percentage'], 2)

            # Test the calculated expense percentages and total expense percentage
            self.assertEqual(calculated_expense_percentages, expected_expense_percentages)

            # Test with an invalid user ID
            calculated_expense_percentages_invalid_user= calculate_expense_percentage_of_income(-1, start_date, end_date)
            self.assertEqual(calculated_expense_percentages_invalid_user, [])

            # Test with invalid dates
            start_date_invalid = date(2023, 1, 15)
            end_date_invalid = date(2023, 1, 10)
            calculated_expense_percentages_invalid_dates= calculate_expense_percentage_of_income(user.id, start_date_invalid, end_date_invalid)
            self.assertEqual(calculated_expense_percentages_invalid_dates, [])

if __name__ == '__main__':
    unittest.main()
