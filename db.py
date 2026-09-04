import mysql.connector

from config import DB_CONFIG


def get_connection():
    """Open a new connection to MySQL and return it."""
    return mysql.connector.connect(**DB_CONFIG)

# **DB_CONFIG is the same as mysql.connector.connect(host="localhost", port=3306, user="root", password="", database="bookshelf")