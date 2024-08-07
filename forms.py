from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, TextAreaField, DateField, FloatField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Regexp

class RegistrationForm(FlaskForm):
    """
    Represents a registration form.
    
    Attributes:
        first_name (StringField): Field for entering the first name.
        last_name (StringField): Field for entering the last name.
        email (StringField): Field for entering an email address.
        password (PasswordField): Field for entering a password.
        confirm_password (PasswordField): Field for confirming the password.
        submit (SubmitField): Button for submitting the form.
    """
    
    first_name = StringField('Nom', validators=[DataRequired(), Length(min=2, max=50), Regexp('^[A-Za-z]*$', message='Seuls les caractères alphabétiques sont autorisés.')],
                             render_kw={"autocomplete": "off", "class": "form-control", "placeholder": "admin", "aria-label": "First name"})
    last_name = StringField('Prenom', validators=[DataRequired(), Length(min=2, max=50), Regexp('^[A-Za-z]*$', message='Seuls les caractères alphabétiques sont autorisés.')],
                            render_kw={"autocomplete": "off", "class": "form-control", "placeholder": "user", "aria-label": "Prenom"})
    email = StringField('Email', validators=[DataRequired(), Email()],
                        render_kw={"autocomplete": "off", "class": "form-control", "placeholder": "user@example.com", "aria-label": "Email"})
    password = PasswordField('Mot de passe', validators=[DataRequired(), Length(min=8), Regexp('^(?=.*[a-z])(?=.*[A-Z])(?=.*\\d)(?=.*[@$!%*?&])[A-Za-z\\d@$!%*?&]*$', message='Le mot de passe doit contenir au moins une lettre majuscule, une lettre minuscule, un chiffre et un caractère spécial.')],
                             render_kw={"autocomplete": "off", "class": "form-control", "placeholder": "Password", "aria-label": "Password"})
    confirm_password = PasswordField('Confirmer le mot de passe', validators=[DataRequired(), EqualTo('password')],
                                     render_kw={"autocomplete": "off", "class": "form-control", "placeholder": "Confirmer le mot de passe", "aria-label": "Confirmer le mot de passe"})
    submit = SubmitField('Se Connecter', render_kw={"class": "btn btn-primary", "id": "registration-submit-button"})

class LoginForm(FlaskForm):
    """
    Represents a login form.
    
    Attributes:
        email (StringField): Field for entering an email address.
        password (PasswordField): Field for entering a password.
        submit (SubmitField): Button for submitting the form.
    """
    
    email = StringField('Email', validators=[DataRequired(), Email()],
                        render_kw={"autocomplete": "off", "class": "form-control", "placeholder": "johndoe@example.com", "aria-label": "Email"})
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8), Regexp('^(?=.*[a-z])(?=.*[A-Z])(?=.*\\d)(?=.*[@$!%*?&])[A-Za-z\\d@$!%*?&]*$', message='Password must contain at least one uppercase letter, one lowercase letter, one digit, and one special character.')],
                             render_kw={"autocomplete": "off", "class": "form-control", "placeholder": "Password", "aria-label": "Password"})
    submit = SubmitField('S identifier', render_kw={"class": "btn btn-primary", "id": "registration-submit-button"})

class IncomeCategoryForm(FlaskForm):
    """
    Represents a form for adding an income category.

    Attributes:
        categoryName (StringField): Field for entering the category name.
        incomeType (SelectField): Dropdown for choosing an income type.
    """
    
    categoryName = StringField('Nom de la catégorie', validators=[DataRequired()])
    incomeType = SelectField('Choisissez le type de revenu', coerce=int)

class IncomeTransactionForm(FlaskForm):
    """
    Represents a form for adding an income transaction.

    Attributes:
        incomeCategory (SelectField): Dropdown for choosing a category.
        amount (FloatField): Field for entering the transaction amount.
        date (DateField): Field for entering the transaction date.
        debtor (SelectField): Dropdown for choosing a debtor (optional).
        description (TextAreaField): Field for entering a transaction description (optional).
    """
    
    incomeCategory = SelectField('Choisir une catégorie', coerce=int)
    amount = FloatField('Montant', validators=[DataRequired()])
    date = DateField('Date', validators=[DataRequired()])
    debtor = SelectField('Débiteur (facultatif)')
    description = TextAreaField('Description (optionelle)')
