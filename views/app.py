from flask import Flask, render_template
import os

app = Flask(__name__)

# Get API URLs from environment variables, fallback to localhost for host testing
API_LOGIN = os.environ.get("API_BASE_LOGIN", "http://localhost:5000/api/login")
API_STUDENT = os.environ.get("API_BASE_STUDENT", "http://localhost:5000/api/student")
API_TEACHER = os.environ.get("API_BASE_TEACHER", "http://localhost:5000/api/teacher")
API_ADMIN = os.environ.get("API_BASE_ADMIN", "http://localhost:5000/api/admin")

@app.route("/")
def index():
    return render_template(
        "index.html",
    )

@app.route("/admin")
def admin():
    return render_template(
        "admin.html"
    )

@app.route("/teacher")
def teacher():
    return render_template(
        "teacher.html",
    )

@app.route("/student")
def student():
    return render_template(
        "student.html",
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5006, debug=True)
