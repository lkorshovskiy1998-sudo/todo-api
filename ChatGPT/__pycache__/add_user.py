import sqlite3

conn = sqlite3.connect("users.db")

cursor = conn.cursor()

cursor.execute("""
INSERT INTO users (name, age, city)
VALUES (?, ?, ?)
""", ("Vova", 55, "Kalush"))

conn.commit()

conn.close()

print("Користувача додано")