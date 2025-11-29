from flask import Flask, request, jsonify, send_from_directory
import requests
from flask_cors import CORS
import os

app = Flask(
    __name__,
    static_folder="static",       # folder for JS/CSS
    template_folder="templates"   # folder for HTML
)
CORS(app)



# ---------------- Backend Nodes ----------------
LOGIN_URL = "http://localhost:5001/login"
ADMIN_URL = "http://localhost:5003"  # still used for admin CRUD

# ---------------- Routes ----------------

# Root - simple message
@app.route("/", methods=["GET"])
def root():
    return jsonify({"message": "Main server running"})

# Serve HTML pages
@app.route("/page/<page_name>")
def serve_page(page_name):
    """Serve HTML pages from templates folder"""
    return send_from_directory(app.template_folder, f"{page_name}.html")

# ---------------- Login API ----------------
@app.route("/api/login", methods=["POST"])
def login_api():
    try:
        payload = request.get_json()
        res = requests.post(LOGIN_URL, json=payload, timeout=2)
        return jsonify(res.json()), res.status_code
    except Exception as e:
        print("ERROR:", e)
        return jsonify({"error": "Login service unavailable"}), 503

# ---------------- Admin CRUD APIs ----------------
# Only admin users can access these (frontend will enforce)
@app.route("/api/admin/users", methods=["GET", "POST"])
def admin_users():
    try:
        payload = request.get_json() if request.method == "POST" else None
        headers = {"Authorization": request.headers.get("Authorization")}
        if request.method == "GET":
            res = requests.get(f"{ADMIN_URL}/admin/users", headers=headers, timeout=2)
        else:  # POST
            res = requests.post(f"{ADMIN_URL}/admin/users", headers=headers, json=payload, timeout=2)
        return jsonify(res.json()), res.status_code
    except Exception as e:
        print("ERROR:", e)
        return jsonify({"error": "Admin service unavailable"}), 503

@app.route("/api/admin/users/<username>", methods=["DELETE", "PUT"])
def admin_users_detail(username):
    try:
        payload = request.get_json() if request.method == "PUT" else None
        headers = {"Authorization": request.headers.get("Authorization")}
        if request.method == "DELETE":
            res = requests.delete(f"{ADMIN_URL}/admin/users/{username}", headers=headers, timeout=2)
        else:  # PUT
            res = requests.put(f"{ADMIN_URL}/admin/users/{username}", headers=headers, json=payload, timeout=2)
        return jsonify(res.json()), res.status_code
    except Exception as e:
        print("ERROR:", e)
        return jsonify({"error": "Admin service unavailable"}), 503

@app.route("/api/admin/subjects", methods=["GET", "POST"])
def admin_subjects():
    try:
        payload = request.get_json() if request.method == "POST" else None
        headers = {"Authorization": request.headers.get("Authorization")}

        if request.method == "GET":
            res = requests.get(f"{ADMIN_URL}/admin/subjects",
                               headers=headers, timeout=2)
        else:  # POST
            res = requests.post(f"{ADMIN_URL}/admin/subjects",
                                headers=headers, json=payload, timeout=2)

        return jsonify(res.json()), res.status_code

    except Exception as e:
        print("ERROR:", e)
        return jsonify({"error": "Admin service unavailable"}), 503

@app.route("/api/admin/subjects/<int:subj_id>", methods=["PUT", "DELETE"])
def admin_subjects_detail(subj_id):
    try:
        payload = request.get_json() if request.method == "PUT" else None
        headers = {"Authorization": request.headers.get("Authorization")}

        if request.method == "DELETE":
            res = requests.delete(f"{ADMIN_URL}/admin/subjects/{subj_id}",
                                  headers=headers, timeout=2)
        else:  # PUT
            res = requests.put(f"{ADMIN_URL}/admin/subjects/{subj_id}",
                               headers=headers, json=payload, timeout=2)

        return jsonify(res.json()), res.status_code

    except Exception as e:
        print("ERROR:", e)
        return jsonify({"error": "Admin service unavailable"}), 503

@app.route("/api/admin/student_records", methods=["GET", "POST"])
def admin_student_records():
    try:
        payload = request.get_json() if request.method == "POST" else None
        headers = {"Authorization": request.headers.get("Authorization")}
        
        if request.method == "GET":
            res = requests.get(f"{ADMIN_URL}/admin/student_records",
                               headers=headers, timeout=2)
        else:  # POST
            res = requests.post(f"{ADMIN_URL}/admin/student_records",
                                headers=headers, json=payload, timeout=2)
        return jsonify(res.json()), res.status_code
    except Exception as e:
        print("ERROR:", e)
        return jsonify({"error": "Admin service unavailable"}), 503

# ---------------- Student Records CRUD ----------------
@app.route("/api/admin/student_records/<int:record_id>", methods=["PUT", "DELETE"])
def admin_student_records_detail(record_id):
    try:
        payload = request.get_json() if request.method == "PUT" else None
        headers = {"Authorization": request.headers.get("Authorization")}

        if request.method == "DELETE":
            res = requests.delete(f"{ADMIN_URL}/admin/student_records/{record_id}",
                                  headers=headers, timeout=2)
        else:  # PUT
            res = requests.put(f"{ADMIN_URL}/admin/student_records/{record_id}",
                               headers=headers, json=payload, timeout=2)

        return jsonify(res.json()), res.status_code

    except Exception as e:
        print("ERROR:", e)
        return jsonify({"error": "Admin service unavailable"}), 503




# ----------------- Main -----------------
if __name__ == "__main__":
    # Ensure folders exist
    os.makedirs("templates", exist_ok=True)
    os.makedirs("static/js", exist_ok=True)
    app.run(port=5000, debug=True)
