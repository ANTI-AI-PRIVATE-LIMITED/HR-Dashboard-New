from flask import Flask, render_template, request, redirect, session, send_from_directory, send_file
import sqlite3
import os
import pandas as pd

# =========================
# BASIC APP CONFIG
# =========================
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "fallback-secret-key")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "hr_management.db")

UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads", "resumes")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# =========================
# DATABASE CONNECTION
# =========================
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# =========================
# AUTH / LOGIN
# =========================
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        # TEMP ADMIN (DEPLOY SAFE)
        if email == "admin@hr.com" and password == "admin123":
            session["user"] = email
            session["hr_logged_in"] = True
            return redirect("/dashboard")

        return "Invalid login", 401

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# =========================
# DASHBOARD
# =========================
@app.route("/dashboard")
def dashboard():
    if not session.get("hr_logged_in"):
        return redirect("/")

    db = get_db()
    cur = db.cursor()

    total_jobs = cur.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]
    total_applications = cur.execute("SELECT COUNT(*) FROM applications").fetchone()[0]

    return render_template(
        "dashboard.html",
        total_jobs=total_jobs,
        total_applications=total_applications
    )


# =========================
# SETTINGS
# =========================
@app.route("/settings")
def settings():
    if not session.get("hr_logged_in"):
        return redirect("/")
    return render_template("settings.html")


# =========================
# JOB MANAGEMENT
# =========================
@app.route("/jobs", methods=["GET", "POST"])
def jobs():
    if not session.get("hr_logged_in"):
        return redirect("/")

    db = get_db()
    cur = db.cursor()

    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description")
        location = request.form.get("location")
        job_type = request.form.get("job_type")

        cur.execute(
            "INSERT INTO jobs (title, description, location, job_type) VALUES (?, ?, ?, ?)",
            (title, description, location, job_type)
        )
        db.commit()

    jobs = cur.execute("SELECT * FROM jobs").fetchall()
    return render_template("jobs.html", jobs=jobs)


@app.route("/delete-job/<int:id>")
def delete_job(id):
    if not session.get("hr_logged_in"):
        return redirect("/")

    db = get_db()
    db.execute("DELETE FROM jobs WHERE id=?", (id,))
    db.commit()
    return redirect("/jobs")


@app.route("/edit-job/<int:id>", methods=["GET", "POST"])
def edit_job(id):
    if not session.get("hr_logged_in"):
        return redirect("/")

    db = get_db()
    cur = db.cursor()

    if request.method == "POST":
        cur.execute("""
            UPDATE jobs
            SET title=?, description=?, location=?, job_type=?
            WHERE id=?
        """, (
            request.form.get("title"),
            request.form.get("description"),
            request.form.get("location"),
            request.form.get("job_type"),
            id
        ))
        db.commit()
        return redirect("/jobs")

    job = cur.execute("SELECT * FROM jobs WHERE id=?", (id,)).fetchone()
    return render_template("edit_job.html", job=job)


# =========================
# APPLY JOB
# =========================
@app.route("/apply/<int:job_id>", methods=["GET", "POST"])
def apply(job_id):
    db = get_db()
    cur = db.cursor()

    job = cur.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()

    if not job:
        return "Job not found", 404

    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        resume = request.files.get("resume")

        if not all([name, email, phone, resume]):
            return "Invalid data", 400

        filename = resume.filename
        resume.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

        cur.execute("""
            INSERT INTO applications
            (job_id, applicant_name, email, phone, resume_path)
            VALUES (?, ?, ?, ?, ?)
        """, (job_id, name, email, phone, filename))

        db.commit()
        return "Application submitted successfully!"

    return render_template("apply.html", job=job)


# =========================
# VIEW / DOWNLOAD RESUME
# =========================
@app.route("/resume/<path:filename>")
def view_resume(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


@app.route("/download/<path:filename>")
def download_resume(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename, as_attachment=True)


# =========================
# APPLICATIONS + EXPORT
# =========================
@app.route("/applications")
def applications():
    if not session.get("hr_logged_in"):
        return redirect("/")

    db = get_db()
    cur = db.cursor()

    jobs = cur.execute("SELECT id, title FROM jobs").fetchall()
    applications = cur.execute("""
        SELECT applications.*, jobs.title AS job_title
        FROM applications
        JOIN jobs ON applications.job_id = jobs.id
        ORDER BY applications.id DESC
    """).fetchall()

    return render_template("applications.html", applications=applications, jobs=jobs)


@app.route("/export-applications")
def export_applications():
    if not session.get("hr_logged_in"):
        return redirect("/")

    db = get_db()
    df = pd.read_sql_query("""
        SELECT jobs.title AS Job,
               applications.applicant_name AS Name,
               applications.email AS Email,
               applications.phone AS Phone
        FROM applications
        JOIN jobs ON applications.job_id = jobs.id
    """, db)

    file_path = os.path.join(BASE_DIR, "applications.xlsx")
    df.to_excel(file_path, index=False)

    return send_file(file_path, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)