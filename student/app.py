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


# -------------------- Helper --------------------
def db_exec(query, params=None, fetch=False):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(query, params)

    result = None
    if fetch:
        result = cur.fetchall()

    conn.commit()
    cur.close()
    conn.close()
    return result


# -------------------- 1. VIEW SUBJECTS --------------------
@app.route("/student/subjects", methods=["GET"])
def student_subjects():
    rows = db_exec("""
        SELECT id, course_code, units, current_enrollees, max_enrollees
        FROM subjects ORDER BY id
    """, fetch=True)

    subjects = [
        {
            "id": r[0],
            "course": r[1],
            "units": r[2],
            "current_enrollees": r[3],
            "max_enrollees": r[4],
        }
        for r in rows
    ]
    return jsonify({"subjects": subjects}), 200


# -------------------- 2. ENLIST IN CLASS --------------------
@app.route("/student/enlist", methods=["POST"])
def student_enlist():
    data = request.get_json()
    username = data.get("username")
    course = data.get("course")

    if not username or not course:
        return jsonify({"error": "Missing username or course"}), 400

    # Check if already enrolled
    exists = db_exec(
        "SELECT id FROM student_records WHERE student_username=%s AND course=%s",
        (username, course),
        fetch=True
    )
    if exists:
        return jsonify({"error": "You are already enlisted in this course"}), 400

    # Check if subject is full
    sub = db_exec(
        "SELECT current_enrollees, max_enrollees FROM subjects WHERE course_code=%s",
        (course,),
        fetch=True
    )
    if not sub:
        return jsonify({"error": "Course does not exist"}), 404

    current, maximum = sub[0]
    if current >= maximum:
        return jsonify({"error": "Class is full"}), 400

    # Insert record
    db_exec(
        "INSERT INTO student_records (student_username, course, grade) VALUES (%s, %s, %s)",
        (username, course, -1)
    )

    # Update subject enrollment
    db_exec(
        "UPDATE subjects SET current_enrollees = current_enrollees + 1 WHERE course_code=%s",
        (course,)
    )

    return jsonify({"message": "Successfully enlisted"}), 201


# -------------------- 3. VIEW MY RECORDS --------------------
@app.route("/student/records", methods=["GET"])
def student_records():
    username = request.args.get("username")

    rows = db_exec("""
        SELECT course, grade FROM student_records
        WHERE student_username=%s
        ORDER BY course
    """, (username,), fetch=True)

    records = [{"course": r[0], "grade": r[1]} for r in rows]

    return jsonify({"records": records}), 200


# -------------------- MAIN --------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0",port=5005, debug=True)
