import mysql.connector

from infrastructure.config import DB_CONFIG


def get_connection():
    """Open a new connection to MySQL and return it."""
    return mysql.connector.connect(**DB_CONFIG)
