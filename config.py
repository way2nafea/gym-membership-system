import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="nafu123",
    database="gym_management"
)

cursor = db.cursor()