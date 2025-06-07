from flask import Flask, render_template, request, redirect, session, url_for, send_from_directory
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"
UPLOAD_FOLDER = "static/uploads"
USER_FILE = "users.txt"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def save_user(username, password):
    with open(USER_FILE, "a") as f:
        f.write(f"{username}:{password}\n")

def user_exists(username, password):
    if not os.path.exists(USER_FILE):
        return False
    with open(USER_FILE, "r") as f:
        users = f.readlines()
    return f"{username}:{password}\n" in users

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if not user_exists(username, password):
            save_user(username, password)
        session["username"] = username
        user_folder = os.path.join(UPLOAD_FOLDER, username)
        os.makedirs(user_folder, exist_ok=True)
        return redirect("/upload")
    return render_template("login.html")

@app.route("/upload", methods=["GET", "POST"])
def upload():
    if "username" not in session:
        return redirect("/")
    username = session["username"]
    user_folder = os.path.join(UPLOAD_FOLDER, username)
    if request.method == "POST":
        for file in request.files.getlist("images"):
            if file:
                file.save(os.path.join(user_folder, file.filename))
    images = os.listdir(user_folder)
    return render_template("gallery.html", images=images, username=username)

@app.route("/uploads/<username>/<filename>")
def uploaded_file(username, filename):
    return send_from_directory(os.path.join(UPLOAD_FOLDER, username), filename)

if __name__ == "__main__":
    app.run(debug=True)
