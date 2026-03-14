import mysql.connector
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    db = mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "gym_db")
    )

    # Cursor (dictionary=True makes results easier to use)
    cursor = db.cursor()

    print("✅ Database connected successfully")

except mysql.connector.Error as err:
    print("❌ Database connection failed:", err)
    db = None
    cursor = None