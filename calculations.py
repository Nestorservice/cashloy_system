from datetime import datetime, date, timedelta
from decimal import Decimal, ROUND_HALF_UP
from models import CashIn, Income, IncomeType, db
import logging
logging.basicConfig(level=logging.INFO)

def calculate_total_income_between_dates(user_id, start_date=None, end_date=None):
    """
    Calculate the total income for a user between specified dates.

    Args:
        user_id (int): The user's ID.
        start_date (date, optional): The start date of the range.
        end_date (date, optional): The end date of the range.

    Returns:
        tuple: A tuple containing total income amount and a list of individual income transactions.
                Each individual transaction is represented as a dictionary with keys: 'amount', 'date', 'name', 'income_type'.
    """
    if start_date is None:
        start_date = date(datetime.now().year, datetime.now().month, 1)
    if end_date is None:
        end_date = date.today()

    cash_incomes = CashIn.query.filter(
        CashIn.user_id == user_id,
        CashIn.date >= start_date,
        CashIn.date <= end_date
    ).all()

    total_income = 0
    individual_incomes = []

    for cash_in in cash_incomes:
        income = db.session.get(Income, cash_in.income_id)
        if income is None:
            logging.error(f"Income is None for income_id: {cash_in.income_id}")
            continue

        income_type = db.session.get(IncomeType, income.income_type_id)
        if income_type is None:
            logging.error(f"IncomeType is None for income_type_id: {income.income_type_id}")
            continue

        total_income += cash_in.amount
        individual_incomes.append({
            'amount': cash_in.amount,
            'date': cash_in.date,
            'name': income.name,
            'description': cash_in.description,
            'id': cash_in.id,
            'income_type': income_type.name,
            'type': 'Income',
            'income_category_id': cash_in.income_id
        })

    total_income = Decimal(total_income).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    return total_income, individual_incomes



def calculate_total_expenses_between_dates(user_id, start_date=None, end_date=None):
    """
    Calculate the total expenses for a user between specified dates.

    Args:
        user_id (int): The user's ID.
        start_date (date, optional): The start date of the range.
        end_date (date, optional): The end date of the range.

    Returns:
        tuple: A tuple containing total expenses amount and a list of individual expense transactions.
                Each individual transaction is represented as a dictionary with keys: 'amount', 'date', 'name'.

    """
    from models import CashOut, Expense, db

    if start_date is None:
        start_date = date(datetime.now().year, datetime.now().month, 1)
    if end_date is None:
        end_date = date.today()

    cash_outflows = CashOut.query.filter(
        CashOut.user_id == user_id,
        CashOut.date >= start_date,
        CashOut.date <= end_date
    ).all()

    total_expenses = 0
    individual_expenses = []

    for cash_out in cash_outflows:
        expense = db.session.get(Expense, cash_out.expense_id)
        total_expenses += cash_out.amount
        individual_expenses.append({
            'amount': cash_out.amount,
            'date': cash_out.date,
            'name': expense.name,
            'description': cash_out.description,
            'id': cash_out.id, 
            'type': 'Expense',
            'expense_category_id': cash_out.expense_id
        })

    total_expenses = Decimal(total_expenses).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    return total_expenses, individual_expenses

def calculate_total_income(user_id):
    """
    Calculate the total income for a user.

    Args:
        user_id (int): The user's ID.

    Returns:
        float: The total income amount for the user.

    """
    from models import CashIn

    incomes = CashIn.query.filter_by(user_id=user_id).all()
    total_income = sum(income.amount for income in incomes)
    return total_income

def calculate_total_expenses(user_id):
    """
    Calculate the total expenses for a user.

    Args:
        user_id (int): The user's ID.

    Returns:
        float: The total expenses amount for the user.

    """
    from models import CashOut

    expenses = CashOut.query.filter_by(user_id=user_id).all()
    total_expenses = sum(expense.amount for expense in expenses)
    return total_expenses

def calculate_savings_between_dates(user_id, start_date=None, end_date=None):
    """
    Calculate a user's savings within a specified date range.

    Args:
        user_id (int): The user's ID.
        start_date (date, optional): The start date of the range.
        end_date (date, optional): The end date of the range.

    Returns:
        float: The savings amount within the specified date range.
        float: The percentage of savings as compared to total income.

    """
    total_income, _ = calculate_total_income_between_dates(user_id, start_date, end_date)
    total_expenses, _ = calculate_total_expenses_between_dates(user_id, start_date, end_date)

    savings = (total_income) - (total_expenses)
    savings_percent_of_income = (savings / total_income) * 100 if total_income != 0 else 0

    savings_percent_of_income = round(savings_percent_of_income, 2)

    return savings, savings_percent_of_income

def calculate_expense_percentage_of_income(user_id, start_date=None, end_date=None):
    from models import Expense, CashOut, db
    from sqlalchemy import func

    if start_date is None:
        start_date = date(datetime.now().year, datetime.now().month, 1)
    if end_date is None:
        end_date = date.today()

    # Step 1: Calculate total income
    total_income, _ = calculate_total_income_between_dates(user_id, start_date, end_date)
    
    # Step 2: Join CashOut and Expense models
    cash_out_expense_join = db.session.query(CashOut, Expense).join(
        Expense, CashOut.expense_id == Expense.id
    )
    
    # Step 3: Group cash out transactions by expense_id and calculate the sum of amount
    expense_sums = cash_out_expense_join.filter(
        CashOut.user_id == user_id,
        CashOut.date >= start_date,
        CashOut.date <= end_date
    ).group_by(Expense.id).with_entities(
        Expense.id,
        Expense.name,
        func.sum(CashOut.amount).label('total_amount')
    ).all()
    
    # Step 4 and 5: Calculate percentage of each expense category's total to total income
    expense_percentages = []
    for expense_sum in expense_sums:
        expense_id, expense_name, total_amount = expense_sum
        try:
            percentage = (total_amount / total_income) * 100 if total_income > 0 else 0
        except:
            percentage = "{:.2f}".format(0)
        expense_percentages.append({
            'expense_id': expense_id,
            'expense_name': expense_name,
            'total_amount': total_amount,
            'percentage': percentage
        })
    
    return expense_percentages



