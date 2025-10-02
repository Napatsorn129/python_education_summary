from flask import Flask, render_template, request, redirect, url_for, flash, session
import os
import sqlite3

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.secret_key = 'your_secret_key'

# สร้างโฟลเดอร์เก็บรูปถ้ายังไม่มี
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ฟังก์ชันเชื่อมต่อฐานข้อมูล
def get_db():
    conn = sqlite3.connect('summary.db')
    conn.row_factory = sqlite3.Row
    return conn

# ฟังก์ชันสร้างตารางถ้ายังไม่มี
def init_db():
    with get_db() as db:
        db.execute('''CREATE TABLE IF NOT EXISTS summary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT,
            image TEXT
        )''')
        db.execute('''CREATE TABLE IF NOT EXISTS comment (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            summary_id INTEGER,
            text TEXT
        )''')
        db.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )''')

# หน้า Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = "12"
        password = "1234"
        return render_template('index.html')
    else:
                flash("ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง")
    return render_template('login.html')

# หน้าแรก
@app.route("/", methods=["GET", "POST"])
def index():
    if "user" not in session:
        return redirect(url_for('login'))

    with get_db() as db:
        if request.method == "POST":
            text = request.form.get("summary")
            file = request.files.get("file")
            file_filename = None
            if file and file.filename:
                file_filename = f"{int.from_bytes(os.urandom(8),'big')}_{file.filename}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], file_filename))
            db.execute("INSERT INTO summary (text, image) VALUES (?, ?)", (text, file_filename))
            db.commit()
            flash("เพิ่มสรุปแล้ว")
            return redirect(url_for('index'))

        summaries = db.execute("SELECT * FROM summary ORDER BY id DESC").fetchall()
        comments = db.execute("SELECT * FROM comment").fetchall()

    comment_map = {}
    for c in comments:
        comment_map.setdefault(c['summary_id'], []).append(c)

    # แปลง summaries เป็น posts และ image เป็น file สำหรับ template
    posts = []
    for s in summaries:
        post = {
            'id': s['id'],
            'text': s['text'],
            'file': s['image']
        }
        posts.append(post)

    return render_template("index.html", posts=posts, comment_map=comment_map, user=session["user"])

# หน้า Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        with get_db() as db:
            try:
                db.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
                db.commit()
                flash("สมัครสมาชิกสำเร็จ")
                return redirect(url_for('login'))
            except sqlite3.IntegrityError:
                flash("ชื่อผู้ใช้ซ้ำ")
    return render_template('register.html')

# Logout
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for('login'))

if __name__ == "__main__":
    init_db()
    app.run(port=5002, debug=True)