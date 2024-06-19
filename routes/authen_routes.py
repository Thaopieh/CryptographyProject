from flask import Blueprint, request, jsonify, redirect, url_for, session, make_response
from pymongo import MongoClient
import bcrypt
import jwt
from config import get_db
import os
current_dir = os.path.dirname(__file__)

# Đường dẫn tệp AES.bin từ thư mục test
secret_key_path = os.path.join(current_dir, '..', 'test', 'AES.bin')

def read_secret_key(filepath):
    with open(filepath, 'rb') as file:
        secret_key = file.read()
    return secret_key

# Đọc khóa bí mật từ tệp
secret_key = read_secret_key(secret_key_path)
authen_bp = Blueprint('authen', __name__)

# Function to encode JWT token
def encode_token(payload):
    return jwt.encode(payload, secret_key, algorithm='HS256')


@authen_bp.route('/register', methods=['POST'])
def register():
    try:
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        school_name = request.form.get('school_name')  # Lấy giá trị school_name hoặc None nếu không có

        # Kiểm tra role có hợp lệ hay không
        if role not in ['issuer', 'verifier']:
            return jsonify({'error': 'Invalid role'}), 400

        db = get_db()
        users_collection = db['users']
        schools_collection = db['school']

        # Kiểm tra xem người dùng đã tồn tại trong cơ sở dữ liệu chưa
        if users_collection.find_one({'username': username}):
            return jsonify({'error': 'Username already exists'}), 400

        # Kiểm tra xem trường đã tồn tại trong cơ sở dữ liệu chưa (nếu có cung cấp school_name)
        if school_name and schools_collection.find_one({'school_name': school_name}):
            return jsonify({'error': 'School has already been registered'}), 400

        # Băm mật khẩu trước khi lưu vào cơ sở dữ liệu
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Tạo đối tượng người dùng
        user_data = {
            'username': username,
            'password': hashed_password,
            'role': role
        }

        if school_name:
            user_data['school_name'] = school_name

        # Thêm người dùng mới vào cơ sở dữ liệu
        users_collection.insert_one(user_data)

        # Thêm trường vào cơ sở dữ liệu nếu có cung cấp school_name
        if school_name:
            schools_collection.insert_one({'school_name': school_name})

        return jsonify({'message': 'Registration successful'}), 200
    except Exception as e:
        return jsonify({'error': f'Failed to register user: {str(e)}'}), 500
def encode_token(data):
    token = jwt.encode(data, secret_key, algorithm="HS256")
    return token  # Đảm bảo token là một chuỗi (string)
@authen_bp.route('/login', methods=['POST'])
def login():
    try:
        username = request.form['username']
        password = request.form['password']

        db = get_db()
        users_collection = db['users']

        # Find user in the database
        user = users_collection.find_one({'username': username})

        if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
            # Successful login, return user info including school_name if exists
            login_data = {
            }

            if user['role'] == 'verifier':
                # Save login info in session
                session['username'] = user['username']
                session['role'] = user['role']

                # Generate JWT token
                token = encode_token({
                    'username': user['username'],
                    'role': user['role'],
                })
                print("token:", token)
                print(login_data)
                # Return successful response with token
                # Set token in cookie
                response = make_response(jsonify({'data': login_data, 'message': 'Login successful'}), 200)
                response.set_cookie('token', token)

                return response

            elif user['role'] == 'issuer':
                # Save login info in session
                login_data['school_name'] = user['school_name']
                session['username'] = user['username']
                session['role'] = user['role']

                # Generate JWT token
                token = encode_token({
                    'username': user['username'],
                    'role': user['role'],
                    'school_name': user['school_name']
                })
                print("token:", token)

                # Return successful response with token
                # Set token in cookie
                response = make_response(jsonify({'data': login_data,'message': 'Login successful'}), 200)
                response.set_cookie('token', token)

                return response
            else:
                return jsonify({'error': 'Invalid username or password'}), 401
        else:
            return jsonify({'error': 'Invalid username or password'}), 401
    except Exception as e:
        return jsonify({'error': f'Failed to login: {str(e)}'}), 500

@authen_bp.route('/logout', methods=['GET'])
def logout():
     
    

    # Xóa thông tin đăng nhập khỏi session
    session.pop('username', None)
    session.pop('role', None)
    session.pop('school_name', None)

    # Tạo một response trống
    response = make_response(redirect(url_for('home')))

    # Thiết lập cookie 'session' với giá trị rỗng và ngày hết hạn trong quá khứ
    response.set_cookie('session', '', expires=0)
    response.set_cookie('token', '', expires=0)  # Xóa cookie 'token'
    response.set_cookie('RASession', '', expires=0)  # Xóa cookie 'token'
    return response
