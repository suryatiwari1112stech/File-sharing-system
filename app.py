from flask import Flask, render_template, request, redirect, session, send_from_directory
import sqlite3
import os

# ==============================
# APP CONFIGURATION
# ==============================

app = Flask(__name__)
app.secret_key = "secret123"

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# uploads folder auto create
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


# ==============================
# HOME PAGE
# ==============================

@app.route("/")
def home():
    return render_template("login.html")


# ==============================
# SIGNUP SYSTEM
# ==============================

@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("notes.db")
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, password)
        )

        conn.commit()
        conn.close()

        return redirect("/")

    return render_template("signup.html")


# ==============================
# LOGIN SYSTEM
# ==============================

@app.route("/login", methods=["POST"])
def login():

    username = request.form["username"]
    password = request.form["password"]

    conn = sqlite3.connect("notes.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (username, password)
    )

    user = cursor.fetchone()

    conn.close()

    if user:
        session["user"] = username
        return redirect("/dashboard")

    return "invalid login"


# ==============================
# USER DASHBOARD
# ==============================

@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect("/")

    return render_template("dashboard.html", user=session["user"])


# ==============================
# UPLOAD NOTES PAGE
# ==============================

@app.route("/upload")
def upload():

    if "user" not in session:
        return redirect("/")

    return render_template("upload.html")


# ==============================
# UPLOAD NOTES SYSTEM
# ==============================

@app.route("/upload_notes", methods=["POST"])
def upload_notes():

    if "user" not in session:
        return redirect("/")

    title = request.form["title"]
    category = request.form["category"]
    file = request.files["file"]

    filename = file.filename

    file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

    conn = sqlite3.connect("notes.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO notes (username,title,category,filename,status) VALUES (?,?,?,?,?)",
        (session["user"], title, category, filename, "pending")
    )

    conn.commit()
    conn.close()

    return redirect("/dashboard")


# ==============================
# MY NOTES (USER NOTES)
# ==============================

@app.route("/my_notes")
def my_notes():

    if "user" not in session:
        return redirect("/")

    conn = sqlite3.connect("notes.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM notes WHERE username=?",
        (session["user"],)
    )

    notes = cursor.fetchall()

    conn.close()

    return render_template("my_notes.html", notes=notes)


# ==============================
# USER DELETE OWN NOTES
# ==============================

@app.route("/delete_my_note/<int:id>")
def delete_my_note(id):

    if "user" not in session:
        return redirect("/")

    conn = sqlite3.connect("notes.db")
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM notes WHERE id=? AND username=?",
        (id, session["user"])
    )

    conn.commit()
    conn.close()

    return redirect("/my_notes")


# ==============================
# VIEW NOTES
# ==============================
@app.route("/notes")
def notes():

    if "user" not in session:
        return redirect("/")

    search = request.args.get("search")

    conn = sqlite3.connect("notes.db")
    cursor = conn.cursor()

    if search:
        cursor.execute(
            "SELECT * FROM notes WHERE status='approved' AND title LIKE ?",
            ('%' + search + '%',)
        )
    else:
        cursor.execute("SELECT * FROM notes WHERE status='approved'")

    notes = cursor.fetchall()

    conn.close()

    return render_template("notes.html", notes=notes)


# ==============================
# FILE VIEW ROUTE
# ==============================

@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory("uploads", filename)


# ==============================
# FILE DOWNLOAD ROUTE
# ==============================

@app.route("/download/<filename>")
def download_file(filename):
    return send_from_directory("uploads", filename, as_attachment=True)


# ==============================
# ADMIN LOGIN SYSTEM
# ==============================

@app.route("/admin_login", methods=["GET","POST"])
def admin_login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "admin123":

            session["admin"] = "admin"

            return redirect("/admin")

        return "Invalid Admin Login"

    return render_template("admin_login.html")


# ==============================
# ADMIN PANEL
# ==============================

@app.route("/admin")
def admin():

    # ADMIN SECURITY (NEW)
    if "admin" not in session:
        return redirect("/admin_login")

    conn = sqlite3.connect("notes.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM notes WHERE status='pending'")
    notes = cursor.fetchall()

    conn.close()

    return render_template("admin.html", notes=notes)


# ==============================
# APPROVE NOTES
# ==============================

@app.route("/approve/<int:id>")
def approve(id):

    if "admin" not in session:
        return redirect("/admin_login")

    conn = sqlite3.connect("notes.db")
    cursor = conn.cursor()

    cursor.execute("UPDATE notes SET status='approved' WHERE id=?", (id,))

    conn.commit()
    conn.close()

    return redirect("/admin")


# ==============================
# DELETE NOTES (ADMIN)
# ==============================

@app.route("/delete/<int:id>")
def delete(id):

    if "admin" not in session:
        return redirect("/admin_login")

    conn = sqlite3.connect("notes.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM notes WHERE id=?", (id,))

    conn.commit()
    conn.close()

    return redirect("/admin")


# ==============================
# ADMIN LOGOUT (NEW)
# ==============================

@app.route("/admin_logout")
def admin_logout():

    session.pop("admin", None)

    return redirect("/admin_login")


# ==============================
# USER LOGOUT
# ==============================

@app.route("/logout")
def logout():

    session.pop("user", None)

    return redirect("/")


# ==============================
# RUN SERVER
# ==============================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)