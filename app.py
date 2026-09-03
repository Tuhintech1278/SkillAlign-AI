from flask import Flask, render_template, jsonify, request
import pandas as pd
import sqlite3
from analyzer import analyze_skills, get_skill_gaps

app = Flask(__name__)

DATABASE = "skillalign.db"


# ---------------- DATABASE ----------------

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database():

    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            company TEXT,
            location TEXT,
            skills TEXT,
            salary REAL
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_name TEXT,
            qualification TEXT,
            skills TEXT,
            demand_score REAL
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS employers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employer_name TEXT,
            skill TEXT,
            rating INTEGER,
            feedback TEXT
        )
    """)

    conn.commit()

    # Add demo jobs if database is empty
    count = conn.execute(
        "SELECT COUNT(*) FROM jobs"
    ).fetchone()[0]

    if count == 0:

        jobs = [
            (
                "Python Developer",
                "Tech Solutions",
                "Mumbai",
                "Python, SQL, Flask, Machine Learning",
                600000
            ),
            (
                "Data Analyst",
                "DataCorp",
                "Pune",
                "Python, SQL, Power BI, Excel",
                500000
            ),
            (
                "AI Engineer",
                "AI Labs",
                "Nagpur",
                "Python, Machine Learning, Deep Learning, TensorFlow",
                800000
            ),
            (
                "Web Developer",
                "Digital India",
                "Nashik",
                "HTML, CSS, JavaScript, React",
                450000
            ),
            (
                "Cloud Engineer",
                "CloudTech",
                "Mumbai",
                "AWS, Docker, Linux, Python",
                700000
            )
        ]

        conn.executemany("""
            INSERT INTO jobs
            (title, company, location, skills, salary)
            VALUES (?, ?, ?, ?, ?)
        """, jobs)

    # Demo courses

    course_count = conn.execute(
        "SELECT COUNT(*) FROM courses"
    ).fetchone()[0]

    if course_count == 0:

        courses = [
            (
                "Advanced Python Programming",
                "Diploma",
                "Python, Flask, SQL",
                90
            ),
            (
                "Data Analytics",
                "Certificate",
                "Python, SQL, Power BI, Excel",
                85
            ),
            (
                "Artificial Intelligence",
                "Diploma",
                "Python, Machine Learning, Deep Learning",
                95
            ),
            (
                "Web Development",
                "Certificate",
                "HTML, CSS, JavaScript, React",
                80
            ),
            (
                "Cloud Computing",
                "Diploma",
                "AWS, Docker, Linux",
                88
            )
        ]

        conn.executemany("""
            INSERT INTO courses
            (course_name, qualification, skills, demand_score)
            VALUES (?, ?, ?, ?)
        """, courses)

    conn.commit()
    conn.close()


# ---------------- DASHBOARD ----------------

@app.route("/")
def index():

    conn = get_db()

    total_jobs = conn.execute(
        "SELECT COUNT(*) FROM jobs"
    ).fetchone()[0]

    total_courses = conn.execute(
        "SELECT COUNT(*) FROM courses"
    ).fetchone()[0]

    locations = conn.execute(
        "SELECT DISTINCT location FROM jobs"
    ).fetchall()

    conn.close()

    return render_template(
        "index.html",
        total_jobs=total_jobs,
        total_courses=total_courses,
        locations=locations
    )


# ---------------- JOBS ----------------

@app.route("/jobs")
def jobs():

    conn = get_db()

    jobs = conn.execute(
        "SELECT * FROM jobs"
    ).fetchall()

    conn.close()

    return render_template(
        "jobs.html",
        jobs=jobs
    )


# ---------------- SKILL ANALYSIS ----------------

@app.route("/skills")
def skills():

    conn = get_db()

    jobs = conn.execute(
        "SELECT skills FROM jobs"
    ).fetchall()

    conn.close()

    skill_data = analyze_skills(jobs)

    return render_template(
        "skills.html",
        skills=skill_data
    )


# ---------------- COURSES ----------------

@app.route("/courses")
def courses():

    conn = get_db()

    courses = conn.execute(
        "SELECT * FROM courses ORDER BY demand_score DESC"
    ).fetchall()

    conn.close()

    return render_template(
        "courses.html",
        courses=courses
    )


# ---------------- SKILL GAP ----------------

@app.route("/skill-gap")
def skill_gap():

    conn = get_db()

    jobs = conn.execute(
        "SELECT skills FROM jobs"
    ).fetchall()

    courses = conn.execute(
        "SELECT * FROM courses"
    ).fetchall()

    conn.close()

    gaps = get_skill_gaps(jobs, courses)

    return jsonify(gaps)


# ---------------- RECOMMENDATIONS ----------------

@app.route("/recommendations")
def recommendations():

    conn = get_db()

    jobs = conn.execute(
        "SELECT skills FROM jobs"
    ).fetchall()

    courses = conn.execute(
        "SELECT * FROM courses"
    ).fetchall()

    conn.close()

    gaps = get_skill_gaps(jobs, courses)

    recommendations = []

    for course in courses:

        course_skills = set(
            x.strip().lower()
            for x in course["skills"].split(",")
        )

        matching_skills = [
            skill for skill in gaps
            if skill["skill"].lower() in course_skills
        ]

        if matching_skills:

            recommendations.append({
                "course": course["course_name"],
                "qualification": course["qualification"],
                "score": course["demand_score"],
                "skills": course["skills"]
            })

    return render_template(
        "recommendations.html",
        recommendations=recommendations
    )


# ---------------- DISTRICT PLAN ----------------

@app.route("/district-plan")
def district_plan():

    conn = get_db()

    data = conn.execute("""
        SELECT location, COUNT(*) as job_count
        FROM jobs
        GROUP BY location
        ORDER BY job_count DESC
    """).fetchall()

    conn.close()

    plans = []

    for row in data:

        plans.append({
            "district": row["location"],
            "job_demand": row["job_count"],
            "recommended_training":
                "Python & Data Analytics"
        })

    return render_template(
        "district.html",
        plans=plans
    )


# ---------------- EMPLOYER VALIDATION ----------------

@app.route("/employer-feedback", methods=["POST"])
def employer_feedback():

    data = request.json

    conn = get_db()

    conn.execute("""
        INSERT INTO employers
        (employer_name, skill, rating, feedback)
        VALUES (?, ?, ?, ?)
    """, (
        data["employer"],
        data["skill"],
        data["rating"],
        data["feedback"]
    ))

    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "message": "Employer feedback successfully recorded."
    })


# ---------------- API ----------------

@app.route("/api/jobs")
def api_jobs():

    conn = get_db()

    jobs = conn.execute(
        "SELECT * FROM jobs"
    ).fetchall()

    conn.close()

    return jsonify([
        dict(job)
        for job in jobs
    ])


@app.route("/api/skills")
def api_skills():

    conn = get_db()

    jobs = conn.execute(
        "SELECT skills FROM jobs"
    ).fetchall()

    conn.close()

    return jsonify(
        analyze_skills(jobs)
    )


if __name__ == "__main__":

    initialize_database()

    app.run(
        debug=True,
        host="0.0.0.0",
        port=5000
    )