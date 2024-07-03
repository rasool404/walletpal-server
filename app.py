from flask import request, jsonify, session
from config import app, db
from models import User

@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()

        if not data:
            return jsonify(message="Invalid input"), 400

        name = data.get('name')
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        if not name or not username or not email or not password:
            return jsonify(message="Missing required fields"), 400

        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            return jsonify(message="User already exists"), 409


        user = User(name=name, username=username, email=email, password=password)
        
        db.session.add(user)
        db.session.commit()

        return jsonify(message="User registered successfully"), 201
    
    except Exception as e:
        print(f"Error registering user: {e}")
        return jsonify(message="Internal server error"), 500

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email, password=password).first()

    if user:
        session['user'] = user.id  # Store user ID in session
        return jsonify(message="Login successful", user_id=user.id, name=user.name), 200
    else:
        return jsonify(message="Invalid credentials"), 401

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user', None)
    return jsonify(message="Logged out successfully"), 200

@app.route('/update', methods=['PUT'])
def update_user():
    if 'user' not in session:
        return jsonify(message="User not logged in"), 401
    
    user_id = session['user']
    user = User.query.get(user_id)
    if not user:
        return jsonify(message="User not found"), 404

    data = request.get_json()
    user.name = data.get('name', user.name)
    user.username = data.get('username', user.username)
    user.email = data.get('email', user.email)
    
    if data.get('username') and data.get('username') != user.username:
        if User.query.filter_by(username=data['username']).first():
            return jsonify(message="Username already exists"), 409

    if data.get('email') and data.get('email') != user.email:
        if User.query.filter_by(email=data['email']).first():
            return jsonify(message="Email already exists"), 409
    
    db.session.commit()

    return jsonify(message="User updated successfully", name=user.name, username=user.username, email=user.email), 200

@app.route('/user', methods=['GET'])
def get_user_info():
    if 'user' not in session:
        return jsonify(message="User not logged in"), 401

    user_id = session['user']
    user = User.query.get(user_id)
    if not user:
        return jsonify(message="User not found"), 404

    return jsonify(
        id=user.id,
        name=user.name,
        username=user.username,
        email=user.email
    ), 200

with app.app_context():
  db.create_all()

if __name__ == '__main__':
    app.run(debug=True)