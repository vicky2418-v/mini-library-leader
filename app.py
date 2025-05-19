from flask import Flask, render_template, send_from_directory ,request, jsonify, session
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# In-memory "database"
users = {}
books = {}
transactions = []

UPLOAD_FOLDER = 'static/covers'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/static/covers/<filename>')
def cover_image(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)




@app.route('/login', methods=['POST'])
def login():
    if not request.is_json:
        return jsonify({'status': 'error', 'message': 'Missing JSON body'}), 400
    data = request.get_json()
    name = data.get('name', '').strip()
    if not name:
        return jsonify({'status':'error', 'message':'Name required'}), 400
    # Check for existing user (case-insensitive)
    user = next((u for u in users.values() if u['name'].lower() == name.lower()), None)
if user:
    session['user_id'] = user['id']
    return jsonify({'status':'success', 'user': user})
else:
    if any(u['name'].lower() == name.lower() for u in users.values()):
        return jsonify({'status':'error', 'message':'Username already exists'}), 400
    user_id = str(len(users) + 1)
    user = {'id': user_id, 'name': name}
    users[user_id] = user
    session['user_id'] = user['id']
    return jsonify({'status':'success', 'user': user})
     

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return jsonify({'status':'success'})

@app.route('/session')
def check_session():
    user_id = session.get('user_id')
    if user_id and user_id in users:
        return jsonify({'logged_in':True, 'user':users[user_id]})
    return jsonify({'logged_in':False})

    

@app.route('/add_book', methods=['POST'])
def add_book():
    if 'user_id' not in session:
        return jsonify({'status':'error', 'message':'Login required'}), 401
    title = request.form.get('title', '').strip()
    author = request.form.get('author', '').strip()
    file = request.files.get('cover')
    if not title or not author or not file:
        return jsonify({'status':'error', 'message':'All fields required'}), 400
    if not allowed_file(file.filename):
        return jsonify({'status':'error', 'message':'Invalid image type. Allowed: png, jpg, jpeg, gif'}), 400
    filename = secure_filename(file.filename)
    file.save(os.path.join(UPLOAD_FOLDER, filename))
    book_id = str(len(books) + 1)
    books[book_id] = {
        'id': book_id,
        'title': title,
        'author': author,
        'cover': filename,
        'owner': session['user_id']
    }
    return jsonify({'status':'success', 'book': books[book_id]})


