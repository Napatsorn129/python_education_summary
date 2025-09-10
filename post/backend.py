import os
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# เก็บโพสต์ในหน่วยความจำ (ถ้าต้องการเก็บถาวรควรใช้ฐานข้อมูล)
posts = []
post_id_counter = 1

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def index():
    global post_id_counter
    if request.method == 'POST':
        text = request.form.get('summary', '')
        file = request.files.get('file')
        filename = None
        if file and allowed_file(file.filename):
            filename = f"{post_id_counter}_{secure_filename(file.filename)}"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        posts.insert(0, {
            'id': post_id_counter,
            'text': text,
            'file': filename
        })
        post_id_counter += 1
        return redirect(url_for('index'))
    return render_template('index.html', posts=posts)

@app.route('/share/<int:post_id>')
def share(post_id):
    post = next((p for p in posts if p['id'] == post_id), None)
    if not post:
        return "ไม่พบโพสต์", 404
    return render_template('share.html', summary={'text': post['text'], 'image': post['file']}, comments=[])

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(host='0.0.0.0', port=5000, debug=True)