import psycopg2
from flask import Flask, request, jsonify

app = Flask(__name__)

# Make sure you created this database first:
# CREATE DATABASE enrollment_db;
DB_CONFIG = {
    "host": "localhost",
    "database": "enrollment_db",
    "user": "postgres",
    "password": "1234"
}

def init_db():
    """Create users, subjects, and student_records tables if they don't exist."""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    # ---------------- USERS TABLE ----------------
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        type TEXT CHECK(type IN ('STUDENT','TEACHER','ADMIN')) NOT NULL
    );
    """)

    # ---------------- SUBJECTS TABLE ----------------
    cur.execute("""
    CREATE TABLE IF NOT EXISTS subjects (
        id SERIAL PRIMARY KEY,
        course_code TEXT UNIQUE NOT NULL,
        units INT NOT NULL CHECK (units > 0),
        added_by TEXT NOT NULL REFERENCES users(username) ON DELETE SET NULL,
        current_enrollees INT DEFAULT 0 CHECK (current_enrollees >= 0),
        max_enrollees INT NOT NULL CHECK (max_enrollees > 0)
    );
    """)

    # ---------------- STUDENT RECORDS TABLE ----------------
    cur.execute("""
    CREATE TABLE IF NOT EXISTS student_records (
        id SERIAL PRIMARY KEY,
        student_username TEXT NOT NULL REFERENCES users(username) ON DELETE CASCADE,
        course TEXT NOT NULL,
        grade INT DEFAULT -1
    );
    """)

    conn.commit()
    cur.close()
    conn.close()
    print("Database initialized (users, subjects, student_records tables ensured).")



def get_user_by_username(username):
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("SELECT id, username, password, type FROM users WHERE username=%s", (username,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if row:
        return {"id": row[0], "username": row[1], "password": row[2], "type": row[3]}
    return None

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    user = get_user_by_username(data["username"])
    if user and user["password"] == data["password"]:
        return jsonify({"message": "Login OK", "user": user})
    return jsonify({"message": "Invalid credentials"}), 401

if __name__ == "__main__":
    init_db()  # just ensure table exists
    app.run(port=5001, debug=True)
