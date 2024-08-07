from flask import Flask, render_template, redirect, url_for, request, flash, jsonify, abort
from auth import register_user, authenticate_user
from forms import RegistrationForm, LoginForm, IncomeCategoryForm, IncomeTransactionForm
from models import db, initialize_default_income_types, User, Income, IncomeType, Credit, CashIn, Expense, Debt, CashOut, Budget, BudgetExpense, DebtorPayment, CreditorPayment
from flask_login import login_required, logout_user, LoginManager, login_user, current_user
from transactions import add_income, add_cash_in_transaction, calculate_income_totals, add_expense, calculate_expense_totals, add_cash_out_transaction, calculate_income_totals_formatted_debt, create_budget
from datetime import date, datetime, timedelta
from calculations import calculate_total_income_between_dates, calculate_total_expenses_between_dates, calculate_expense_percentage_of_income
from sqlalchemy import func
from titlecase import titlecase
from decimal import Decimal
import os
from dotenv import load_dotenv
import pymysql
from flask_migrate import Migrate

# Load environment variables from .env file
load_dotenv()

pymysql.install_as_MySQLdb()


# Configuration
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
#app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)

migrate = Migrate(app, db, render_as_batch=True)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Home Page(landing page)
@app.route('/')
def home():
    """
    Affichez la page d’accueil.

Retourne:
        str : modèle HTML rendu pour la page d’accueil.
    """
    return render_template('home.html')

# User login
@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Gérez la page de connexion.

Si l’utilisateur est déjà authentifié, redirigez-vous vers la page du tableau de bord.
    Si la méthode de requête est GET, affichez le formulaire de connexion.
    Si la méthode de requête est POST, traitez les données du formulaire et authentifiez l’utilisateur.

Retourne:
        str : Le modèle HTML rendu pour la page de connexion, avec le formulaire de connexion ou les messages flash.
    """
    
    form = LoginForm()

    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = authenticate_user(email, password)
        if user:
            login_user(user)
            if current_user.is_authenticated:
                username = current_user.first_name
            return redirect(url_for('dashboard', username=username))  
        else:
            flash('E-mail ou mot de passe non valide.', 'danger')
    
    return render_template('login.html', form=form)

# User Registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Gérez la page S’inscrire.

Si la méthode de requête est GET, affichez le formulaire d’inscription.
    Si la méthode de requête est POST, traitez les données du formulaire et créez un nouvel utilisateur.

Retourne:
        str : Le modèle HTML rendu pour la page de registre, avec le formulaire de registre ou les messages flash.
    """
    form = RegistrationForm()

    if form.validate_on_submit():
        first_name = form.first_name.data
        last_name = form.last_name.data
        password = form.password.data
        email = form.email.data
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('L’e-mail existe déjà. Veuillez en choisir un autre.', 'danger')
            return redirect(url_for('register'))
        new_user = register_user(first_name=first_name, last_name=last_name, password=password, email=email)

        flash('Inscription réussie !', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', form=form)

# User logout
@app.route('/logout')
@login_required
def logout():
    """
    Déconnectez l’utilisateur actuel.

Retourne:
        redirect : redirige l’utilisateur vers la page d’accueil.
    """
    logout_user()
    flash('Déconnexion réussie.', 'info')
    return redirect(url_for('home'))

@app.route('/chart_data', methods=['POST'])
def chart_data():
    expense_percentages = calculate_expense_percentage_of_income(current_user.id)
    expense_percentages.sort(key=lambda x: x['percentage'], reverse=True)
    top_expenses = expense_percentages[:6]
    remaining_percentage = sum(expense['percentage'] for expense in expense_percentages[6:])
    labels = [expense['expense_name'] for expense in top_expenses] + ['Autres']
    values = [expense['percentage'] for expense in top_expenses] + [remaining_percentage]

    colors = ['#ffb65d', '#465bca', '#9d3171', '#3eeed0', '#ff5497', '#309a6a', '#141c33']
    expense_chart_data = {
        'labels': labels,
        'values': values,
        'colors': colors,
    }
    income_totals = calculate_income_totals(current_user.id)

    today = date.today()
    start_date = date(today.year, today.month, 1)
    end_date = date.today()
    total_amount_paid = db.session.query(func.sum(CashIn.amount)).filter(
        CashIn.income_id==2,
        CashIn.user_id == current_user.id,
        CashIn.date >= start_date,
        CashIn.date <= end_date
    ).scalar()

    if total_amount_paid is None:
        total_amount_paid = 0 
    total_amount_taken = db.session.query(func.sum(Debt.amount)).filter(
        Debt.user_id == current_user.id,
        Debt.date_taken >= start_date,
        Debt.date_taken <= end_date
    ).scalar()

    if total_amount_taken is None:
        total_amount_taken = 0
    
    income_totals['Dette contractée'] = total_amount_taken

    income_totals['Crédit réglé'] = total_amount_paid

    total_income = sum(income_totals.values())
    income_labels = []
    income_values = []
    income_colors = ['#ffb65d', '#465bca', '#9d3171', '#3eeed0', '#ff5497', '#309a6a', '#141c33']

    income_chart_data = {
        'labels': income_labels,
        'values': income_values,
        'colors': income_colors,
    }

    for category, amount in income_totals.items():
        try:
            percentage = "{:.2f}".format((amount / total_income) * 100)
        except:
            percentage = "{:.2f}".format(0)
        income_labels.append(category)
        income_values.append(percentage)

    today = date.today()
    start_date = date(today.year, today.month, 1)

    end_date1 = start_date + timedelta(days=6)
    end_date2 = start_date + timedelta(days=13)
    end_date3 = start_date + timedelta(days=20)
    end_date4 = start_date + timedelta(days=27)

    total_cash_out1 = db.session.query(func.sum(CashOut.amount)).filter(
        CashOut.user_id == current_user.id,
        CashOut.date >= start_date,
        CashOut.date <= end_date1
    ).scalar()

    total_cash_out2 = db.session.query(func.sum(CashOut.amount)).filter(
        CashOut.user_id == current_user.id,
        CashOut.date >= end_date1 + timedelta(days=1),
        CashOut.date <= end_date2
    ).scalar()

    total_cash_out3 = db.session.query(func.sum(CashOut.amount)).filter(
        CashOut.user_id == current_user.id,
        CashOut.date >= end_date2 + timedelta(days=1),
        CashOut.date <= end_date3
    ).scalar()

    total_cash_out4 = db.session.query(func.sum(CashOut.amount)).filter(
        CashOut.user_id == current_user.id,
        CashOut.date >= end_date3 + timedelta(days=1),
        CashOut.date <= end_date4
    ).scalar()

    cash_out_labels = [f"Semaine 1",
                       f"Semaine 2",
                       f"Semaine 3",
                       f"Semaine 4"]

    cash_out_values = [total_cash_out1 or 0, total_cash_out2 or 0, total_cash_out3 or 0, total_cash_out4 or 0]

    cash_out_chart_data = {
        'labels': cash_out_labels,
        'values': cash_out_values,
    }

    chart_data = {
        'expense_chart_data': expense_chart_data,
        'income_chart_data': income_chart_data,
        'cash_out_chart_data': cash_out_chart_data 
    }

    return jsonify(chart_data)

@login_required
@app.route('/dashboard', methods=['GET'])
def dashboard():
    """
    Affichez le tableau de bord de l’utilisateur.

Retourne:
        str : modèle HTML rendu pour le tableau de bord de l’utilisateur.
    """
    if current_user.is_authenticated:
        user_id = current_user.id
        user = User.query.get(user_id).first_name
        total_income, income_transactions = calculate_total_income_between_dates(user_id)
        total_expenses, expense_transactions = calculate_total_expenses_between_dates(user_id)
        all_transactions = income_transactions + expense_transactions
        all_transactions.sort(key=lambda x: x['date'])
        total_balance = total_income - total_expenses

        return render_template('dashboard.html', 
                               total_income=total_income, 
                               total_expenses=total_expenses, 
                               total_balance=total_balance, 
                               transactions=all_transactions, 
                               username=user)
    else:
        return redirect(url_for('login'))

# Revenu Magement ------------------------------------------------------------------------
@login_required
@app.route('/income', methods=['GET', 'POST'])
def income():
    """
    Gérer la gestion des revenus des utilisateurs.

Retourne:
        str : Le modèle HTML rendu pour la gestion des revenus.
    """
    user_id = current_user.id
    if request.method == 'POST':
        '''
        Filtrer les transactions de revenus par catégorie
        '''
        try:
            category_name = request.json.get('category_name')
            if   category_name == 'Debt':
                income_category = Income.query.filter_by(user_id=1, name=category_name).first()
            elif category_name == 'Settled Credit':
                income_category = Income.query.filter_by(user_id=1, name=category_name).first()
            else:
                income_category = Income.query.filter_by(user_id=user_id, name=category_name).first()

            if income_category:
                income_category_id = income_category.id
                transactions = CashIn.query.filter_by(income_id=income_category_id, user_id=user_id).all()
                
                total = 0
                transaction_data = []
                for transaction in transactions:
                    total += transaction.amount
                    transaction_data.append({
                        'id': transaction.id,
                        'category': category_name,
                        'amount': "{:,.2f}/=".format(float(transaction.amount)),
                        'date': transaction.date.strftime('%Y-%m-%d'),
                        'description': transaction.description
                    })

                return jsonify({'transactions': transaction_data, 
                                'total': "{:,.2f}/=".format(total)
                                }), 200
            
            else:
                return jsonify({'error': 'Catégorie introuvable pour l’utilisateur actuel'}), 404
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    category_form = IncomeCategoryForm()
    transaction_form = IncomeTransactionForm()
    income_types = IncomeType.query.all()
    category_form.incomeType.choices = [(it.id, it.name) for it in income_types]
    income_categories = Income.query.filter_by(user_id=current_user.id).all()
    transaction_form.incomeCategory.choices = [(ic.id, ic.name) for ic in income_categories]
    income_totals = calculate_income_totals_formatted_debt(current_user.id)
    total_income, individual_incomes = calculate_total_income_between_dates(current_user.id)
    income_transactions = [
        {
            'transaction_id': income['id'],
            'income_category_name': income['name'],
            'income_category_id': income['income_category_id'],
            'description': income['description'],
            'date': income['date'].strftime('%Y-%m-%d'),
            'amount': "{:,.2f}/=".format(income['amount']),
        }
        for income in individual_incomes
    ]
    today = date.today()
    start_of_month = date(today.year, today.month, 1)
    from_date_formatted = start_of_month.strftime('%b %d, %Y')
    to_date_formatted = today.strftime('%b %d, %Y')

    return render_template('income.html', 
                           category_form=category_form, 
                           transaction_form=transaction_form,
                           income_types=income_types,
                           income_categories=income_categories, 
                           income_totals=income_totals, 
                           income_transactions=income_transactions, 
                           total_income="{:,.2f}/=".format(total_income), 
                           from_date=from_date_formatted, 
                           to_date=to_date_formatted) 

@login_required
@app.route('/create_income_category', methods=['POST'])
def create_income_category():
    """
    Créez une nouvelle catégorie de revenus.

Retourne:
        json : réponse JSON indiquant la réussite ou un message d’erreur.
    """

    if request.method == 'POST':
        category_name = request.form.get('categoryName')
        income_type_id = request.form.get('incomeType')
        user_id = current_user.id
        result, income = add_income(user_id, category_name, income_type_id)

        if result is True:
            if income:
                category_id = income.id
                response_data = {
                    'message': 'Catégorie créée avec succès',
                    'category_name': category_name,
                    'category_id': category_id 
                }
                return jsonify(response_data), 200
            else:
                return jsonify({'error': 'Category not found'}), 404
        else:
            response_data = {'error': result}  
            return jsonify(response_data), 400
    else:
        return abort(405)

@login_required
@app.route('/create_income_transaction', methods=['POST'])
def create_income_transaction():
    income_category = request.form.get('incomeCategory')
    amount = request.form.get('amount')
    date = request.form.get('date')
    debtor = request.form.get('debtor')
    description = request.form.get('description')
    try:
        income_category = int(income_category)
        amount = float(amount)
    except ValueError:
        return jsonify({'error': 'Données non valides fournies'}), 400
    try:
        date_obj = datetime.strptime(date, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Données non valides fournies'}), 400
    try:
        user_id = current_user.id
        credit_to_settle = Credit.query.filter_by(debtor=debtor, user_id=user_id, is_paid=False).first()

        if not credit_to_settle and income_category == 1:
            raise ValueError("Aucun crédit impayé n’a été trouvé pour le débiteur désigné.")
        cash_in = add_cash_in_transaction(
            user_id=user_id,
            amount=amount,
            date=date_obj,
            income_id=income_category,
            description=description,
            settled_credit_id=credit_to_settle.id if credit_to_settle else None
        )

        if credit_to_settle:
            credit = Credit.query.filter_by(id=credit_to_settle.id, user_id=current_user.id).first()
            if not credit:
                return jsonify({"error": "Crédit introuvable ou non autorisé"}), 403

            if credit.is_paid:
                return jsonify({"error": "Le crédit est déjà payé"}), 400

            payment = DebtorPayment(credit_id=credit.id, amount=amount, date=date_obj)
            db.session.add(payment)

            credit.amount_paid += Decimal(amount)

            if credit.amount_paid >= credit.amount:
                credit.is_paid = True

            db.session.commit()

        income_category_name = Income.query.get(income_category).name
        response_data = {
            'message': 'Transaction de revenu réalisée avec succès',
            'transaction_id': cash_in.id,
            'income_category_name': income_category_name,
            'amount': "{:,.2f}/=".format(amount),
            'description': description,
            'date': date,
        }

        return jsonify(response_data), 201

    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@app.route('/search_income_transactions', methods=['GET'])
@login_required
def search_income_transactions() :
    '''
    Recherche de transactions de revenus par date
    '''
    user_id = current_user.id 
    start_date_str = request.args.get('from')
    end_date_str = request.args.get('to')

    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

        total_income, individual_incomes = calculate_total_income_between_dates(user_id, start_date, end_date)
        income_totals = calculate_income_totals_formatted_debt(user_id, start_date, end_date)

        response_data = {
            'total_income': str(total_income),
            'individual_incomes': individual_incomes,
            'income_totals': income_totals
        }

        return jsonify(response_data)

    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/edit_income_transaction', methods=['POST'])
@login_required
def edit_income_transaction():
    data = request.get_json()
    transaction_id = data.get('transaction_id')
    new_date_str = data.get('new_date') 
    new_amount = data.get('new_amount')
    new_description = data.get('new_description')
    new_category_id = data.get('new_category_id')
    if not (new_date_str and new_amount and new_category_id):
        return jsonify({'error': 'Veuillez fournir tous les champs obligatoires.'}), 400

    try:
        new_date = datetime.strptime(new_date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Format de date non valide. Veuillez utiliser le format AAAA-MM-JJ.'}), 400
    if new_date > datetime.now().date():
        return jsonify({'error': 'Veuillez sélectionner une date qui n’est pas dans le futur.'}), 400

    if new_amount < 0:
        return jsonify({'error': 'Veuillez saisir un montant non négatif.'}), 400

    if new_description:
        if len(new_description) > 100:
            return jsonify({'error': 'La description ne doit pas dépasser 100 caractères.'}), 400

    transaction = CashIn.query.get(transaction_id)
    if not transaction:
        return jsonify({'error': 'Transaction introuvable.'}), 404

    category = Income.query.get(new_category_id)
    if not category:
        return jsonify({'error': 'Catégorie de revenu introuvable.'}), 404

    try:
        transaction.update_transaction(new_description, new_amount, new_date, new_category_id)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erreur lors de la modification de la transaction.'}), 500

    new_category_name = Income.query.get(transaction.income_id).name

    # Return the edited transaction details in the response
    edited_transaction = {
        'transaction_id': transaction.id,
        'new_date': transaction.date.strftime('%Y-%m-%d'),
        'new_amount': "{:,.2f}/=".format(transaction.amount),
        'new_description': transaction.description,
        'new_category_id': transaction.income_id,
        'new_category_name': new_category_name,
    }

    return jsonify({'message': 'Transaction de revenu mise à jour avec succès ', ' edited_transaction': edited_transaction}), 200

@app.route('/delete_income_transaction', methods=['POST'])
@login_required
def delete_income_transaction():
    data = request.get_json()
    transaction_id = data.get('transaction_id')
    transaction = CashIn.query.get(transaction_id)
    if not transaction:
        return jsonify({'error': 'Transaction introuvable.'}), 404

    try:
        transaction.delete_transaction()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erreur lors de la suppression de la transaction.'}), 500
    return jsonify({'message': 'Transaction de revenu supprimée avec succès'}), 200


# Magement des dépenses ------------------------------------------------------------------------
@app.route('/expense', methods=['GET', 'POST'])
@login_required
def expense():
    if request.method == 'GET':
        expense_categories = Expense.query.filter_by(user_id=current_user.id).all()
        expense_totals = calculate_expense_totals(current_user.id)
        '''
        Inclure le crédit et les dettes réglées comme catégories qui excluent le revenu
        '''
        today = date.today()
        start_date = date(today.year, today.month, 1)
        end_date = date.today()
        total_amount_paid = db.session.query(func.sum(Debt.amount_payed)).filter(
            Debt.user_id == current_user.id,
            Debt.date_taken >= start_date,
            Debt.date_taken <= end_date
        ).scalar()

        if total_amount_paid is None:
            total_amount_paid = 0 
        total_amount_given = db.session.query(func.sum(Credit.amount)).filter(
            Credit.user_id == current_user.id,
            Debt.date_taken >= start_date,
            Debt.date_taken <= end_date
        ).scalar()

        if total_amount_given is None:
            total_amount_given = 0 

        expense_totals['Settled Debt'] = total_amount_paid
        expense_totals['Credit'] = total_amount_given
        formatted_expense_totals = {}
        total_expense = sum(expense_totals.values())
        for category, amount in expense_totals.items():
            formatted_amount = "{:,.2f}/=".format(amount)
            try:
                percentage = "{:.2f}".format((amount / total_expense) * 100)
            except:
                percentage = "{:.2f}".format(0)
            formatted_expense_totals[category] = (formatted_amount, percentage)
        expense_totals = formatted_expense_totals
        total_expenses, individual_expenses = calculate_total_expenses_between_dates(current_user.id)
        expense_transactions = [
            {
                'transaction_id': exp['id'],
                'expense_category_name': exp['name'],
                'expense_category_id': exp['expense_category_id'],
                'description': exp['description'],
                'date': exp['date'].strftime('%Y-%m-%d'),
                'amount': "{:,.2f}/=".format(exp['amount']), 
            }
            for index, exp in enumerate(individual_expenses)
        ]
        today = date.today()
        start_of_month = date(today.year, today.month, 1)
        from_date_formatted = start_of_month.strftime('%b %d, %Y')
        to_date_formatted = today.strftime('%b %d, %Y')
        return render_template('expense.html', 
                               expense_categories = expense_categories,
                               expense_totals = expense_totals,
                               expense_transactions = expense_transactions, 
                               total_expenses = "{:,.2f}/=".format(total_expenses),
                               from_date=from_date_formatted,
                               to_date=to_date_formatted
                               )
    else:
        '''
        Filtrer les transactions de revenus par catégorie
        '''
        try:
            category_name = request.json.get('category_name')
            user_id = current_user.id
            if   category_name == 'Credit':
                expense_category = Expense.query.filter_by(user_id=1, name=category_name).first()
            elif   category_name == 'Settled Debt':
                expense_category = Expense.query.filter_by(user_id=1, name=category_name).first()
            else:
                expense_category = Expense.query.filter_by(user_id=user_id, name=category_name).first()

            if expense_category:
                if category_name == 'Credit':
                    expense_category_id = 1

                else:
                    expense_category_id = expense_category.id
                transactions = CashOut.query.filter_by(expense_id=expense_category_id, user_id=user_id).all()
                total_expenses = 0
                transaction_data = []
                for transaction in transactions:
                    transaction_data.append({
                        'id': transaction.id,
                        'category': category_name,
                        'amount': "{:,.2f}/=".format(float(transaction.amount)),
                        'date': transaction.date.strftime('%Y-%m-%d'),
                        'description': transaction.description
                    })
                    total_expenses += transaction.amount

                return jsonify({'transactions': transaction_data,
                                'total_expenses':"{:,.2f}/=".format(total_expenses)
                                })
            
            else:
                return jsonify({'error': 'Catégorie introuvable pour l’utilisateur actuel'}), 404
        except Exception as e:
            return jsonify({'error': str(e)}), 500

@app.route('/create_expense_category', methods=['POST'])
@login_required
def create_expense_category():
    user_id = current_user.id
    data = request.get_json()
    expense_name = data.get('categoryName')

    if not expense_name:
        return jsonify({"success": False, "message": "Le nom de la catégorie ne peut pas être vide."}), 400

    if len(expense_name) > 100:
        return jsonify({"success": False, "message": "Le nom de la catégorie ne doit pas dépasser 100 caractères."}), 400
    result = add_expense(user_id, expense_name)

    if isinstance(result, Expense):
        expense = result
        return jsonify({"success": True, "name": expense.name, "id": expense.id})
    return jsonify({"success": False, "message": "Une erreur s’est produite lors de l’ajout de la dépense."}), 500

@login_required
@app.route('/create_expense_transaction', methods=['POST'])
def create_expense_transaction():
    expense_category = request.form.get('expenseCategory')
    amount = request.form.get('amount')
    date = request.form.get('date')
    creditor = request.form.get('creditor')
    description = request.form.get('description')
    try:
        expense_category = int(expense_category)
        amount = float(amount)
    except ValueError:
        return jsonify({'error': 'Données non valides fournies'}), 400
    try:
        date_obj = datetime.strptime(date, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Date non valides fournies'}), 400
    try:
        user_id = current_user.id
        current_month = datetime.now().month
        current_year = datetime.now().year
 
        current_budget = Budget.query.filter_by(user_id=user_id, month=current_month, year=current_year).first()

        if current_budget:
            budget_expense = BudgetExpense.query.filter_by(budget_id=current_budget.id, expense_id=expense_category).first()
            if budget_expense:
                print('Budget Charge avant transaction', budget_expense.spent_amount)
                try:
                    amount = int(amount) if amount else 0.0
                    budget_expense.update_spent_amount(amount)
                    db.session.commit()
                    print('Budget Charge apres transaction', budget_expense.spent_amount)
                except Exception as e:
                    print('Dépenses budgétaires non mises à jour')
                    db.session.rollback() 
        cash_out = add_cash_out_transaction(
            user_id=user_id,
            amount=amount,
            date=date_obj,
            expense_id=expense_category,
            description=description,
        )

        expense_category_name = Expense.query.get(expense_category).name
        response_data = {
            'message': 'Expense transaction created successfully',
            'transaction_id': cash_out.id,
            'expense_category_name': expense_category_name,
            'amount': "{:,.2f}/=".format(amount),
            'description': description,
            'date': date,
        }

        return jsonify(response_data), 201

    except ValueError as e:
        return jsonify({'error': str(e)}), 400

    except Exception as e:
        return jsonify({'error': 'Une erreur s’est produite lors de la création de la transaction de revenu'}), 500

@app.route('/search_expense_transactions', methods=['GET'])
@login_required
def search_expense_transactions():
    '''
    Rechercher des transactions de dépenses par date
    '''
    user_id = current_user.id 
    start_date_str = request.args.get('from')
    end_date_str = request.args.get('to')

    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

        total_expense, individual_expenses = calculate_total_expenses_between_dates(
            user_id, start_date, end_date
        )
        expense_totals = calculate_expense_totals(current_user.id, start_date, end_date)
        '''
        Inclure le crédit comme une catégorie qui contribue aux dépenses
        '''
        total_amount_given = db.session.query(func.sum(Credit.amount)).filter(
            Credit.user_id == user_id,
            Credit.date_taken >= start_date,
            Credit.date_taken <= end_date
        ).scalar()

        if total_amount_given is None:
            total_amount_given = 0
        expense_totals['Credit'] = total_amount_given

        '''
        Inclure les dettes réglées comme une catégorie qui contribue aux dépenses
        '''
        total_amount_paid = db.session.query(func.sum(CashOut.amount)).filter(
            CashOut.expense_id==2,
            CashOut.user_id == user_id,
            CashOut.date >= start_date,
            CashOut.date <= end_date
        ).scalar()

        if total_amount_paid is None:
            total_amount_paid = 0 
        
        expense_totals['Settled Debt'] = total_amount_paid
        formatted_expense_totals = {}
        total_expense = sum(expense_totals.values())
        for category, amount in expense_totals.items():
            formatted_amount = "{:,.2f}/=".format(amount)
            try:
                percentage = "{:.2f}".format((amount / total_expense) * 100)
            except:
                percentage = "{:.2f}".format(0)
            formatted_expense_totals[category] = (formatted_amount, percentage)
        expense_totals = formatted_expense_totals

        response_data = {
            'total_expense': str(total_expense),
            'individual_expenses': individual_expenses,
            'expense_totals': expense_totals
        }

        return jsonify(response_data)

    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/edit_expense_transaction', methods=['POST'])
@login_required
def edit_expense_transaction():
    data = request.get_json()
    transaction_id = data.get('transaction_id')
    new_date_str = data.get('new_date')
    new_amount = data.get('new_amount')
    new_description = data.get('new_description')
    expense_id = data.get('expense_id')
    amount_diff = data.get('amount_diff')
    if not (new_date_str and new_amount):
        return jsonify({'error': 'Veuillez fournir tous les champs obligatoires.'}), 400
    try:
        new_date = datetime.strptime(new_date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Format de date non valide. Veuillez utiliser le format AAAA-MM-JJ.'}), 400
    if new_date > datetime.now().date():
        return jsonify({'error': 'Veuillez sélectionner une date qui n’est pas dans le futur.'}), 400
    if new_amount < 0:
        return jsonify({'error': 'Veuillez saisir un montant non négatif.'}), 400
    if new_description:
        if len(new_description) > 100:
            return jsonify({'error': 'La description ne doit pas dépasser 100 caractères.'}), 400
    transaction = CashOut.query.get(transaction_id)
    if not transaction:
        return jsonify({'error': 'Transaction introuvable.'}), 404
    new_month = get_month_name(new_date.month)
    new_year = new_date.year
    budget = Budget.query.filter_by(
        user_id=current_user.id,
        month=new_month,
        year=new_year
    ).first()

    if budget:
        budget_expense = BudgetExpense.query.filter_by(
            budget_id=budget.id,
            expense_id=expense_id
        ).first()
 
        if budget_expense:
            try:     
                if amount_diff < 0:
                    budget_expense.spent_amount -= abs(amount_diff)
                elif amount_diff > 0:
                    budget_expense.update_spent_amount(amount_diff)
                db.session.commit()

            except Exception as e:
                db.session.rollback()
                return jsonify({'error': 'Erreur lors de la mise à jour du montant dépensé dans BudgetExpense.'}), 500

    try:
        transaction.update_transaction(new_description, new_amount, new_date, int(expense_id))
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erreur lors de la modification de la transaction.'}), 500
    
    new_category_name = Expense.query.get(transaction.expense_id).name
    edited_transaction = {
        'transaction_id': transaction.id,
        'new_date': transaction.date.strftime('%Y-%m-%d'),
        'new_amount': "{:,.2f}/=".format(transaction.amount),
        'new_description': transaction.description,
        'new_category_id': transaction.expense_id,
        'new_category_name': new_category_name,
    }

    return jsonify({'message': 'Transaction de dépense mise à jour avec succès', 'edited_transaction': edited_transaction}), 200

@app.route('/delete_expense_transaction', methods=['POST'])
@login_required
def delete_expense_transaction():
    data = request.get_json()
    transaction_id = data.get('transaction_id')
    transaction = CashOut.query.get(transaction_id)

    if not transaction:
        return jsonify({'error': 'Transaction introuvable.'}), 404

    try:
        if transaction.date and transaction.expense_id:
            transaction_month = transaction.date.month
            transaction_year = transaction.date.year
            budget = Budget.query.filter_by(
                user_id=current_user.id,
                month=transaction_month,
                year=transaction_year
            ).first()

            if budget:
                budget_expense = BudgetExpense.query.filter_by(
                    budget_id=budget.id,
                    expense_id=transaction.expense_id
                ).first()

                if budget_expense:
                    budget_expense.spent_amount -= transaction.amount
                    db.session.commit()
        transaction.delete_transaction()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erreur lors de la suppression de la transaction.'}), 500
    return jsonify({'message': 'Transaction de dépense supprimée avec succès'}), 200


# Budget Magement ------------------------------------------------------------------------
def get_month_name(month_number):
    month_names = [
        'Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
        'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'
    ]
    if 1 <= month_number <= 12:
        return month_names[month_number - 1]
    else:
        return None
    
@app.route('/budget', methods=['GET', 'POST'])
@login_required
def budget():
    user_id = current_user.id
    current_year = int(datetime.now().year)
    current_month = int(datetime.now().month)
    if request.method == 'POST':
        new_budget = create_budget(user_id, current_year, current_month)
        return jsonify({
            'id': new_budget.id,
            'user_id': new_budget.user_id,
            'year': new_budget.year,
            'month': new_budget.month
        })
    expenses = Expense.query.filter_by(user_id=user_id).all()
    budgets = Budget.query.filter_by(user_id=user_id).all()

    budget_with_totals = []
    for budget in budgets:
        budget_expenses = BudgetExpense.query.filter_by(budget_id=budget.id).all()

        total_expected_amount = sum(budget_expense.expected_amount for budget_expense in budget_expenses)
        total_actual_amount = sum(budget_expense.spent_amount for budget_expense in budget_expenses)

        budget_with_totals.append({
            'id': budget.id,
            'user_id': budget.user_id,
            'year': budget.year,
            'month': budget.month,
            'total_expected_amount': total_expected_amount,
            'total_actual_amount': total_actual_amount
        })

    current_budget = Budget.query.filter_by(user_id=user_id, year=current_year, month=current_month).first()

    budget_expenses_with_names = []
    current_total_expected_amount = 0
    current_total_actual_amount = 0
    expense_count = 0
    if current_budget:
        start_date = date(current_year, current_month, 1)
        end_date = date.today()
        budget_expenses = BudgetExpense.query.filter_by(budget_id=current_budget.id).all()
        for budget_expense in budget_expenses:
            expense_count += 1
            expense = Expense.query.get(budget_expense.expense_id)
            total_spent_amount = db.session.query(func.sum(CashOut.amount)).filter(
                CashOut.user_id == user_id,
                CashOut.expense_id == expense.id,
                CashOut.date >= start_date,
                CashOut.date <= end_date
            ).scalar()
            if budget_expense.spent_amount == 0:
                amt = total_spent_amount if total_spent_amount else 0.0
                budget_expense.update_spent_amount(amt)
                db.session.commit()

            budget_expense=BudgetExpense.query.get(budget_expense.id)
            budget_expenses_with_names.append({
                'id': budget_expense.id,
                'budget_id': budget_expense.budget_id,
                'expense_id': budget_expense.expense_id,
                'expected_amount': budget_expense.expected_amount,
                'spent_amount': budget_expense.spent_amount,
                'expense_name': expense.name
            })

        current_total_expected_amount += sum(budget_expense.expected_amount for budget_expense in budget_expenses)
        current_total_actual_amount += sum(budget_expense.spent_amount for budget_expense in budget_expenses)
    months = {
        1 : 'Janvier',
        2 : 'Février',
        3 : 'Mars',
        4 : 'Avril',
        5 : 'Mai',
        6 : 'Juin',
        7 : 'Juillet',
        8 : 'Août',
        9 : 'Septembre',
        10 : 'Octobre',
        11 : 'Novembre',
        12 : 'Décembre'
    }
    return render_template('budget.html', expenses=expenses, 
                           current_budget=current_budget, 
                           budget_expenses=budget_expenses_with_names,
                           budgets=budget_with_totals,
                           current_total_expected_amount=current_total_expected_amount,
                           current_total_actual_amount=current_total_actual_amount,
                           expense_count=expense_count,
                           months=months
                           )

@app.route('/create_budget_expense', methods=['POST'])
@login_required
def create_budget_expense():
    try:
        data = request.get_json()
        expense_id = data.get('expense_id')
        expected_amount = data.get('expected_amount')
        budgetId = data.get('budgetId')
        if not expense_id or not budgetId or expected_amount is None or expected_amount < 0:
            return jsonify({'error': 'Donnee invalide'}), 400
        budget_expense = BudgetExpense(
            budget_id=budgetId,
            expense_id=expense_id,
            expected_amount=expected_amount,
            spent_amount=0.0
        )
        db.session.add(budget_expense)
        db.session.commit()
        expense = Expense.query.get(expense_id)
        budget = Budget.query.get(budgetId)
        response_data = {
            'message': 'Dépense budgétaire créée avec succès',
            'expense_id': expense.id,
            'expense_name': expense.name,
            'budget_id': budget.id,
            'budget_expense_id': budget_expense.id,
            'expected_amount': "{:,.2f}/=".format(budget_expense.expected_amount),
            'actual_amount': "{:,.2f}/=".format(0.00)
        }
        return jsonify(response_data), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/search_budget_expenses/<int:budget_id>', methods=['GET'])
@login_required
def search_budget_expenses(budget_id):
    try:
        budget = Budget.query.get(budget_id)
        if not budget:
            return jsonify({'error': 'Budget introuvable'}), 404
        budget_expenses = BudgetExpense.query.filter_by(budget_id=budget_id).all()
        total_expected_amount = sum(expense.expected_amount for expense in budget_expenses)
        total_spent_amount = sum(expense.spent_amount for expense in budget_expenses)
        expense_count = 0
        budget_expenses_data = []
        for expense in budget_expenses:
            expense_count += 1
            budget_expenses_data.append({
                'id': expense.id,
                'budget_id': expense.budget_id,
                'expense_id': expense.expense_id,
                'expected_amount':  "{:,.2f}/=".format(expense.expected_amount),
                'spent_amount':  "{:,.2f}/=".format(expense.spent_amount),
                'percentage': "{:.2f}".format((expense.spent_amount / expense.expected_amount) * 100),
                'expense_name': Expense.query.get(expense.expense_id).name
            })

        if isinstance(budget.month, int):
            budget.month = get_month_name(budget.month)
        return jsonify({
            'budget_expenses': budget_expenses_data,
            'total_expected_amount': total_expected_amount,
            'total_spent_amount': total_spent_amount,
            'percent': "{:.2f}%".format((total_spent_amount / total_expected_amount) * 100),
            'expense_count': expense_count,
            'year': budget.year,
            'month': budget.month,
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/search_budget_by_year_month', methods=['POST'])
@login_required
def search_budget_by_year_month():
    data = request.get_json()
    year = data.get('year')
    month = data.get('month')

    month = int(month)
    
    try:
        budget = Budget.query.filter_by(year=year, month=month, user_id=current_user.id).first()
        if not budget:
            return jsonify({'error': 'Budget introuvable pour l’année et le mois spécifiés'}), 404
        budget_expenses = BudgetExpense.query.filter_by(budget_id=budget.id).all()

        total_expected_amount = sum(expense.expected_amount for expense in budget_expenses)
        total_spent_amount = sum(expense.spent_amount for expense in budget_expenses)

        expense_count = 0
        budget_expenses_data = []
        for expense in budget_expenses:
            expense_count += 1
            budget_expenses_data.append({
                'id': expense.id,
                'budget_expense_id': expense.id,
                'budget_id': expense.budget_id,
                'expense_id': expense.expense_id,
                'expected_amount': "{:,.2f}/=".format(expense.expected_amount),
                'spent_amount':  "{:,.2f}/=".format(expense.spent_amount),
                'percentage': "{:.2f}".format((expense.spent_amount / expense.expected_amount) * 100),
                'expense_name': Expense.query.get(expense.expense_id).name 
            })

        return jsonify({
            'budget_id': budget.id,
            'year': budget.year,
            'month': budget.month,
            'budget_expenses': budget_expenses_data,
            'total_expected_amount': total_expected_amount,
            'total_spent_amount': total_spent_amount,
            'percent': "{:.2f}%".format((total_spent_amount / total_expected_amount) * 100),
            'expense_count': expense_count
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/edit_budget_expense', methods=['POST'])
@login_required
def edit_budget_expense():
    try:
        data = request.get_json()
        budget_expense_id = data['budget_expense_id']
        budget_id = data['budget_id']
        expenseId = data['expenseId']
        edited_expected_amount = data['edited_expected_amount']

        budget_expense = db.session.query(BudgetExpense).filter_by(
            id=budget_expense_id,
            budget_id=budget_id,
            expense_id=expenseId
        ).first()

        if budget_expense:
            budget_expense.expected_amount = edited_expected_amount

            db.session.commit()

            budget_expense = db.session.query(BudgetExpense).filter_by(
                id=budget_expense_id,
                budget_id=budget_id,
                expense_id=expenseId
            ).first()
            edited_expected_amount = "{:,.2f}".format(budget_expense.expected_amount)

            return jsonify({'updated_expected_amount': edited_expected_amount, 
                            'message': 'BudgetExpense modifié avec succès'}), 200

        else:
            return jsonify({'error': 'BudgetExpense introuvable'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/delete_budget_expense', methods=['POST'])
@login_required
def delete_budget_expense():
    try:
        data = request.get_json()
        budget_expense_id = data['budget_expense_id']

        budget_expense = db.session.query(BudgetExpense).filter_by(id=budget_expense_id).first()

        if budget_expense:
            db.session.delete(budget_expense)
            db.session.commit()
            return jsonify({'message': 'BudgetExpense supprimé avec succès'}), 200

        else:
            return jsonify({'error': 'BudgetExpense introuvable'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
# Credit Magement ------------------------------------------------------------------------
@app.route('/credit', methods=['GET', 'POST'])
@login_required
def credit():
    if request.method == 'POST':
        try:
            data = request.get_json()
            debtor = data.get('debtor')
            amount = data.get('amount')
            date_taken = data.get('dateTaken')
            date_due = data.get('dateDue')
            description = data.get('description')
            debtor = titlecase(debtor.strip())
            try:
                date_taken = datetime.strptime(date_taken, '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': 'Date de prise non valide fournie'}), 400
            
            if date_due:
                try:
                    date_due = datetime.strptime(date_due, '%Y-%m-%d').date()
                except ValueError:
                    return jsonify({'error': 'Invalid date due provided'}), 400

            # Create a new Credit record
            new_credit = Credit(
                user_id=current_user.id,
                debtor=debtor,
                amount=amount,
                date_taken=date_taken,
                date_due=date_due,
                description=description
            )

            # Add and commit the new credit record to the database
            db.session.add(new_credit)

            cash_out = CashOut(
                user_id=current_user.id,
                expense_id=1,
                amount=amount,
                date=date_taken,
                description=description
            )

            db.session.add(cash_out)

            db.session.commit()

            # Return the newly created credit record in JSON format
            response_data = {
                'id': new_credit.id,
                'user_id': new_credit.user_id,
                'debtor': new_credit.debtor,
                'amount': "{:,.2f}/=".format(new_credit.amount),
                'date_taken': new_credit.date_taken.strftime('%Y-%m-%d'),
                'date_due': new_credit.date_due.strftime('%Y-%m-%d') if new_credit.date_due else None,
                'description': new_credit.description,
                'is_paid': new_credit.is_paid,
                'amount_paid': "{:,.2f}/=".format(new_credit.amount_paid)
            }

            return jsonify(response_data), 201  # Return 201 status code for successful creation

        except Exception as e:
            # Handle errors and return an error response
            error_message = str(e)
            return jsonify({'error': error_message}), 400  # Return 400 status code for bad request
    # Fetch all rows in the Credit model for the current user, ordered by date_taken
    credits = Credit.query.filter_by(user_id=current_user.id).order_by(Credit.date_taken.desc()).all()
    total_amount_paid = db.session.query(func.sum(Credit.amount_paid)).filter(
        Credit.user_id == current_user.id,
    ).scalar()

    total_amount_owed = db.session.query(func.sum(Credit.amount)).filter(
        Credit.user_id == current_user.id,
    ).scalar()

    if total_amount_paid is None:
        total_amount_paid = 0 

    if total_amount_owed is None:
        total_amount_owed = 0 
    
    return render_template('credit.html', 
                           credits=credits,
                           total_amount_owed=total_amount_owed,
                           total_amount_paid=total_amount_paid)

@app.route('/credit/settle', methods=['POST'])
@login_required
def settle_credit():
    try:
        data = request.json
        credit_id = int(data['creditId'])
        amount_to_pay = data['amountToPay'] 
        date_paid_str = data['datePaid']
        date_paid = datetime.strptime(date_paid_str, '%Y-%m-%d').date() 

        credit = Credit.query.filter_by(id=credit_id, user_id=current_user.id).first()

        if not credit:
            return jsonify({"error": "Credit not found or unauthorized"}), 403

        if credit.is_paid:
            return jsonify({"error": "Credit is already paid"}), 400

        payment = DebtorPayment(credit_id=credit_id, amount=amount_to_pay, date=date_paid)
        db.session.add(payment)

        credit.amount_paid += amount_to_pay

        if credit.amount_paid >= credit.amount:
            credit.is_paid = True

        # Create a CashIn transaction
        cash_in = CashIn(
            user_id=current_user.id,
            income_id=2,
            amount=amount_to_pay,
            date=date_paid,
            description="settling {}'s credit".format(credit.debtor), 
            settled_credit_id=credit.id
        )
        db.session.add(cash_in)
        db.session.commit()

        progress = round((credit.amount_paid / credit.amount) * 100, 2) 

        return jsonify({
            "amountPaid": "{:,.2f}/=".format(credit.amount_paid),
            "progress": "{}%".format(progress),
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# Debt Magement ------------------------------------------------------------------------
@app.route('/debt', methods=['GET', 'POST'])
@login_required
def debt():
    if request.method == 'POST':
        try:
            data = request.get_json()

            # Extract data from JSON
            creditor = data.get('debtor')
            amount = data.get('amount')
            date_taken = data.get('dateTaken')
            date_due = data.get('dateDue')
            description = data.get('description')

            # Trim and convert debtor name to title case
            creditor = titlecase(creditor.strip())

            # Convert the date string to a Python date object
            try:
                date_taken = datetime.strptime(date_taken, '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': 'Invalid date taken provided'}), 400
            
            if date_due:
                try:
                    date_due = datetime.strptime(date_due, '%Y-%m-%d').date()
                except ValueError:
                    return jsonify({'error': 'Invalid date due provided'}), 400

            # Create a new Debt record
            new_debt = Debt(
                user_id=current_user.id,
                creditor=creditor,
                amount=amount,
                date_taken=date_taken,
                date_due=date_due,
                description=description
            )

            # Add and commit the new debt record to the database
            db.session.add(new_debt)

            cash_in = CashIn(
                user_id=current_user.id,
                income_id=1,
                amount=amount,
                date=date_taken,
                description=description
            )

            # Add and commit the new cashin record to the database
            db.session.add(cash_in)  
            db.session.commit()

            # Return the newly created debt record in JSON format
            response_data = {
                'id': new_debt.id,
                'user_id': new_debt.user_id,
                'debtor': new_debt.creditor,
                'amount': "{:,.2f}/=".format(new_debt.amount),
                'date_taken': new_debt.date_taken.strftime('%Y-%m-%d'),
                'date_due': new_debt.date_due.strftime('%Y-%m-%d') if new_debt.date_due else None,
                'description': new_debt.description,
                'is_paid': new_debt.is_paid,
                'amount_paid': "{:,.2f}/=".format(new_debt.amount_payed)
            }

            return jsonify(response_data), 201

        except Exception as e:
            # Handle errors and return an error response
            error_message = str(e)
            return jsonify({'error': error_message}), 400 
         
    # Fetch all rows in the Credit model for the current user, ordered by date_taken
    debits = Debt.query.filter_by(user_id=current_user.id).order_by(Debt.date_taken.desc()).all()

    total_amount_returned = 0

    total_amount_received = 0

    for debit in debits:
        total_amount_received += debit.amount
        total_amount_returned += debit.amount_payed

    if total_amount_returned is None:
        total_amount_returned = 0.00 

    if total_amount_received  is None:
        total_amount_received = 0.00 
    
    return render_template('debt.html', 
                           debits=debits,
                           total_amount_received=total_amount_received,
                           total_amount_returned=total_amount_returned)

@app.route('/debt/settle', methods=['POST'])
@login_required
def settle_debt():
    try:
        data = request.json
        debt_id = int(data['creditId'])
        amount_to_pay = data['amountToPay'] 
        date_paid_str = data['datePaid']
        date_paid = datetime.strptime(date_paid_str, '%Y-%m-%d').date()

        debt = Debt.query.filter_by(id=debt_id, user_id=current_user.id).first()

        if not debt:
            return jsonify({"error": "debt not found or unauthorized"}), 403

        if debt.is_paid:
            return jsonify({"error": "Credit is already paid"}), 400

        payment = CreditorPayment(debt_id=debt_id, amount=amount_to_pay, date=date_paid)
        db.session.add(payment)

        debt.amount_payed += Decimal(amount_to_pay)

        if debt.amount_payed >= debt.amount:
            credit.is_paid = True

        # Create a CashOut transaction
        cash_out = CashOut(
            user_id=current_user.id,
            expense_id=2,
            amount=amount_to_pay,
            date=date_paid,
            description="settling {}'s debt".format(debt.creditor), 
            settled_debt_id=debt.id 
        )

        db.session.add(cash_out)
        db.session.commit()

        progress = round((debt.amount_payed / debt.amount) * 100, 2) 

        return jsonify({
            "amountPaid": "{:,.2f}/=".format(debt.amount_payed),
            "progress": "{}%".format(progress),
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
 
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        initialize_default_income_types()

    app.run(debug=True)


