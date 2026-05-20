import sqlite3
from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route("/users", methods=["GET"])
def get_users():
    conn = sqlite3.connect("users.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    result = [dict(u) for u in users]

    conn.close()

    return jsonify(result)

@app.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    conn = sqlite3.connect("users.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))

    user = cursor.fetchone()

    conn.close()

    if user is not None:
        return jsonify(dict(user))
    else:
        return jsonify({
            "message": "Користувача не знайдено"
        }), 404

@app.route("/users", methods=["GET"])
def get_filter():
    min_age = request.args.get("min_age")
    search_city = request.args.get("city")
    search_name = request.args.get("name")
    limit = request.args.get("limit")
    offset = request.args.get("offset")
    
    #сортування
    sort = request.args.get("sort")
    allowed_sorts = {
        "age": "age ASC",
        "age_desc": "age DESC",
        "name": "name ASC",
        "name_desc": "name DESC",
        "city": "city ASC",
        "city_desc": "city DESC"
    }
    #-----------------


    #строрення запиту у БД
    query = "SELECT * FROM users"
    conditions = []
    params = []

    if min_age is not None:
        conditions.append("age >= ?")
        params.append(int(min_age))

    if search_city is not None:
        conditions.append("city = ?")
        params.append(search_city)

    if search_name is not None:
        conditions.append("name LIKE ?")
        params.append(f"%{search_name}%")

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    if sort in allowed_sorts:
        query += " ORDER BY " + allowed_sorts[sort]

    if limit is not None:
        query += " LIMIT ?"
        params.append(int(limit))
        
        if offset is not None:
            query += " OFFSET ?"
            params.append(int(offset))

    conn = sqlite3.connect("users.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(query, params)
    users = cursor.fetchall()

    conn.close()

    result = [dict(u) for u in users]

    return jsonify(result)


@app.route("/users", methods=["POST"])
def add_user():
    data = request.json

    #перевірка полів
    if not data.get("name"):
        return jsonify({"message": "Ім'я обов'язкове"}), 400
    
    if "age" not in data or data["age"] <= 0:
        return jsonify({"message": "Вік має бути більше 0"}), 400

    if not data.get("city"):
        return jsonify({"message": "Місто обов'язкове"}), 400
    #---------------

    #додавання користувача
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO users (name, age, city)
        VALUES (?, ?, ?)
        """, (data['name'], data['age'], data['city']))
    
    new_id = cursor.lastrowid
    data['id'] = new_id

    conn.commit()

    conn.close()

    return jsonify({
        "message": "Користувача додано",
        "user": data
    })

@app.route("/users/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    data = request.json

    #перевірка полів
    if not data.get("name"):
        return jsonify({"message": "Ім'я обов'язкове"}), 400
    
    if "age" not in data or data["age"] <= 0:
        return jsonify({"message": "Вік має бути більше 0"}), 400

    if not data.get("city"):
        return jsonify({"message": "Місто обов'язкове"}), 400
    #---------------

    #оновлення даних
    conn = sqlite3.connect("users.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))

    user = cursor.fetchone()

    if user is not None:
        cursor.execute(
            "UPDATE users SET name = ?, age = ?, city = ? WHERE id = ?",
            (data['name'], data['age'], data['city'], user_id)
        )

        conn.commit()

        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))

        user = cursor.fetchone()

        conn.close()

        return jsonify({
            "message": "Дані оновлено",
            "user": dict(user)
        })
    else:
        conn.close()
        return jsonify({
            "message": "Користувача не знайдено"
        }), 404

@app.route("/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    conn = sqlite3.connect("users.db")

    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))

    user = cursor.fetchone()

    if user is not None:
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))

        conn.commit()

        conn.close()

        return jsonify({
            "message": "Користувача видалено",
            "user": dict(user)
        })
    else:
        conn.close()
        return jsonify({
            "message": "Користувача не знайдено"
        }), 404
    

app.run(debug=True)