from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_session import Session
import os
import json
from datetime import datetime

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.secret_key = 'brand_new_secret_key_xyz123'

# ตั้งค่า Session ให้เก็บในเซิร์ฟเวอร์ (filesystem)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_FILE_DIR'] = './flask_session'
Session(app)

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ไฟล์เก็บข้อมูล
DATA_FILE = 'posts_data.json'
USERS_FILE = 'users_data.json'

def load_data():
    """โหลดข้อมูลโพสต์จากไฟล์ JSON"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'posts': [], 'comments': []}

def save_data(data):
    """บันทึกข้อมูลโพสต์ลงไฟล์ JSON"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_users():
    """โหลดข้อมูลผู้ใช้จากไฟล์ JSON"""
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_users(users):
    """บันทึกข้อมูลผู้ใช้ลงไฟล์ JSON"""
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

def clear_old_sessions():
    """ล้าง session เก่า"""
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
            return redirect(url_for('home'))
        else:
            flash("ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง")
    
    return render_template('login.html')

@app.route("/")
def index():
    return redirect(url_for('home'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        users = load_users()
        
        # ตรวจสอบว่ามีชื่อผู้ใช้ซ้ำหรือไม่
        if any(u['username'] == username for u in users):
            flash("ชื่อผู้ใช้ซ้ำ")
        else:
            users.append({'username': username, 'password': password})
            save_users(users)
            flash("สมัครสมาชิกสำเร็จ")
            return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/home', methods=['GET', 'POST'])
def home():
    category_names = {
        'math': 'คณิตศาสตร์',
        'physics': 'ฟิสิกส์',
        'biology': 'ชีววิทยา',
        'chemistry': 'เคมี',
        'history': 'ประวัติศาสตร์',
        'thai': 'ภาษาไทย'
    }
    
    data = load_data()
    
    if request.method == "POST":
        text = request.form.get("summary")
        category = request.form.get("category")
        file = request.files.get("file")
        file_filename = None
        
        if file and file.filename:
            file_filename = f"{int.from_bytes(os.urandom(8),'big')}_{file.filename}"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], file_filename))
        
        # สร้าง ID ใหม่
        new_id = max([p['id'] for p in data['posts']], default=0) + 1
        
        # เพิ่มโพสต์ใหม่
        new_post = {
            'id': new_id,
            'user': session['user'],
            'text': text,
            'file': file_filename,
            'category': category,
            'timestamp': datetime.now().isoformat()
        }
        
        data['posts'].insert(0, new_post)  # ใส่ไว้ด้านบนสุด
        save_data(data)
        
        flash("เพิ่มสรุปแล้ว")
        return redirect(url_for('home'))
    
    # จัดเตรียมข้อมูลสำหรับแสดงผล
    comment_map = {}
    for c in data.get('comments', []):
        comment_map.setdefault(c['summary_id'], []).append(c)
    
    posts = []
    for s in data['posts']:
        post = {
            'id': s['id'],
            'text': s['text'],
            'file': s.get('file'),
            'category': s.get('category'),
            'category_display': category_names.get(s.get('category'), s.get('category')) if s.get('category') else None,
            'category_class': s.get('category')
        }
        posts.append(post)
    
    return render_template("index.html", posts=posts, comment_map=comment_map, user=session["user"])

@app.route('/sub')
def sub():
    if "user" not in session:
        return redirect(url_for('login'))
    return render_template("s.html", user=session["user"])

@app.route('/math')
def math():
    if "user" not in session:
        return redirect(url_for('login'))
    
    category_names = {
        'math': 'คณิตศาสตร์',
        'physics': 'ฟิสิกส์',
        'biology': 'ชีววิทยา',
        'chemistry': 'เคมี',
        'history': 'ประวัติศาสตร์',
        'thai': 'ภาษาไทย'
    }
    
    data = load_data()
    
    # กรองเฉพาะโพสต์วิชาคณิตศาสตร์
    filtered_posts = [p for p in data['posts'] if p.get('category') == 'math']
    
    comment_map = {}
    for c in data.get('comments', []):
        comment_map.setdefault(c['summary_id'], []).append(c)
    
    posts = []
    for s in filtered_posts:
        post = {
            'id': s['id'],
            'text': s['text'],
            'file': s.get('file'),
            'category': s.get('category'),
            'category_display': category_names.get(s.get('category'), s.get('category')) if s.get('category') else None,
            'category_class': s.get('category')
        }
        posts.append(post)
    
    return render_template("math.html", posts=posts, comment_map=comment_map, user=session["user"])

@app.route('/physics')
def physics():
    if "user" not in session:
        return redirect(url_for('login'))
    
    category_names = {
        'math': 'คณิตศาสตร์',
        'physics': 'ฟิสิกส์',
        'biology': 'ชีววิทยา',
        'chemistry': 'เคมี',
        'history': 'ประวัติศาสตร์',
        'thai': 'ภาษาไทย'
    }
    
    data = load_data()
    filtered_posts = [p for p in data['posts'] if p.get('category') == 'physics']
    
    comment_map = {}
    for c in data.get('comments', []):
        comment_map.setdefault(c['summary_id'], []).append(c)
    
    posts = []
    for s in filtered_posts:
        post = {
            'id': s['id'],
            'text': s['text'],
            'file': s.get('file'),
            'category': s.get('category'),
            'category_display': category_names.get(s.get('category'), s.get('category')) if s.get('category') else None,
            'category_class': s.get('category')
        }
        posts.append(post)
    
    return render_template("physics.html", posts=posts, comment_map=comment_map, user=session["user"])

@app.route('/biology')
def biology():
    if "user" not in session:
        return redirect(url_for('login'))
    
    category_names = {
        'math': 'คณิตศาสตร์',
        'physics': 'ฟิสิกส์',
        'biology': 'ชีววิทยา',
        'chemistry': 'เคมี',
        'history': 'ประวัติศาสตร์',
        'thai': 'ภาษาไทย'
    }
    
    data = load_data()
    filtered_posts = [p for p in data['posts'] if p.get('category') == 'biology']
    
    comment_map = {}
    for c in data.get('comments', []):
        comment_map.setdefault(c['summary_id'], []).append(c)
    
    posts = []
    for s in filtered_posts:
        post = {
            'id': s['id'],
            'text': s['text'],
            'file': s.get('file'),
            'category': s.get('category'),
            'category_display': category_names.get(s.get('category'), s.get('category')) if s.get('category') else None,
            'category_class': s.get('category')
        }
        posts.append(post)
    
    return render_template("biology.html", posts=posts, comment_map=comment_map, user=session["user"])

@app.route('/chemistry')
def chemistry():
    if "user" not in session:
        return redirect(url_for('login'))
    
    category_names = {
        'math': 'คณิตศาสตร์',
        'physics': 'ฟิสิกส์',
        'biology': 'ชีววิทยา',
        'chemistry': 'เคมี',
        'history': 'ประวัติศาสตร์',
        'thai': 'ภาษาไทย'
    }
    
    data = load_data()
    filtered_posts = [p for p in data['posts'] if p.get('category') == 'chemistry']
    
    comment_map = {}
    for c in data.get('comments', []):
        comment_map.setdefault(c['summary_id'], []).append(c)
    
    posts = []
    for s in filtered_posts:
        post = {
            'id': s['id'],
            'text': s['text'],
            'file': s.get('file'),
            'category': s.get('category'),
            'category_display': category_names.get(s.get('category'), s.get('category')) if s.get('category') else None,
            'category_class': s.get('category')
        }
        posts.append(post)
    
    return render_template("chemistry.html", posts=posts, comment_map=comment_map, user=session["user"])

@app.route('/history')
def history():
    if "user" not in session:
        return redirect(url_for('login'))
    
    category_names = {
        'math': 'คณิตศาสตร์',
        'physics': 'ฟิสิกส์',
        'biology': 'ชีววิทยา',
        'chemistry': 'เคมี',
        'history': 'ประวัติศาสตร์',
        'thai': 'ภาษาไทย'
    }
    
    data = load_data()
    filtered_posts = [p for p in data['posts'] if p.get('category') == 'history']
    
    comment_map = {}
    for c in data.get('comments', []):
        comment_map.setdefault(c['summary_id'], []).append(c)
    
    posts = []
    for s in filtered_posts:
        post = {
            'id': s['id'],
            'text': s['text'],
            'file': s.get('file'),
            'category': s.get('category'),
            'category_display': category_names.get(s.get('category'), s.get('category')) if s.get('category') else None,
            'category_class': s.get('category')
        }
        posts.append(post)
    
    return render_template("history.html", posts=posts, comment_map=comment_map, user=session["user"])

@app.route('/thai')
def thai():
    if "user" not in session:
        return redirect(url_for('login'))
    
    category_names = {
        'math': 'คณิตศาสตร์',
        'physics': 'ฟิสิกส์',
        'biology': 'ชีววิทยา',
        'chemistry': 'เคมี',
        'history': 'ประวัติศาสตร์',
        'thai': 'ภาษาไทย'
    }
    
    data = load_data()
    filtered_posts = [p for p in data['posts'] if p.get('category') == 'thai']
    
    comment_map = {}
    for c in data.get('comments', []):
        comment_map.setdefault(c['summary_id'], []).append(c)
    
    posts = []
    for s in filtered_posts:
        post = {
            'id': s['id'],
            'text': s['text'],
            'file': s.get('file'),
            'category': s.get('category'),
            'category_display': category_names.get(s.get('category'), s.get('category')) if s.get('category') else None,
            'category_class': s.get('category')
        }
        posts.append(post)
    
    return render_template("thai.html", posts=posts, comment_map=comment_map, user=session["user"])

@app.route("/logout")
def logout():
    session.clear()
    flash("ออกจากระบบสำเร็จ")
    return redirect(url_for('login'))

if __name__ == "__main__":
    clear_old_sessions()
    app.run(port=5002, debug=True)