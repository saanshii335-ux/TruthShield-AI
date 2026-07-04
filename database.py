import sqlite3

conn = sqlite3.connect("detections.db")
print("Database created successfully")

conn.close()

import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="fake_post_detector"
)

print("Database connected successfully!")

conn.close()

import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="fake_post_detector"
)

cursor = conn.cursor()

sql = """
INSERT INTO detections
(post_text, prediction, confidence)
VALUES (%s, %s, %s)
"""

values = (
    "This is a test social media post",
    "FAKE",
    92.5
)

cursor.execute(sql, values)

conn.commit()

print("Record inserted successfully!")

conn.close()