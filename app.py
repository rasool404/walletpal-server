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
        session['user'] = user.id  
        return jsonify(message="Login successful", user_id=user.id, name=user.name), 200
    else:
        return jsonify(message="Invalid credentials"), 401
    
    
# =============== Logout ===============
@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user', None)
    return jsonify(message="Logged out successfully"), 200


# =============== Update ===============
@app.route('/update', methods=['PUT'])
def update_user():
    if 'user' not in session:
        return jsonify(message="User not logged in"), 401
    
    user_id = session['user']
    user = User.query.get(user_id)
    if not user:
        return jsonify(message="User not found"), 404

    data = request.get_json()

    # Check if the new username is provided and not empty, otherwise keep the original
    new_username = data.get('username')
    if new_username is None or new_username.strip() == "":
        new_username = user.username
    else:
        # Check if the new username already exists in the database
        if new_username != user.username and User.query.filter_by(username=new_username).first():
            return jsonify(message="Username already exists"), 409

    # Check if the new email is provided and not empty, otherwise keep the original
    new_email = data.get('email')
    if new_email is None or new_email.strip() == "":
        new_email = user.email
    else:
        # Check if the new email already exists in the database
        if new_email != user.email and User.query.filter_by(email=new_email).first():
            return jsonify(message="Email already exists"), 409

    # Check if the new password is provided and not empty, otherwise keep the original
    new_password = data.get('password')
    if new_password is None or new_password.strip() == "":
        new_password = user.password  # Assuming passwords are stored as plain text (not recommended)
    else:
        # Ideally, you'd hash the new password before storing it
        new_password = new_password  # Here, you might want to hash the password instead

    # Check if the new name is provided and not empty, otherwise keep the original
    new_name = data.get('name')
    if new_name is None or new_name.strip() == "":
        new_name = user.name

    # Update the user information
    user.name = new_name
    user.username = new_username
    user.email = new_email
    user.password = new_password

    try:
        db.session.commit()
        return jsonify(
            message="User updated successfully",
            name=user.name,
            username=user.username,
            email=user.email
        ), 200
    except Exception as e:
        print(f"Error updating user: {e}")
        db.session.rollback()
        return jsonify(message="Internal server error"), 500



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

@app.route('/users', methods=['GET'])
def get_all_users():
    try:
        users = User.query.all()
        
        users_list = [
            {
                'id': user.id,
                'name': user.name,
                'username': user.username,
                'email': user.email
            } for user in users
        ]

        return jsonify(users=users_list), 200

    except Exception as e:
        print(f"Error fetching users: {e}")
        return jsonify(message="Internal server error"), 500

with app.app_context():
  db.create_all()

if __name__ == '__main__':
    app.run(debug=True)