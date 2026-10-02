from flask import render_template, session, redirect, flash
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import sqlite3

# Setup database
DATABASE = "database.db"

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row  # Access columns by name
    return db

# User login functions

def hash_password(password):
    return generate_password_hash(password)

def check_password(hash, password):
    return check_password_hash(hash, password)

def check_characters_username(username):
    if len(username) < 3 or len(username) > 15:
        return False

    for char in username:
        if not (char.isalnum() or char in "_-"):
            return False
    return True

def check_characters_password(password):
    if len(password) < 6 or len(password) > 30:
        return False
    
    for char in password:
        if char in [" ", ",", ";", "\"", "\'"]:
            return False
    return True

def login_required(f):

    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get("user_id"):
            flash("You are not logged in yet!", "error")
            return redirect("/")
        return f(*args, **kwargs)
    
    return wrapper


