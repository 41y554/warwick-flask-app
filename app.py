import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, redirect, session, url_for

app = Flask(__name__)
app.secret_key = "your-secret-key"
app.config['TEMPLATES_AUTO_RELOAD'] = True

DB = "applications.db"

def init_db():
    with sqlite3.connect(DB) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY,
                name TEXT,
                email TEXT,
                course TEXT,
                reason TEXT,
                timestamp TEXT,
                status TEXT DEFAULT 'pending'
            )
            """
        )

def fetch_query(query, args=(), one=False):
    with sqlite3.connect(DB) as connection:
        cursor = connection.execute(query, args)
        results = cursor.fetchall()
    return results[0] if one else results




## routes ##
@app.route("/")
@app.route("/home")
def course_summary():
    details = [
        {'id': 1, 'course': 'Management', 'deadline': '18th May', 'length':'Two Weeks','price':'£150'},
        {'id': 2, 'course': 'Business Analytics', 'deadline': '18th May', 'length':'Two Weeks', 'price':'£150'},
        {'id': 3, 'course': 'International Business', 'deadline': '18th May', 'length':'Two Weeks', 'price':'£150'},
        {'id': 4, 'course': 'Machine Learning', 'deadline': '18th May', 'length':'Two Weeks', 'price':'£150'},
        {'id': 5, 'course': 'Computer Science', 'deadline': '18th May', 'length':'Two Weeks', 'price':'£150'},
        {'id': 6, 'course': 'Artificial Intelligence', 'deadline': '18th May', 'length':'Two Weeks', 'price':'£150'},
        {'id': 7, 'course': 'Biology', 'deadline': '18th May', 'length':'Two Weeks', 'price':'£150'},
        {'id': 8, 'course': 'Chemistry', 'deadline': '18th May', 'length':'Two Weeks', 'price':'£150'},
        {'id': 9, 'course': 'Physics', 'deadline': '18th May', 'length':'Two Weeks', 'price':'£150'}
    ]
    print(details)
    return render_template('home.html', items=details)

@app.route("/business")
def business_page():
    return render_template('business.html', item_name='Business')

@app.route("/technology")
def technology_page():
    return render_template('technology.html', item_name='Technology')

@app.route("/science")
def science_page():
    return render_template('science.html', item_name='Science')

##application##

@app.route("/application", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"].strip()
        email = request.form["email"].strip()
        course = request.form["course"].strip()
        reason = request.form["applicationreason"].strip()
        timestamp = datetime.now().isoformat(sep=" ", timespec="seconds")

        with sqlite3.connect(DB) as connection:
            connection.execute(
                "INSERT INTO applications (name, email, course, reason, timestamp, status) VALUES (?, ?, ?, ?, ?, ?)",
                (name, email, course, reason, timestamp, "pending")
            )
        return render_template("receipt.html", name=name, course=course)

    return render_template("application.html")


##admin login/dashboard##

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "admin":
            # Set session variable to indicate the user is logged in
            session["admin"] = True
            return redirect(url_for("dashboard"))  # Redirect to dashboard on successful login
        else:
            # Return error message if credentials are invalid
            return render_template("login.html", error="Invalid credentials")

    return render_template("login.html")  # Show login page when method is GET


@app.route("/admin/dashboard")
def dashboard():
    if not session.get("admin"):
        return redirect(url_for("login"))

    applications = fetch_query("SELECT id, name, email, course, reason, timestamp, status FROM applications ORDER BY id DESC")
    return render_template("dashboard.html", applications=applications)

@app.route("/admin/delete/<int:reg_id>")
def delete(reg_id):
    if not session.get("admin"):
        return redirect(url_for("login"))

    with sqlite3.connect(DB) as connection:
        connection.execute("DELETE FROM applications WHERE id = ?", (reg_id,))
    return redirect(url_for("dashboard"))

#subject to change
@app.route("/admin/accept/<int:reg_id>")
def accept(reg_id):
    if not session.get("admin"):
        return redirect(url_for("login"))
    with sqlite3.connect(DB) as connection:
        connection.execute("UPDATE applications SET status = 'accepted' WHERE id = ?", (reg_id,))
    return redirect(url_for("dashboard"))

@app.route("/admin/reject/<int:reg_id>")
def reject(reg_id):
    if not session.get("admin"):
        return redirect(url_for("login"))
    with sqlite3.connect(DB) as connection:
        connection.execute("UPDATE applications SET status = 'rejected' WHERE id = ?", (reg_id,))
    return redirect(url_for("dashboard"))
#subject to change^^

@app.route("/admin/view/<int:app_id>")
def view(app_id):
    if not session.get("admin"):
        return redirect(url_for("login"))

    application = fetch_query(
        "SELECT id, name, email, course, reason, timestamp, status FROM applications WHERE id = ?",
        (app_id,),
        one=True
    )
    return render_template("view.html", application=application)


@app.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect(url_for("course_summary"))



if __name__ == '__main__':
    init_db()
    app.run(debug=True)