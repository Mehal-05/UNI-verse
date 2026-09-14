from flask import Flask, render_template, request, redirect, session
import mysql.connector

app = Flask(__name__)
app.secret_key = "universe_secret_key"


def get_db_connection():
    return mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="sajuuyire",
        database="universe_db"
    )


@app.route("/")
def home():
    return redirect("/login")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        registration_no = request.form["registration_no"]
        password = request.form["password"]

        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM student WHERE registration_no = %s AND password = %s",
            (registration_no, password)
        )

        student = cursor.fetchone()

        if student:
            session["student_id"] = student["student_id"]
            session["role"] = "student"

            cursor.close()
            db.close()

            return redirect("/student")

        cursor.execute(
            "SELECT * FROM placement_officer WHERE email = %s AND password = %s",
            (registration_no, password)
        )

        officer = cursor.fetchone()

        cursor.close()
        db.close()

        if officer:
            session["officer_id"] = officer["officer_id"]
            session["role"] = "officer"

            return redirect("/officer")

        return "Invalid login details"

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        registration_no = request.form["registration_no"]
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        campus_id = request.form["campus_id"]
        department_id = request.form["department_id"]
        cgpa = request.form["cgpa"]
        backlogs = request.form["backlogs"]
        graduation_year = request.form["graduation_year"]

        db = get_db_connection()
        cursor = db.cursor()

        cursor.execute("""
            INSERT INTO student
            (registration_no, name, email, password, campus_id,
             department_id, cgpa, backlogs, graduation_year)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            registration_no, name, email, password, campus_id,
            department_id, cgpa, backlogs, graduation_year
        ))

        db.commit()

        cursor.close()
        db.close()

        return redirect("/login")

    return render_template("register.html")


@app.route("/student")
def student_dashboard():
    if session.get("role") != "student":
        return redirect("/login")

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM student WHERE student_id = %s",
        (session["student_id"],)
    )

    student = cursor.fetchone()

    cursor.execute("""
        SELECT
            pd.drive_id,
            c.company_name,
            pd.job_role,
            pd.package_lpa,
            pd.drive_date
        FROM student s
        JOIN placement_drive pd
            ON s.campus_id = pd.campus_id
        JOIN company c
            ON pd.company_id = c.company_id
        WHERE s.student_id = %s
          AND s.cgpa >= pd.minimum_cgpa
          AND s.backlogs <= pd.maximum_backlogs
        ORDER BY pd.package_lpa DESC
    """, (session["student_id"],))

    companies = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template(
        "student_dashboard.html",
        student=student,
        companies=companies
    )


@app.route("/officer")
@app.route("/officer")
@app.route("/officer")
def officer_dashboard():
    if session.get("role") != "officer":
        return redirect("/login")

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM company")
    companies = cursor.fetchall()

    cursor.execute("SELECT * FROM campus")
    campuses = cursor.fetchall()

    cursor.execute("SELECT * FROM department")
    departments = cursor.fetchall()

    cursor.execute("""
        SELECT
            pd.drive_id,
            c.company_name,
            ca.campus_name,
            pd.job_role,
            pd.package_lpa,
            pd.minimum_cgpa,
            pd.maximum_backlogs,
            pd.drive_date
        FROM placement_drive pd
        JOIN company c ON pd.company_id = c.company_id
        JOIN campus ca ON pd.campus_id = ca.campus_id
        ORDER BY pd.drive_date
    """)

    drives = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template(
        "officer_dashboard.html",
        companies=companies,
        campuses=campuses,
        departments=departments,
        drives=drives
    )


@app.route("/add_company", methods=["POST"])
def add_company():
    if session.get("role") != "officer":
        return redirect("/login")

    company_name = request.form["company_name"]
    industry = request.form["industry"]

    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute("""
        INSERT INTO company (company_name, industry)
        VALUES (%s, %s)
    """, (company_name, industry))

    db.commit()

    cursor.close()
    db.close()

    return redirect("/officer")


@app.route("/add_drive", methods=["POST"])
def add_drive():
    if session.get("role") != "officer":
        return redirect("/login")

    company_id = request.form["company_id"]
    campus_id = request.form["campus_id"]
    job_role = request.form["job_role"]
    package_lpa = request.form["package_lpa"]
    minimum_cgpa = request.form["minimum_cgpa"]
    maximum_backlogs = request.form["maximum_backlogs"]
    drive_date = request.form["drive_date"]

    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute("""
        INSERT INTO placement_drive
        (company_id, campus_id, job_role, package_lpa,
         minimum_cgpa, maximum_backlogs, drive_date)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (
        company_id,
        campus_id,
        job_role,
        package_lpa,
        minimum_cgpa,
        maximum_backlogs,
        drive_date
    ))

    db.commit()

    cursor.close()
    db.close()

    return redirect("/officer")
@app.route("/apply/<int:drive_id>", methods=["POST"])
def apply(drive_id):
    if session.get("role") != "student":
        return redirect("/login")

    student_id = session["student_id"]

    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute("""
        INSERT INTO application (student_id, drive_id, status)
        SELECT s.student_id, pd.drive_id, 'Applied'
        FROM student s
        JOIN placement_drive pd
            ON s.campus_id = pd.campus_id
        WHERE s.student_id = %s
          AND pd.drive_id = %s
          AND s.cgpa >= pd.minimum_cgpa
          AND s.backlogs <= pd.maximum_backlogs
    """, (student_id, drive_id))

    db.commit()

    cursor.close()
    db.close()

    return redirect("/student")


@app.route("/applications")
def applications():
    if session.get("role") != "student":
        return redirect("/login")

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            c.company_name,
            pd.job_role,
            pd.package_lpa,
            pd.drive_date,
            a.status,
            a.applied_date,
            a.updated_at
        FROM application a
        JOIN placement_drive pd
            ON a.drive_id = pd.drive_id
        JOIN company c
            ON pd.company_id = c.company_id
        WHERE a.student_id = %s
        ORDER BY a.applied_date DESC
    """, (session["student_id"],))

    applications = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template(
        "applications.html",
        applications=applications
    )


@app.route("/officer/applications")
def officer_applications():
    if session.get("role") != "officer":
        return redirect("/login")

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            a.application_id,
            s.name,
            s.registration_no,
            c.company_name,
            pd.job_role,
            a.status,
            a.applied_date
        FROM application a
        JOIN student s
            ON a.student_id = s.student_id
        JOIN placement_drive pd
            ON a.drive_id = pd.drive_id
        JOIN company c
            ON pd.company_id = c.company_id
        ORDER BY a.applied_date DESC
    """)

    applications = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template(
        "officer_applications.html",
        applications=applications
    )


@app.route("/officer/update_application/<int:application_id>", methods=["POST"])
def update_application(application_id):
    if session.get("role") != "officer":
        return redirect("/login")

    status = request.form["status"]

    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute("""
        UPDATE application
        SET status = %s
        WHERE application_id = %s
    """, (status, application_id))

    db.commit()

    cursor.close()
    db.close()

    return redirect("/officer/applications")
def logout():
    session.clear()
    return redirect("/login")


if __name__ == "__main__":
    app.run(debug=True)