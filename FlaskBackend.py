import os
from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import socket
import sqlite3
import uuid

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'server_grass_photos'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
PORT = 5000

# Create upload directory if it doesn't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def init_db():
    conn = sqlite3.connect('grassbuddy.db')
    c = conn.cursor()
    
    # Create users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            name TEXT NOT NULL,
            auth_token TEXT,
            score INTEGER DEFAULT 0
        )
    ''')
    
    # Create photos table
    c.execute('''
        CREATE TABLE IF NOT EXISTS photos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            user_id INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    
    # Create notifications table
    c.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            type TEXT,
            message TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id))''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS friends (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            friend_id INTEGER,
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(friend_id) REFERENCES users(id)
        
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS friend_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER,
            receiver_id INTEGER,
            status TEXT DEFAULT 'pending',
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(sender_id) REFERENCES users(id),
            FOREIGN KEY(receiver_id) REFERENCES users(id),
            UNIQUE(sender_id, receiver_id)
        )
    ''')

    
    conn.commit()
    conn.close()

def connect_db():
    return sqlite3.connect('grassbuddy.db')

@app.route('/')
def index():
    return "GrassBuddy Server is Running! Touch Grass."

@app.route('/register', methods=['POST'])
def register():
    # Expects JSON: {"username": "foo", "password": "bar", "name": "Foo Bar"}
    data = request.get_json()
    if not data or not all(k in data for k in ('username', 'password', 'name')):
        return jsonify({'error': 'Missing fields'}), 400
    
    username = data['username']
    password = data['password']
    name = data['name']
    
    # Hash the password
    # Standard practice: Hash on the server.
    # The complexity of securely handling seeds/salts on the client is hard.
    # We rely on HTTPS to protect the password in transit.
    hashed_pw = generate_password_hash(password)
    
    conn = connect_db()
    c = conn.cursor()
    
    try:
        c.execute('INSERT INTO users (username, password_hash, name) VALUES (?, ?, ?)', 
                  (username, hashed_pw, name))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'error': 'Username already exists'}), 409
        
    conn.close()
    return jsonify({'message': 'User registered successfully'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not all(k in data for k in ('username', 'password')):
        return jsonify({'error': 'Missing fields'}), 400
        
    username = data['username']
    password = data['password']
    
    conn = connect_db()
    c = conn.cursor()
    
    c.execute('SELECT id, password_hash, name FROM users WHERE username = ?', (username,))
    row = c.fetchone()
    
    if not row:
        conn.close()
        return jsonify({'error': 'Invalid credentials'}), 401
        
    user_id, stored_hash, name = row
    
    if check_password_hash(stored_hash, password):
        # Login success! Generate a token for this session
        token = str(uuid.uuid4())
        
        c.execute('UPDATE users SET auth_token = ? WHERE id = ?', (token, user_id))
        conn.commit()
        conn.close()
        
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user_id': user_id,
            'name': name
        }), 200
    else:
        conn.close()
        return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Avoid overwriting by prepending count or using unique IDs in production
        # For now, just save it.
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(save_path)
        
        # Add to DB if authenticated
        auth_header = request.headers.get('Authorization')
        user_id = None
        notify_friends = request.form.get('notify_friends') == 'true'

        if auth_header:
             # Extract token
            token = auth_header.split(" ")[1] if " " in auth_header else auth_header
            conn = connect_db()
            c = conn.cursor()
            c.execute('SELECT id, name FROM users WHERE auth_token = ?', (token,))
            row = c.fetchone()
            if row:
                user_id, user_name = row
                # Insert into photos
                c.execute('INSERT INTO photos (filename, user_id) VALUES (?, ?)', (filename, user_id))
                
                c.execute('UPDATE users SET score = score + 10 WHERE id = ?', (user_id,))
                
                if notify_friends:
                    # Find all friends
                    c.execute('SELECT friend_id FROM friends WHERE user_id = ?', (user_id,))
                    friends = c.fetchall()
                    for friend_row in friends:
                        friend_id = friend_row[0]
                        msg = f"{user_name} just touched grass!"
                        c.execute('INSERT INTO notifications (user_id, type, message) VALUES (?, ?, ?)',
                                  (friend_id, 'FEED_POST', msg))
                
                conn.commit()
            conn.close()

        return jsonify({
            'message': 'Grass touched successfully!',
            'filename': filename,
            'url': f'/images/{filename}',
            'score_added': 10 if user_id else 0
        }), 201
        
    return jsonify({'error': 'File type not allowed'}), 400

@app.route('/feed', methods=['GET'])
def get_feed():
    conn = connect_db()
    c = conn.cursor()
    # Join photos with users to get the uploader's name
    c.execute('''
        SELECT photos.filename, photos.timestamp, users.name 
        FROM photos 
        LEFT JOIN users ON photos.user_id = users.id 
        ORDER BY photos.timestamp DESC
    ''')
    rows = c.fetchall()
    conn.close()
    
    files = []
    for row in rows:
        filename, timestamp, user_name = row
        files.append({
            'filename': filename,
            'url': f'/images/{filename}',
            'timestamp': timestamp,
            'user': user_name or 'Anonymous'
        })
    
    return jsonify({'feed': files}), 200

@app.route('/images/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/notifications', methods=['GET'])
def get_notifications():
    # Authenticate User
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({'error': 'Missing Authorization header'}), 401
    
    # Extract token
    token = auth_header.split(" ")[1] if " " in auth_header else auth_header

    conn = connect_db()
    c = conn.cursor()
    
    # 1. Verify User
    c.execute('SELECT id, name FROM users WHERE auth_token = ?', (token,))
    user_row = c.fetchone()
    print(f"Found user row: {user_row}")
    if not user_row:
        conn.close()
        return jsonify({'error': 'Invalid auth token'}), 401
    
    user_id = user_row[0]
    print(f"Fetching notifications for user ID: {user_id} ({user_row[1]})")

    # 2. Get notifications for this user
    c.execute('SELECT id, type, message, timestamp FROM notifications WHERE user_id = ? ORDER BY timestamp ASC', (user_id,))
    notifs = c.fetchall()
    
    response_data = []
    for notif in notifs:
        notif_id, n_type, msg, ts = notif
        response_data.append({
            'id': notif_id,
            'type': n_type,
            'message': msg,
            'timestamp': ts,
            'from': 'See message'
        })
    
    # 3. Delete notifications (or mark as read) so they aren't shown again
    if notifs:
        c.execute('DELETE FROM notifications WHERE user_id = ?', (user_id,))
        conn.commit()
    
    conn.close()
    return jsonify({'notifications': response_data}), 200

@app.route('/users/<user_id>/friends', methods=['GET'])
def get_friends(user_id):
    conn = connect_db()
    c = conn.cursor()
    
    # Verify user exists
    c.execute('SELECT id, name FROM users WHERE id = ?', (user_id,))
    user = c.fetchone()
    if not user:
        conn.close()
        return jsonify({'error': 'User not found'}), 404
    
    # Get friends (users linked in friends table)
    # This assumes friends table stores user_id -> friend_id relationship
    c.execute('''
        SELECT users.id, users.name 
        FROM users 
        JOIN friends ON users.id = friends.friend_id 
        WHERE friends.user_id = ?
    ''', (user_id,))
    
    rows = c.fetchall()
    conn.close()
    
    friends_list = [{'id': r[0], 'name': r[1]} for r in rows]
            
    return jsonify({'friends': friends_list}), 200

@app.route('/friend_request/send', methods=['POST'])
def send_friend_request():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({'error': 'Missing Authorization header'}), 401
    token = auth_header.split(" ")[1] if " " in auth_header else auth_header
    
    data = request.get_json()
    target_username = data.get('username')
    
    conn = connect_db()
    c = conn.cursor()
    
    # 1. Get Sender ID
    c.execute('SELECT id, name FROM users WHERE auth_token = ?', (token,))
    sender = c.fetchone()
    if not sender:
        conn.close()
        return jsonify({'error': 'Invalid auth token'}), 401
    sender_id, sender_name = sender

    # 2. Get Receiver ID
    c.execute('SELECT id FROM users WHERE username = ?', (target_username,))
    receiver = c.fetchone()
    if not receiver:
        conn.close()
        return jsonify({'error': 'User not found'}), 404
    receiver_id = receiver[0]

    if sender_id == receiver_id:
        conn.close()
        return jsonify({'error': 'Cannot friend yourself'}), 400

    # 3. Check existing request or friendship
    # Check if a request already exists
    c.execute('SELECT id, status FROM friend_requests WHERE (sender_id = ? AND receiver_id = ?) OR (sender_id = ? AND receiver_id = ?)', 
              (sender_id, receiver_id, receiver_id, sender_id))
    existing_req = c.fetchone()
    
    if existing_req:
        conn.close()
        status = existing_req[1]
        if status == 'accepted':
             return jsonify({'error': 'Already friends'}), 400
        elif status == 'pending':
             return jsonify({'error': 'Friend request already pending'}), 400
        else:
             # If rejected, maybe allow re-request? For now simpler to say pending.
             return jsonify({'error': 'Request already exists'}), 400

    # 4. Insert Request
    c.execute('INSERT INTO friend_requests (sender_id, receiver_id, status) VALUES (?, ?, ?)', 
              (sender_id, receiver_id, 'pending'))
    
    # Notify Receiver
    msg = f"Friend request from {sender_name}"
    c.execute('INSERT INTO notifications (user_id, type, message) VALUES (?, ?, ?)',
              (receiver_id, 'FRIEND_REQ', msg))

    conn.commit()
    conn.close()
    
    return jsonify({'message': f'Friend request sent to {target_username}'}), 201

@app.route('/friend_request/list', methods=['GET'])
def list_friend_requests():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({'error': 'Missing Authorization header'}), 401
    token = auth_header.split(" ")[1] if " " in auth_header else auth_header
    
    conn = connect_db()
    c = conn.cursor()
    
    c.execute('SELECT id FROM users WHERE auth_token = ?', (token,))
    user = c.fetchone()
    if not user:
        conn.close()
        return jsonify({'error': 'Invalid auth token'}), 401
    user_id = user[0]

    # Get pending requests received by this user
    c.execute('''
        SELECT fr.id, u.username, u.name, fr.timestamp 
        FROM friend_requests fr
        JOIN users u ON fr.sender_id = u.id
        WHERE fr.receiver_id = ? AND fr.status = 'pending'
    ''', (user_id,))
    
    reqs = c.fetchall()
    conn.close()
    
    return jsonify({'requests': [{'req_id': r[0], 'username': r[1], 'name': r[2], 'timestamp': r[3]} for r in reqs]}), 200

@app.route('/friend_request/respond', methods=['POST'])
def respond_friend_request():
    auth_header = request.headers.get('Authorization')
    token = auth_header.split(" ")[1] if auth_header and " " in auth_header else auth_header
    data = request.get_json()
    req_id = data.get('req_id')
    action = data.get('action') # 'accept' or 'reject'
    
    conn = connect_db()
    c = conn.cursor()
    
    # Validate user
    c.execute('SELECT id, name FROM users WHERE auth_token = ?', (token,))
    user = c.fetchone()
    if not user:
        conn.close()
        return jsonify({'error': 'Invalid auth token'}), 401
    user_id, user_name = user

    # Get request and verify it's for this user
    c.execute('SELECT sender_id, receiver_id, status FROM friend_requests WHERE id = ?', (req_id,))
    req = c.fetchone()
    
    if not req:
        conn.close()
        return jsonify({'error': 'Request not found'}), 404
    
    sender_id, receiver_id, status = req
    
    if receiver_id != user_id:
        conn.close()
        return jsonify({'error': 'Not authorized for this request'}), 403
    
    if action == 'accept':
        # Update status
        c.execute("UPDATE friend_requests SET status = 'accepted' WHERE id = ?", (req_id,))
        # Add to friends table (bidirectional)
        c.execute("INSERT INTO friends (user_id, friend_id) VALUES (?, ?)", (user_id, sender_id))
        c.execute("INSERT INTO friends (user_id, friend_id) VALUES (?, ?)", (sender_id, user_id))
        
        # Notify Sender
        c.execute("INSERT INTO notifications (user_id, type, message) VALUES (?, ?, ?)",
                  (sender_id, 'FRIEND_ACCEPT', f"{user_name} accepted your friend request!"))
                  
        msg = "Friend request accepted"
    else:
        # Reject
        c.execute("UPDATE friend_requests SET status = 'rejected' WHERE id = ?", (req_id,))
        msg = "Friend request rejected"
        
    conn.commit()
    conn.close()
    
    return jsonify({'message': msg}), 200

@app.route('/leaderboard', methods=['GET']) # Changed route name
def get_leaderboard_data():
    conn = connect_db()
    c = conn.cursor()
    
    # Get all users sorted by score (highest first)
    c.execute('SELECT name, score FROM users ORDER BY score DESC')
    rows = c.fetchall()
    conn.close()
    
    if not rows:
        return jsonify({'leaderboard_data': [], 'message': 'No users yet!'}), 200
    
    # Map rows to dictionary
    leaderboard_list = [{'name': r[0], 'score': r[1]} for r in rows]
            
    return jsonify({'leaderboard_data': leaderboard_list}), 200

@app.route('/nudge/<target_user_id>', methods=['POST'])
def nudge_person(target_user_id):
    # Authenticate Sender
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({'error': 'Missing Authorization header'}), 401
    
    # Extract token (Bearer <token> or simply <token>)
    token = auth_header.split(" ")[1] if " " in auth_header else auth_header

    conn = connect_db()
    c = conn.cursor()
    
    # 1. Verify Sender
    c.execute('SELECT id, name FROM users WHERE auth_token = ?', (token,))
    sender_row = c.fetchone()
    
    if not sender_row:
        conn.close()
        return jsonify({'error': 'Invalid auth token'}), 401
    
    sender_id, sender_name = sender_row

    # 2. Find Target User
    c.execute('SELECT id, name FROM users WHERE id = ?', (target_user_id,))
    target_row = c.fetchone()
    
    if not target_row:
        conn.close()
        return jsonify({'error': 'Target user not found'}), 404

    target_id, target_name = target_row

    # 3. Add Nudge Notification with Sender Info
    message = f"Go touch grass! (from {sender_name})"
    c.execute('INSERT INTO notifications (user_id, type, message) VALUES (?, ?, ?)',
              (target_id, 'NUDGE', message))
    
    conn.commit()
    conn.close()

    print(f"NUDGE: {sender_name} -> {target_name} ({target_user_id})")
    
    return jsonify({
        'message': f'You successfully nudged {target_name}!',
        'target_id': target_id,
        'sender_id': sender_id,
        'action': 'TOUCH_GRASS'
    }), 200

def get_ip_address():
    try:
        # Connect to an external server (doesn't actually send data) to get local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_address = s.getsockname()[0]
        s.close()
        return ip_address
    except Exception:
        return "127.0.0.1"

@app.route('/add_user/<name>', methods=['POST'])
def add_user(name):
    db = connect_db()
    c = db.cursor()
    # Generate a simple auth token (in production, use something secure)
    auth_token = f"auth_{name.lower()}_{len(users) + 1}"
    c.execute("INSERT INTO users (name, auth_token) VALUES (?, ?)", (name, auth_token))
    db.commit()
    user_id = c.lastrowid
    db.close()

def check_schema():
    """Ensure all tables exist even if DB already exists."""
    conn = connect_db()
    c = conn.cursor()
    
    # Create friend_requests table if it doesn't exist (migration for existing users)
    c.execute('''
        CREATE TABLE IF NOT EXISTS friend_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER,
            receiver_id INTEGER,
            status TEXT DEFAULT 'pending',
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(sender_id) REFERENCES users(id),
            FOREIGN KEY(receiver_id) REFERENCES users(id),
            UNIQUE(sender_id, receiver_id)
        )
    ''')
    conn.commit()
    conn.close()

if __name__ == '__main__':
    # Initialize DB (create tables if they don't exist)
    if not os.path.exists('grassbuddy.db'):
        init_db()
        print("Initialized database 'grassbuddy.db'")
    else:
        check_schema()
        print("Checked database schema.")

    # host='0.0.0.0' allows other devices on the network to access it
    ip = get_ip_address()
    print(f"\n--- GrassBuddy Server ---")
    print(f"Listening on: http://{ip}:{PORT}")
    print(f"Local access: http://127.0.0.1:{PORT}")
    print(f"-------------------------\n")
    
    app.run(host='0.0.0.0', port=PORT, debug=True)
