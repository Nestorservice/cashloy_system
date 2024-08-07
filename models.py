from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(db.Model, UserMixin):
    """
    Represents a user of the application.

    Attributes:
        id (int): The unique identifier for the user.
        first_name (str): The first name of the user.
        last_name (str): The last name of the user.
        password (str): The password associated with the user.
        email (str): The email address of the user (unique).
    Methods:
        __repr__: Returns a string representation of the User object.
    """

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return f"<User {self.id}: {self.first_name} {self.last_name}>"

class IncomeType(db.Model):
    """
    Represents different types of income sources.

    Attributes:
        id (int): The unique identifier for the income type.
        name (str): The name of the income type.
    """

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f"<IncomeType {self.name}>"

class Income(db.Model):
    """
    Represents an income category associated with a user and an income type.

    Attributes:
        id (int): The unique identifier for the income transaction.
        name (str): The name of the income.
        user_id (int): The foreign key referencing the associated User.
        income_type_id (int): The foreign key referencing the associated IncomeType.
    """

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    income_type_id = db.Column(db.Integer, db.ForeignKey('income_type.id'), nullable=False)

    def __repr__(self):
        return f"<Income {self.name}>"

class Expense(db.Model):
    """
    Represents an expense category associated with a user.

    Attributes:
        id (int): The unique identifier for the expense transaction.
        name (str): The name of the expense.
        user_id (int): The foreign key referencing the associated User.
    """

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    budget_expenses = db.relationship('BudgetExpense', back_populates='expense', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Expense {self.name}>"

class CashIn(db.Model):
    """
    Represents a cash inflow transaction associated with a user and an income.

    Attributes:
        id (int): The unique identifier for the cash inflow transaction.
        user_id (int): The foreign key referencing the associated User.
        income_id (int): The foreign key referencing the associated Income.
        amount (float): The amount of cash inflow.
        date (date): The date of the cash inflow transaction.
        description: Details of the transaction
        settled_credit_id (int): The foreign key referencing the associated Credit (optional).
        settled_credit (relationship): Many-to-one relationship with Credit.
    """

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    income_id = db.Column(db.Integer, db.ForeignKey('income.id'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    date = db.Column(db.Date, nullable=False)
    description = db.Column(db.String(100), nullable=True)
    settled_credit_id = db.Column(db.Integer, db.ForeignKey('credit.id'), nullable=True)

    settled_credit = db.relationship('Credit', back_populates='cash_in_transactions')

    def update_transaction(self, new_description, new_amount, new_date, new_income_id):
        # Update the transaction attributes
        self.description = new_description
        self.amount = new_amount
        self.date = new_date
        self.income_id = new_income_id
        db.session.commit()

    def delete_transaction(self):
        # Delete the transaction from the database
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return f"<CashIn {self.amount} on {self.date}>"

class CashOut(db.Model):
    """
    Represents a cash outflow transaction associated with a user and an expense.

    Attributes:
        id (int): The unique identifier for the cash outflow transaction.
        user_id (int): The foreign key referencing the associated User.
        amount (float): The amount of cash outflow.
        date (date): The date of the cash outflow transaction.
        expense_id (int): The foreign key referencing the associated Expense.
        description: Details of the transaction
        settled_debt_id (int): The foreign key referencing the associated Debt (optional).
        settled_debt (relationship): Many-to-one relationship with Debt.
    """

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    date = db.Column(db.Date, nullable=False)
    expense_id = db.Column(db.Integer, db.ForeignKey('expense.id'), nullable=False)
    description = db.Column(db.String(100), nullable=True)
    settled_debt_id = db.Column(db.Integer, db.ForeignKey('debt.id'), nullable=True)

    settled_debt = db.relationship('Debt', back_populates='cash_out_transactions')

    def update_transaction(self, new_description, new_amount, new_date, new_expense_id):
        # Update the transaction attributes
        self.description = new_description
        self.amount = new_amount
        self.date = new_date
        self.expense_id = new_expense_id
        db.session.commit()

    def delete_transaction(self):
        # Delete the transaction from the database
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return f"<CashOut {self.amount} on {self.date}>"

class Budget(db.Model):
    """
    Represents a budget for a specific month and year with its associated expenses.

    Attributes:
        id (int): The unique identifier for the budget.
        user_id (int): The foreign key referencing the associated User.
        year (int): The year of the budget.
        month (int): The month of the budget.
        budget_expenses (relationship): One-to-many relationship with BudgetExpense.
         
    Constraints:
        Unique constraint on user_id and month.
    
    Methods:
        __repr__: Returns a string representation of the Budget object.
    """

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    month = db.Column(db.Integer, nullable=False)

    # Add a unique constraint on user_id and month
    __table_args__ = (db.UniqueConstraint('user_id', 'year', 'month', name='_user_month_uc'),)

    expenses = db.relationship('BudgetExpense', back_populates='budget', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Budget {self.year}-{self.month} for User {self.user_id}>"

class BudgetExpense(db.Model):
    """
    Represents an expense associated with a budget, including the expected and spent amounts.

    Attributes:
        id (int): The unique identifier for the budget expense.
        budget_id (int): The foreign key referencing the associated Budget.
        expense_id (int): The foreign key referencing the associated Expense.
        expected_amount (float): The expected amount to be spent on the expense in the budget.
        spent_amount (float): The amount that has been spent on the expense in the budget.
    """
    
    id = db.Column(db.Integer, primary_key=True)
    budget_id = db.Column(db.Integer, db.ForeignKey('budget.id'), nullable=False)
    expense_id = db.Column(db.Integer, db.ForeignKey('expense.id', ondelete='CASCADE'), nullable=False)
    expected_amount = db.Column(db.Numeric(10, 2), nullable=False)
    spent_amount = db.Column(db.Numeric(10, 2), default=0.0)

    budget = db.relationship('Budget', back_populates='expenses')
    expense = db.relationship('Expense', back_populates='budget_expenses')

    # Add a unique constraint to prevent duplicate budget expense entries
    __table_args__ = (db.UniqueConstraint('budget_id', 'expense_id'),)

    def update_spent_amount(self, amount):
        # Update the transaction attributes
        if self.spent_amount == 0:
            self.spent_amount = amount
        else:
            self.spent_amount += amount
        db.session.commit()
        

    def __repr__(self):
        return f"<BudgetExpense budget_id={self.budget_id}, expense_id={self.expense_id}>"

class Debt(db.Model):
    """
    Represents a debt transaction associated with a user. You owe money

    Attributes:
        id (int): The unique identifier for the debt transaction.
        user_id (int): The foreign key referencing the associated User.
        creditor (str): The name of the creditor.
        amount (float): The amount of the debt.
        date (date): The date of the debt transaction.
        description (str): A description of the debt.
        date_due (date): The date when the debt is due to be paid.
        is_paid (bool): Indicates whether the debt has been paid (True) or not (False).
        amount_payed (float): The amount of the debt that has been paid.
        cash_out_transactions (relationship): One-to-many relationship with CashOut.
    """

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    creditor = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    date_taken = db.Column(db.Date, nullable=False)
    description = db.Column(db.String(200), nullable=True)
    date_due = db.Column(db.Date, nullable=True)
    is_paid = db.Column(db.Boolean, default=False)
    amount_payed = db.Column(db.Numeric(10, 2), default=0.0)

    cash_out_transactions = db.relationship('CashOut', back_populates='settled_debt', cascade='all')



    def __repr__(self):
        return f"<Debt {self.amount} to {self.creditor} on {self.date_taken}>"
    
class CreditorPayment(db.Model):
    """
    Represents payment transactions for a particular creditor.

    Attributes:
        id (int): The unique identifier for the payment transaction.
        debt_id (int): The foreign key referencing the associated debt.
        amount (float): The amount of the payment.
        date (date): The date of the payment transaction.
    """

    id = db.Column(db.Integer, primary_key=True)
    debt_id = db.Column(db.Integer, db.ForeignKey('debt.id'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    date = db.Column(db.Date, nullable=False)

    def __repr__(self):
        return f"<CreditorPayment {self.amount} for debt {self.debt_id} on {self.date}>"

class Credit(db.Model):
    """
    Represents a credit associated with a user. Someone who owes you money

    Attributes:
        id (int): The unique identifier for the credit transaction.
        user_id (int): The foreign key referencing the associated User.
        debtor (str): The name of the debtor.
        amount (float): The amount of the credit.
        date_taken (date): The date the credit was taken.
        description (str): A description of the credit.
        date_due (date): The date when the credit is due to be received.
        is_paid (bool): Indicates whether the credit has been received (True) or not (False).
        amount_paid (float): The amount of the credit that has been received.
        cash_in_transactions (relationship): One-to-many relationship with CashIn.
    """

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    debtor = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    date_taken = db.Column(db.Date, nullable=False)
    description = db.Column(db.String(200), nullable=True)
    date_due = db.Column(db.Date, nullable=True)
    is_paid = db.Column(db.Boolean, default=False)
    amount_paid = db.Column(db.Numeric(10, 2), default=0.0)

    cash_in_transactions = db.relationship('CashIn', back_populates='settled_credit', cascade='all')

    def __repr__(self):
        return f"<Credit {self.amount} from {self.debtor} on {self.date_taken}>"
    
class DebtorPayment(db.Model):
    """
    Represents payment transactions for a particular debtor.

    Attributes:
        id (int): The unique identifier for the payment transaction.
        credit_id (int): The foreign key referencing the associated Credit.
        amount (float): The amount of the payment.
        date (date): The date of the payment transaction.
    """

    id = db.Column(db.Integer, primary_key=True)
    credit_id = db.Column(db.Integer, db.ForeignKey('credit.id'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    date = db.Column(db.Date, nullable=False)

    # Define a relationship with the Credit model to associate payments with a specific credit
    #credit = db.relationship('Credit', back_populates='payments')

    def __repr__(self):
        return f"<DebtorPayment {self.amount} for Credit {self.credit_id} on {self.date}>"

def initialize_default_income_types():
    """
    Initialize default income types and global categories.
    Returns:
        None
    """
    default_income_types = [
        {'name': 'Revenu gagné'},
        {'name': 'Revenu passif'},
        {'name': 'Revenu du portefeuille'}
    ]

    for income_type_data in default_income_types:
        income_type = IncomeType.query.filter_by(name=income_type_data['name']).first()
        if not income_type:
            income_type = IncomeType(**income_type_data)
            db.session.add(income_type)

    # Check if a user with the email address already exists
    user = User.query.filter_by(email='default@gmail.com').first()

    if user:
        pass
    else:
        # Create a new user with the unique email address
        user = User(first_name='default', last_name='default', password='default', email='default@gmail.com')
        db.session.add(user)
        db.session.commit()

    # Check if the "Credit" expense category already exists
    expense1 = Expense.query.filter_by(user_id=user.id, name='Credit').first()
    if not expense1:
        expense1 = Expense(user_id=user.id, name='Credit')
        db.session.add(expense1)

    # Check if the "Settled Debt" expense category already exists
    expense2 = Expense.query.filter_by(user_id=user.id, name='Crédit réglé').first()
    if not expense2:
        expense2 = Expense(user_id=user.id, name='Crédit réglé')
        db.session.add(expense2)

    # Check if the "Debt" Income category already exists
    income_type = IncomeType.query.filter_by(name='Revenu du portefeuille').first()
    debt = Income.query.filter_by(user_id=user.id, name='Dette').first()
    if not debt:
        debt = Income(user_id=user.id, name='Dette', income_type_id=income_type.id)
        db.session.add(debt)

    # Check if the "Settled Credit" Income category already exists
    settled_credit = Income.query.filter_by(user_id=user.id, name='Crédit réglé').first()
    if not settled_credit:
        settled_credit = Income(user_id=user.id, name='Crédit réglé', income_type_id=income_type.id)
        db.session.add(settled_credit)

    db.session.commit()



