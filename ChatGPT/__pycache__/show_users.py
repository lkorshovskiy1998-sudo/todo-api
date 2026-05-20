import sqlite3

conn = sqlite3.connect("users.db")

cursor = conn.cursor()

min_age = int(input("Мінімальний вік: "))

cursor.execute("SELECT * FROM users WHERE age >= ?", (min_age,))

users = cursor.fetchall()

conn.close()


for u in users:
    print(f"{u[0]} - {u[1]} - {u[2]} - {u[3]}")