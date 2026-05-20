from flask import Blueprint, jsonify, request
from database import get_db_connection

tasks_bp = Blueprint("tasks", __name__)

@tasks_bp.route("/tasks", methods=["GET"])
def get_tasks():
    completed = request.args.get("completed")
    search = request.args.get("search")
    sort = request.args.get("sort")
    limit = request.args.get("limit")
    offset = request.args.get("offset")

    allowed_sorts = {
        "id": "id ASC",
        "id_desc": "id DESC",
        "title": "title ASC",
        "title_desc": "title DESC"
    }

    query = "SELECT * FROM tasks"
    conditions = []
    params = []

    conn = get_db_connection()
    cursor = conn.cursor()

    if completed is not None:
        conditions.append("completed = ?")
        params.append(int(completed))
    
    if search is not None:
        conditions.append("title LIKE ?")
        params.append(f"%{search}%")

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    if sort in allowed_sorts:
        query += " ORDER BY " + allowed_sorts[sort]

    if limit is not None:
        query += " LIMIT ? "
        params.append(int(limit))

        if offset is not None:
            query += " OFFSET ? "
            params.append(int(offset))

    cursor.execute(query, params)
    tasks = cursor.fetchall()

    conn.close()

    result = [dict(task) for task in tasks]

    return jsonify(result)

@tasks_bp.route("/tasks", methods=["POST"])
def add_task():
    data = request.json

    if not data.get("title"):
        return jsonify({"message": "Поле title обов'язкове"}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO tasks (title)
        VALUES (?)
        """, (data['title'],))

    new_id = cursor.lastrowid
    data['id'] = new_id
    data["completed"] = 0

    conn.commit()
    
    conn.close()

    return jsonify({
        "message": "Задачу додано",
        "task": data
    })

@tasks_bp.route("/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM tasks WHERE id = ?", (int(task_id),))
    task = cursor.fetchone()

    conn.close()

    if task is not None:
        return jsonify(dict(task))
    else:
        return jsonify({
            "message": "Задачу не знайдено"   
        }), 404

@tasks_bp.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    data = request.json

    #перевірка полів
    if not data.get("title"):
        return jsonify({"message": "Поле title обов'язкове"}), 400
    if data.get("completed") not in [0, 1]:
        return jsonify({"message": "Поле completed має бути 0 або 1"}), 400
    #------------------

    conn = get_db_connection()
    cursor = conn.cursor()

    #перевірка чи існує задача
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    task = cursor.fetchone()

    if task is None:
        conn.close()
        return jsonify({"message": "Задачу не знайдено"}), 404
    #-------------------

    #оновлення задачі
    cursor.execute("UPDATE tasks SET title = ?, completed = ? WHERE id = ?", (data['title'], int(data['completed']), task_id))

    conn.commit()

    conn.close()
    #-----------------

    updated_task = {
        "id": task_id,
        "title": data["title"],
        "completed": data["completed"]
    }

    return jsonify(updated_task)

@tasks_bp.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    #перевірка чи існує задача
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    task = cursor.fetchone()

    if task is None:
        conn.close()
        return jsonify({"message": "Задачу не знайдено"}), 404
    #-------------------

    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))

    conn.commit()

    conn.close()

    return jsonify({
        "message": "Задачу видалено",
        "task": dict(task)
    })