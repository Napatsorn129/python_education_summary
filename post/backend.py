from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_session import Session
import os
import sqlite3

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.secret_key = 'brand_new_secret_key_xyz123'

# ตั้งค่า Session ให้เก็บในเซิร์ฟเวอร์ (filesystem)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_FILE_DIR'] = './flask_session'  # โฟลเดอร์เก็บ session
Session(app)

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def get_db():
    conn = sqlite3.connect('summary.db')
    conn.row_factory = sqlite3.Row
    return conn

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

# ล้าง session เก่าทุกครั้งที่รันเซิร์ฟเวอร์
def clear_old_sessions():
    import shutil
    session_dir = './flask_session'
    if os.path.exists(session_dir):
        shutil.rmtree(session_dir)
    os.makedirs(session_dir, exist_ok=True)

@app.before_request
def check_session():
    if request.endpoint not in ['login', 'register', 'static', 'clear_session']:
        if 'user' not in session:
            return redirect(url_for('login'))

@app.route('/clear')
def clear_session():
    session.clear()
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == "12" and password == "1234":
            session.clear()
            session.permanent = False
            session['user'] = username
            flash("เข้าสู่ระบบสำเร็จ")
            return redirect(url_for('index'))
        else:
            flash("ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง")
    
    return render_template('login.html')

@app.route("/", methods=["GET", "POST"])
def index():
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

    posts = []
    for s in summaries:
        post = {
            'id': s['id'],
            'text': s['text'],
            'file': s['image']
        }
        posts.append(post)

    return render_template("index.html", posts=posts, comment_map=comment_map, user=session["user"])

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

@app.route('/home', methods=['GET', 'POST'])
def home():
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
            return redirect(url_for('home'))

        summaries = db.execute("SELECT * FROM summary ORDER BY id DESC").fetchall()
        comments = db.execute("SELECT * FROM comment").fetchall()

    comment_map = {}
    for c in comments:
        comment_map.setdefault(c['summary_id'], []).append(c)

    posts = []
    for s in summaries:
        post = {
            'id': s['id'],
            'text': s['text'],
            'file': s['image']
        }
        posts.append(post)

    return render_template("index.html", posts=posts, comment_map=comment_map, user=session["user"])

@app.route('/sub')
def sub():
    if "user" not in session:
        return redirect(url_for('login'))
    return render_template("s.html", user=session["user"])

@app.route("/logout")
def logout():
    session.clear()
    flash("ออกจากระบบสำเร็จ")
    return redirect(url_for('login'))

if __name__ == "__main__":
    init_db()
    clear_old_sessions()  # ล้าง session เก่าทุกครั้งที่รันเซิร์ฟเวอร์
    app.run(port=5002, debug=True)