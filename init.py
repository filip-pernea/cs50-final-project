import sqlite3
from functions import hash_password

from settings import DEFAULT_NAME, DEFAULT_USERNAME, DEFAULT_PASSWORD, DEFAULT_BIO, DEFAULT_ROLE

connection = sqlite3.connect('database.db')
with open('schema.sql') as f:
    connection.executescript(f.read())

connection.execute("INSERT INTO users (full_name, bio, username, password, role) VALUES (?, ?, ?, ?, ?)", [DEFAULT_NAME, DEFAULT_BIO, DEFAULT_USERNAME, hash_password(DEFAULT_PASSWORD), DEFAULT_ROLE])

connection.commit()
connection.close()
