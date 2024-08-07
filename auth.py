from models import db
from werkzeug.security import generate_password_hash, check_password_hash

def register_user(first_name, last_name, password, email):
    """
    Register a new user.

    Args:
        first_name (str): The first name of the user.
        last_name (str): The last name of the user.
        password (str): The user's chosen password.
        email (str): The email address of the user.

    Returns:
        User/str: The authenticated User object if successful, otherwise an error message.
    """
    from models import User
    
    hashed_password = generate_password_hash(password)
    user = User(first_name=first_name, last_name=last_name, password=hashed_password, email=email)
    try:
        db.session.add(user)
        db.session.commit()
        return user
    except Exception as e:
        db.session.rollback()
        return str(e)

def authenticate_user(email, password):
    """
    Authenticate a user.

    Args:
        username (str): The username of the user.
        password (str): The password provided by the user.

    Returns:
        User/None: The authenticated User object if successful, otherwise None.

    """
    from models import User

    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password, password):
        return user
    return None
