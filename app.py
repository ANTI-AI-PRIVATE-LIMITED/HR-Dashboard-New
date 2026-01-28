from flask import Flask, render_template, request, redirect, session, send_file
from werkzeug.security import check_password_hash
from supabase import create_client
import os
import pandas as pd
from datetime import datetime

# =========================
# APP CONFIG
# =========================
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "fallback-secret")

# =========================
# SUPABASE CONFIG
# =========================
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise Exception("Supabase credentials not set")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# =========================
# AUTH
# =========================
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        res = supabase.table("admins").select("*").eq("email", email).execute()

        if not res.data:
            return "Invalid login", 401

        admin = res.data[0]

        if check_password_hash(admin["password"], password):
            session.clear()
            session["hr_logged_in"] = True
            session["admin_email"] = email
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

    jobs = supabase.table("jobs").select("id").execute().data
    applications = supabase.table("applications").select("id").execute().data

    return render_template(
        "dashboard.html",
        total_jobs=len(jobs),
        total_applications=len(applications)
    )

# =========================
# JOBS
# =========================
@app.route("/jobs", methods=["GET", "POST"])
def jobs():
    if not session.get("hr_logged_in"):
        return redirect("/")

    if request.method == "POST":
        supabase.table("jobs").insert({
            "title": request.form.get("title"),
            "description": request.form.get("description"),
            "location": request.form.get("location"),
            "job_type": request.form.get("job_type"),
            "posted_at": datetime.utcnow().date().isoformat()
        }).execute()

    jobs = supabase.table("jobs").select("*").order("id", desc=True).execute().data
    return render_template("jobs.html", jobs=jobs)

@app.route("/delete-job/<int:id>")
def delete_job(id):
    if not session.get("hr_logged_in"):
        return redirect("/")

    supabase.table("jobs").delete().eq("id", id).execute()
    return redirect("/jobs")

# =========================
# APPLY JOB
# =========================
@app.route("/apply/<int:job_id>", methods=["GET", "POST"])
def apply(job_id):
    job = supabase.table("jobs").select("*").eq("id", job_id).execute().data
    if not job:
        return "Job not found", 404

    if request.method == "POST":
        resume = request.files.get("resume")
        filename = f"{job_id}_{int(datetime.utcnow().timestamp())}_{resume.filename}"

        supabase.storage.from_("resumes").upload(
            filename,
            resume.read(),
            {"content-type": resume.content_type}
        )

        resume_url = f"{SUPABASE_URL}/storage/v1/object/public/resumes/{filename}"

        supabase.table("applications").insert({
            "job_id": job_id,
            "applicant_name": request.form.get("name"),
            "email": request.form.get("email"),
            "phone": request.form.get("phone"),
            "resume_url": resume_url
        }).execute()

        return "Application submitted successfully!"

    return render_template("apply.html", job=job[0])

# =========================
# APPLICATIONS
# =========================
@app.route("/applications")
def applications():
    if not session.get("hr_logged_in"):
        return redirect("/")

    jobs = supabase.table("jobs").select("id,title").execute().data
    applications = supabase.table("applications").select("*").execute().data

    return render_template(
        "applications.html",
        applications=applications,
        jobs=jobs,
        selected_job=None
    )
