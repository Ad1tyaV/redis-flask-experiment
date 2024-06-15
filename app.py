from flask import Flask, request, jsonify
import sqlite3
import redis

app = Flask(__name__)

# Configure Redis connection
r = redis.StrictRedis(host='redis', port=6379, db=0)

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''
              CREATE TABLE IF NOT EXISTS users
              (id INTEGER PRIMARY KEY, name TEXT, age INTEGER)
              ''')
    conn.commit()
    conn.close()

@app.route('/')
def home():
    return "Welcome to the Flask-Redis-SQLite App!"

@app.route('/add_user', methods=['POST'])
def add_user():
    data = request.get_json()
    name = data['name']
    age = data['age']
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('INSERT INTO users (name, age) VALUES (?, ?)', (name, age))
    user_id = c.lastrowid
    conn.commit()
    conn.close()
    return jsonify({"status": "User added successfully!", "user_id": user_id})

@app.route('/get_user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = r.get(user_id)
    if user:
        return jsonify({"user": user.decode('utf-8')})
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = c.fetchone()
    conn.close()
    if user:
        user_data = {"id": user[0], "name": user[1], "age": user[2]}
        r.set(user_id, str(user_data))
        return jsonify({"user": user_data})
    return jsonify({"error": "User not found"}), 404

@app.route('/list_users', methods=['GET'])
def list_users():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users')
    users = c.fetchall()
    conn.close()
    user_list = [{"id": user[0], "name": user[1], "age": user[2]} for user in users]
    return jsonify({"users": user_list})

@app.route('/update_user/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.get_json()
    name = data.get('name')
    age = data.get('age')
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('UPDATE users SET name = ?, age = ? WHERE id = ?', (name, age, user_id))
    conn.commit()
    conn.close()
    r.delete(user_id)  # Remove old cached data
    return jsonify({"status": "User updated successfully!"})

@app.route('/delete_user/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('DELETE FROM users WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()
    r.delete(user_id)  # Remove user from Redis cache
    return jsonify({"status": "User deleted successfully!"})

@app.route('/redis_entries', methods=['GET'])
def redis_entries():
    num_entries = r.dbsize()
    return jsonify({"num_entries": num_entries})

@app.route('/redis_dump', methods=['GET'])
def redis_dump():
    keys = r.keys()
    result = []
    for key in keys:
        value = r.get(key)
        result.append({"key": key.decode('utf-8'), "value": value.decode('utf-8')})
    return jsonify(result)


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
