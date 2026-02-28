import os
from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import socket

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

@app.route('/')
def index():
    return "GrassBuddy Server is Running! Touch Grass."

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
        
        return jsonify({
            'message': 'Grass touched successfully!',
            'filename': filename,
            'url': f'/images/{filename}'
        }), 201
        
    return jsonify({'error': 'File type not allowed'}), 400

@app.route('/feed', methods=['GET'])
def get_feed():
    # List all files in the upload directory
    # In a real app, you'd store metadata in a database
    files = []
    if os.path.exists(UPLOAD_FOLDER):
        for filename in os.listdir(UPLOAD_FOLDER):
            if allowed_file(filename):
                # Sort by modification time (newest first)
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                files.append({
                    'filename': filename,
                    'url': f'/images/{filename}',
                    'timestamp': os.path.getmtime(filepath)
                })
    
    # Sort by timestamp descending
    files.sort(key=lambda x: x['timestamp'], reverse=True)
    
    return jsonify({'feed': files}), 200

@app.route('/images/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Mock database of users and their friends
users = {
    '1': {'name': 'Nick', 'friends': ['2', '3']},
    '2': {'name': 'Sarah', 'friends': ['1']},
    '3': {'name': 'Mike', 'friends': ['1']}
}

@app.route('/users/<user_id>/friends', methods=['GET'])
def get_friends(user_id):
    user = users.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    friends_list = []
    for friend_id in user['friends']:
        friend = users.get(friend_id)
        if friend:
            friends_list.append({'id': friend_id, 'name': friend['name']})
            
    return jsonify({'friends': friends_list}), 200

@app.route('/nudge/<user_id>', methods=['POST', 'GET'])
def nudge_person(user_id):
    target_user = users.get(user_id)
    
    if not target_user:
        return jsonify({'error': 'User not found'}), 404

    # In a real app, this would send a push notification or update a database
    print(f"NUDGE SENT: Someone nudged {target_user['name']} (ID: {user_id}) to go touch grass!")
    
    return jsonify({
        'message': f'You successfully nudged {target_user["name"]}!',
        'target_id': user_id,
        'target_name': target_user['name'],
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

if __name__ == '__main__':
    # host='0.0.0.0' allows other devices on the network to access it
    ip = get_ip_address()
    print(f"\n--- GrassBuddy Server ---")
    print(f"Listening on: http://{ip}:{PORT}")
    print(f"Local access: http://127.0.0.1:{PORT}")
    print(f"-------------------------\n")
    
    app.run(host='0.0.0.0', port=PORT, debug=True)
