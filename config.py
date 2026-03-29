import mysql.connector
import os
from mysql.connector import Error
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "gym_management")
DB_PORT = int(os.getenv("DB_PORT", "3306"))


def get_connection():
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            port=DB_PORT,
            auth_plugin="mysql_native_password",
            connection_timeout=10,
        )
        if conn.is_connected():
            return conn
    except Error as err:
        print("❌ DB connection failed:", err)
        raise


try:
    db = get_connection()
    cursor = db.cursor(buffered=True, dictionary=False)
    print("✅ Database connected successfully")

    # schema fix for password length to avoid 1406 error on hashed password
    try:
        cursor.execute("ALTER TABLE users MODIFY password VARCHAR(255) NOT NULL")
        cursor.execute("ALTER TABLE admin MODIFY password VARCHAR(255) NOT NULL")
        db.commit()
        print("✅ Password columns set to VARCHAR(255)")
    except Exception:
        # ignore if already modified or fails for any reason
        pass

except Exception:
    db = None
    cursor = None