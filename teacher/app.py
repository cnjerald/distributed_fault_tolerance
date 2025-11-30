import psycopg2
from flask import Flask, request, jsonify

app = Flask(__name__)

DB_CONFIG = {
    "host": "localhost",
    "database": "enrollment_db",
    "user": "postgres",
    "password": "1234"
}

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

# ----------------- TEACHER LOGIN -----------------

@app.route("/teacher/login", methods=["POST"])
def teacher_login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT username, password, type FROM users WHERE username=%s", (username,))
    row = cur.fetchone()
    cur.close()
    conn.close()

    if row and row[1] == password and row[2] == "TEACHER":
        return jsonify({"message": "Login OK", "username": username})
    return jsonify({"error": "Invalid credentials"}), 401



# -------------------- Helper for DB --------------------

def db_exec(query, params=None, fetch=False):
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


# -------------------- SUBJECTS CRUD (Teacher Can Manage) --------------------

@app.route("/teacher/subjects", methods=["GET"])
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



@app.route("/teacher/subjects", methods=["POST"])
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



@app.route("/teacher/subjects/<int:subj_id>", methods=["PUT"])
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



@app.route("/teacher/subjects/<int:subj_id>", methods=["DELETE"])
def delete_subject(subj_id):

    try:
        db_exec("DELETE FROM subjects WHERE id=%s", (subj_id,))
        return jsonify({"message": "Subject deleted"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400



# -------------------- STUDENT RECORD CRUD --------------------

@app.route("/teacher/student_records", methods=["GET"])
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



@app.route("/teacher/student_records", methods=["POST"])
def create_student_record():
    data = request.get_json()
    student_username = data.get("student_username")
    course = data.get("course")

    if not student_username or not course:
        return jsonify({"error": "Missing student or course"}), 400

    # Prevent duplicate enrollment
    existing = db_exec(
        "SELECT id FROM student_records WHERE student_username=%s AND course=%s",
        (student_username, course),
        fetch=True
    )
    if existing:
        return jsonify({"error": "This student already has a record for this course"}), 400

    grade = data.get("grade", -1)
    try:
        db_exec(
            "INSERT INTO student_records (student_username, course, grade) VALUES (%s, %s, %s)",
            (student_username, course, grade)
        )
        db_exec(
            "UPDATE subjects SET current_enrollees = current_enrollees + 1 WHERE course_code=%s",
            (course,)
        )
        return jsonify({"message": "Student record created"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400



@app.route("/teacher/student_records/<int:record_id>", methods=["PUT"])
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



@app.route("/teacher/student_records/<int:record_id>", methods=["DELETE"])
def delete_student_record(record_id):
    db_exec("DELETE FROM student_records WHERE id=%s", (record_id,))
    return jsonify({"message": "Student record deleted"}), 200


@app.route("/teacher/users", methods=["GET"])
def get_students():
    rows = db_exec("SELECT username, type FROM users WHERE type='STUDENT'", fetch=True)

    students = [{"username": r[0], "type": r[1]} for r in rows]

    return jsonify({"students": students}), 200



# ----------------- Main -----------------

if __name__ == "__main__":
    app.run(port=5004, debug=True)
