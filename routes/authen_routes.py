from flask import Blueprint, request, jsonify, redirect, url_for, session , make_response
from pymongo import MongoClient
import bcrypt
from config import get_db

authen_bp = Blueprint('authen', __name__)

@authen_bp.route('/register', methods=['POST'])
def register():
    try:
        username = request.form['username']
        password = request.form['password']
        school_name = request.form['school_name']

        db = get_db()
        users_collection = db['users']
        schools_collection = db['school']

        # Kiểm tra xem người dùng đã tồn tại trong cơ sở dữ liệu chưa
        if users_collection.find_one({'username': username}):
            return jsonify({'error': 'Username already exists'}), 400

        # Kiểm tra xem trường đã tồn tại trong cơ sở dữ liệu chưa
        if schools_collection.find_one({'school_name': school_name}):
            return jsonify({'error': 'School has already been registered'}), 400

        # Băm mật khẩu trước khi lưu vào cơ sở dữ liệu
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Thêm người dùng mới vào cơ sở dữ liệu
        users_collection.insert_one({'username': username, 'password': hashed_password, 'school_name': school_name})

        # Thêm trường vào cơ sở dữ liệu
        schools_collection.insert_one({'school_name': school_name})

        return jsonify({'message': 'Registration successful'}), 200
    except Exception as e:
        return jsonify({'error': f'Failed to register user: {str(e)}'}), 500
@authen_bp.route('/login', methods=['POST'])
def login():
    try:
        username = request.form['username']
        password = request.form['password']

        db = get_db()
        users_collection = db['users']

        # Tìm người dùng trong cơ sở dữ liệu
        user = users_collection.find_one({'username': username})

        if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
            # Đăng nhập thành công, trả về thông tin người dùng bao gồm school_name
            login_data = {
                'username': user['username'],
                'school_name': user['school_name']
            }

            # Lưu thông tin đăng nhập vào session
            session['username'] = user['username']
            session['school_name'] = user['school_name']
            
            return jsonify({'data': login_data, 'message': 'Login successful'}), 200
        else:
            return jsonify({'error': 'Invalid username or password'}), 401
    except Exception as e:
        return jsonify({'error': f'Failed to login: {str(e)}'}), 500


@authen_bp.route('/logout', methods=['GET'])
def logout():
    # Xóa thông tin đăng nhập khỏi session
    session.pop('username', None)
    
    # Tạo một response trống
    response = make_response(redirect(url_for('home')))

    # Thiết lập cookie 'session' với giá trị rỗng và ngày hết hạn trong quá khứ
    response.set_cookie('session', '', expires=0)

    return response
