from functools import wraps
from flask import request, jsonify, session,redirect, url_for
from config import get_db
import jwt
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

def decode_token(token):
    try:
        decoded = jwt.decode(token, secret_key, algorithms=["HS256"])
        print("decode",decoded)
        return decoded
    except jwt.ExpiredSignatureError:
        return {'error': 'Token has expired'}
    except jwt.InvalidTokenError:
        return {'error': 'Invalid token'}
def get_username_from_token():
    token = request.cookies.get('token')
    print("Token from cookie:", token)
    if token:
        try:
            decoded_token = decode_token(token)
            if 'error' in decoded_token:
                return None
            return decoded_token.get('username')
        except jwt.InvalidTokenError:
            return None
    return None
def load_user_from_db(username):
    db = get_db()
    users_collection = db['users']
    return users_collection.find_one({'username': username})
def before_request():
   

        username = get_username_from_token()
        user = load_user_from_db(username)
        if user:
            request.user = {
                'username': user['username'],
                'role': user['role']
            }
            if 'school_name' in user:
                request.user['school_name'] = user['school_name']
            print(f"Authenticated user: {request.user}")
        else:
            request.user = None
            print("User not found in database.")

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'role' not in session:
            return jsonify({'error': 'Unauthorized'}), 401  # Return unauthorized error
        return f(*args, **kwargs)
    return decorated_function
def already_logged_in(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' in session:
            if session['role'] == 'issuer':
                return redirect(url_for('School'))  # Redirect to School for issuer
            elif session['role'] == 'verifier':
                return redirect(url_for('use'))  # Redirect to use for verifier
            else:
                return redirect(url_for('home'))  # Default redirect if role is undefined
        return f(*args, **kwargs)
    return decorated_function
def verifier_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = request.user
        if not user or user['role'] not in ['verifier', 'issuer']:
            return jsonify({'error': 'Access denied'}), 403  # Return access denied error
        return f(*args, **kwargs)
    return decorated_function
def comfirm_issuer(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = request.user
        if not user or user['role'] not in ['issuer']:
            return jsonify({'error': 'Access denied'}), 403  # Return access denied error
        return f(*args, **kwargs)
    return decorated_function
def abac_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = request.user
        if not user:
            print("Unauthorized: No user in request.")
            return jsonify({'error': 'Unauthorized'}), 401

        resource = kwargs
        action = request.method
        
        print(f"User: {user}")
        print(f"Resource: {resource}")
        print(f"Action: {action}")
        
        if not evaluate_policy(user, resource, action):
            print("Access denied: Policy evaluation failed.")
            return jsonify({'error': 'Access denied'}), 403
        
        return f(*args, **kwargs)
    return decorated_function

def evaluate_policy(user, resource, action):
    role = user['role']
    endpoint = request.endpoint
    
    policies = {
        'issuer': {
            'POST': ['qualificate.issue_qualificate', '', 'school.require_cert', 'school.generate_key', 'school.get_certificate','qualificate.verify_qualificate'],
            'GET' : ['qualificate.get_qualificate_file','school.get_school_certificate'],
        },
        'verifier': {
            'GET': ['qualificate.get_qualificate_file','school.get_school_certificate'],
            'POST': ['qualificate.verify_qualificate']
        }
    }
    
    print(f"Evaluating policy for role: {role}, action: {action}, endpoint: {endpoint}")
    
    if role in policies and action in policies[role] and endpoint in policies[role][action]:
        print("Policy evaluation successful.")
        return True

    print("Policy evaluation failed.")
    return False
