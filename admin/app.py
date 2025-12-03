import psycopg2
from flask import Flask, request, jsonify

app = Flask(__name__)

DB_CONFIG = {
    "host": "host.docker.internal",  # points to your host machine
    "database": "enrollment_db",
    "user": "postgres",
    "password": "1234",
    "port": 5432                      # optional, default is 5432
}


def get_connection():
    return psycopg2.connect(**DB_CONFIG)

# ----------------- Routes -----------------

# Admin login - casual
@app.route("/admin/login", methods=["POST"])
def admin_login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT username, password, type FROM users WHERE username=%s", (username,))
    row = cur.fetchone()
    cur.close()
    conn.close()

    if row and row[1] == password and row[2] == "ADMIN":
        # Just return a success flag; no JWT
        return jsonify({"message": "Login OK", "username": username})
    return jsonify({"error": "Invalid credentials"}), 401

# Create user
@app.route("/admin/users", methods=["POST"])
def create_user():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password", "123")
    type_ = data.get("type")

    if type_ not in ("STUDENT", "TEACHER"):
        return jsonify({"error": "Invalid user type"}), 400

    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO users (username, password, type) VALUES (%s, %s, %s)",
            (username, password, type_)
        )
        conn.commit()
        return jsonify({"message": "User created successfully"}), 201
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        return jsonify({"error": "Username already exists"}), 409
    finally:
        cur.close()
        conn.close()

# Delete user
@app.route("/admin/users/<username>", methods=["DELETE"])
def delete_user(username):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE username=%s RETURNING username", (username,))
    deleted = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    if deleted:
        return jsonify({"message": f"User {deleted[0]} deleted"}), 200
    return jsonify({"error": "User not found"}), 404

# Get all users
@app.route("/admin/users", methods=["GET"])
def get_all_users():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, username, type FROM users ORDER BY id")
    users = [{"id": row[0], "username": row[1], "type": row[2]} for row in cur.fetchall()]
    cur.close()
    conn.close()
    return jsonify({"users": users})

# Update user role
@app.route("/admin/users/<username>", methods=["PUT"])
def update_user_role(username):
    data = request.get_json()
    new_type = data.get("type")
    if new_type not in ("STUDENT", "TEACHER"):
        return jsonify({"error": "Invalid user type"}), 400

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE users SET type=%s WHERE username=%s RETURNING username, type",
        (new_type, username)
    )
    updated = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    if updated:
        return jsonify({"message": f"User {updated[0]} updated to {updated[1]}"}), 200
    return jsonify({"error": "User not found"}), 404

# -------------------- Helper for SUBJECTS --------------------

def db_exec(query, params=None, fetch=False):
    """Simple helper used only by subjects CRUD."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(query, params)

    results = None
    if fetch:
        results = cur.fetchall()

    conn.commit()
    cur.close()
    conn.close()
    return results


# -------------------- SUBJECTS CRUD --------------------


@app.route("/admin/subjects", methods=["GET"])
def get_subjects():
    rows = db_exec("""
        SELECT id, course_code, units, added_by, current_enrollees, max_enrollees
        FROM subjects ORDER BY id
    """, fetch=True)

    subjects = [
        {
            "id": r[0],
            "course_code": r[1],
            "units": r[2],
            "added_by": r[3],
            "current_enrollees": r[4],
            "max_enrollees": r[5],
        }
        for r in rows
    ]

    return jsonify({"subjects": subjects}), 200



@app.route("/admin/subjects", methods=["POST"])
def create_subject():
    data = request.get_json()

    required = ["course_code", "units", "added_by", "max_enrollees"]
    for field in required:
        if field not in data:
            return jsonify({"error": f"Missing field: {field}"}), 400

    try:
        db_exec("""
            INSERT INTO subjects (course_code, units, added_by, max_enrollees, current_enrollees)
            VALUES (%s, %s, %s, %s, 0)
        """, (
            data["course_code"],
            data["units"],
            data["added_by"],
            data["max_enrollees"]
        ))

        return jsonify({"message": "Subject created"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 400



@app.route("/admin/subjects/<int:subj_id>", methods=["PUT"])
def update_subject(subj_id):
    data = request.get_json()

    try:
        db_exec("""
            UPDATE subjects
            SET course_code=%s, units=%s, max_enrollees=%s
            WHERE id=%s
        """, (
            data["course_code"],
            data["units"],
            data["max_enrollees"],
            subj_id
        ))

        return jsonify({"message": "Subject updated"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400



@app.route("/admin/subjects/<int:subj_id>", methods=["DELETE"])
def delete_subject(subj_id):

    try:
        db_exec("DELETE FROM subjects WHERE id=%s", (subj_id,))
        return jsonify({"message": "Subject deleted"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400
    


# STUDENT CRUD
# Get all student records
@app.route("/admin/student_records", methods=["GET"])
def get_student_records():
    rows = db_exec("""
        SELECT id, student_username, course, grade FROM student_records ORDER BY id
    """, fetch=True)

    records = [
        {
            "id": r[0],
            "student_username": r[1],
            "course": r[2],
            "grade": r[3]
        } for r in rows
    ]
    return jsonify({"records": records}), 200


# Add a student record
@app.route("/admin/student_records", methods=["POST"])
def create_student_record():
    data = request.get_json()
    student_username = data.get("student_username")
    course = data.get("course")

    if not student_username or not course:
        return jsonify({"error": "Missing student or course"}), 400

    # Check if record exists
    existing = db_exec(
        "SELECT id FROM student_records WHERE student_username=%s AND course=%s",
        (student_username, course),
        fetch=True
    )
    if existing:
        return jsonify({"error": "This student already has a record for this course"}), 400

    grade = data.get("grade", -1)
    try:
        # Insert record
        db_exec(
            "INSERT INTO student_records (student_username, course, grade) VALUES (%s, %s, %s)",
            (student_username, course, grade)
        )
        # Increment current_enrollees
        db_exec(
            "UPDATE subjects SET current_enrollees = current_enrollees + 1 WHERE course_code=%s",
            (course,)
        )
        return jsonify({"message": "Student record created"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400




# Update grade
@app.route("/admin/student_records/<int:record_id>", methods=["PUT"])
def update_student_record(record_id):
    data = request.get_json()
    if "grade" not in data:
        return jsonify({"error": "Missing grade"}), 400

    db_exec("""
        UPDATE student_records
        SET grade=%s
        WHERE id=%s
    """, (data["grade"], record_id))

    return jsonify({"message": "Grade updated"}), 200




# Delete a student record
@app.route("/admin/student_records/<int:record_id>", methods=["DELETE"])
def delete_student_record(record_id):
    db_exec("DELETE FROM student_records WHERE id=%s", (record_id,))
    return jsonify({"message": "Student record deleted"}), 200





# ----------------- Main -----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0",port=5003, debug=True)
