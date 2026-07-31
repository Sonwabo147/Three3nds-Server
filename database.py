import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

DB_IP = os.getenv("DB_IP")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")


def db_conn():

    return mysql.connector.connect(
        host=DB_IP,
        user=DB_USER,
        password=DB_PASSWORD,
        database="demz"
    )