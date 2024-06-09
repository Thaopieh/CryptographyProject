from flask import Blueprint, request, jsonify, send_file
from pymongo import MongoClient
import logging
from config import get_db
import io
import tempfile
school_bp = Blueprint('school', __name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


import subprocess
import time
import os
import zipfile

current_dir = os.path.dirname(os.path.abspath(__file__))
pathOpenssl = os.path.join(current_dir, "..", "bin", "openssl ")
configOpenssl = os.path.join(current_dir, "..", "ssl", "openssl.cnf")


def create_test_directory():
    if not os.path.exists("test"):
        os.makedirs("test")

def genKey(privateKey):
    command = pathOpenssl + "genpkey -algorithm dilithium3 -out test/" + privateKey + ".key"
    subprocess.run(command, shell=True)


@school_bp.route('/genkey', methods=['POST'])
def generate_key():
    try:
        school_name = request.form['school_name']
        
        # Tạo tên tệp khóa riêng tư và công khai dựa trên tên trường
        private_key_file = f"{school_name}_private"
        public_key_file = f"{school_name}_public"

        # Tạo khóa riêng tư
        genKey(private_key_file)
        
        # Đường dẫn tệp khóa riêng tư và công khai
        private_key_path = f"test/{private_key_file}.key"
        public_key_path = f"test/{public_key_file}.key"

        # Lệnh để tạo khóa công khai từ khóa riêng tư
        command = f"{pathOpenssl}pkey -in {private_key_path} -pubout -out {public_key_path}"
        subprocess.run(command, shell=True, check=True)

        # Kiểm tra nếu tệp khóa riêng tư và công khai đã được tạo thành công
        if not os.path.exists(private_key_path) or not os.path.exists(public_key_path):
            return jsonify({'error': 'Failed to generate private or public key'}), 500

        # Đọc nội dung tệp khóa riêng tư và công khai
        with open(private_key_path, 'rb') as f:
            private_key_data = f.read()

        with open(public_key_path, 'rb') as f:
            public_key_data = f.read()

        # Tạo tệp ZIP chứa cả hai tệp
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
            zip_file.writestr(f"{school_name}_private.key", private_key_data)
            zip_file.writestr(f"{school_name}_public.key", public_key_data)
        
        # Đặt con trỏ của zip_buffer về đầu
        zip_buffer.seek(0)

        # Xóa các tệp khóa riêng tư và công khai
        os.remove(private_key_path)
        os.remove(public_key_path)

        # Trả về tệp ZIP
        return send_file(
            zip_buffer,
            as_attachment=True,
            download_name=f"{school_name}_keys.zip",
            mimetype='application/zip'
        ), 200

    except Exception as e:
        logger.error(f"Error generating private and public key: {e}")
        return jsonify({'error': f'Failed to generate private and public key: {str(e)}'}), 500

    
@school_bp.route('/require_cert', methods=['POST'])
def require_cert():
    try:
        # Lấy thông tin từ form
        school_name = request.form['school_name']
        auth_name = request.form['auth_name']
        auth_email = request.form['auth_email']
        country = request.form['C']
        state = request.form['ST']
        locality = request.form['L']
        org_unit = request.form['OU']
        
        private_key_file = request.files['private_key']

        private_key_path = f"temp/{school_name}_private.key"
        
        with open(private_key_path, 'wb') as f:
            f.write(private_key_file.read())

        # Tạo các trường thông tin từ dữ liệu form
        subj_fields = {
            "C": country,
            "ST": state,
            "L": locality,
            "OU": org_unit,
            "CN": school_name,
            "emailAddress": auth_email
        }

        # Tạo CSR

        csr_path = f"temp/{school_name}.csr"
        if getCert(private_key_path, csr_path, subj_fields, csr_only=True):
            # Đọc dữ liệu CSR
            with open(csr_path, 'rb') as f:
                csr_data = f.read()

            # Xóa tệp tạm
            os.remove(private_key_path)
            os.remove(csr_path)

            db = get_db()
            certificate_collection = db.certificate

            # Thêm CSR vào cơ sở dữ liệu với trạng thái 0 (chưa được ký)
            certificate_data = {
                'school_name': school_name,
                'auth_name': auth_name,
                'auth_email': auth_email,
                'csr': csr_data,
                'status': 0  # Trạng thái ban đầu là 0
            }
            certificate_collection.insert_one(certificate_data)

            # Trả về CSR dưới dạng tệp đính kèm
            return send_file(
                io.BytesIO(csr_data),
                as_attachment=True,
                download_name=f"{school_name}.csr",
                mimetype='application/pkcs10'
            )
        else:
            return jsonify({'error': 'Failed to generate CSR'}), 500
    except Exception as e:
        logger.error(f"Error generating CSR: {e}")
        return jsonify({'error': f'Failed to generate CSR: {str(e)}'}), 500

@school_bp.route('/get_certificate', methods=['POST'])
def get_certificate():
    try:
        school_name = request.form['school_name']
        csr_file = request.files['csr']

        csr_path = f"temp/{school_name}.csr"
        certificate_path = f"temp/{school_name}.crt"
        rootca_path = "test/RootCA.crt"

        with open(csr_path, 'wb') as f:
            f.write(csr_file.read())

        # Ký CSR để tạo chứng chỉ
        command = f"{pathOpenssl}x509 -req -in {csr_path} -out {certificate_path} -CA {rootca_path} -CAkey test/RootCA.key -CAcreateserial -days 365"
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            logger.error(f"OpenSSL error: {result.stderr}")
            return jsonify({'error': 'Failed to get certificate'}), 500

        with open(certificate_path, 'rb') as cert_file:
            cert_data = cert_file.read()

        with open(rootca_path, 'rb') as rootca_file:
            rootca_data = rootca_file.read()

        db = get_db()
        certificate_collection = db.certificate

        # Cập nhật trạng thái chứng chỉ trong cơ sở dữ liệu thành 1 (đã được ký)
        certificate_collection.update_one(
            {'school_name': school_name, 'status': 0},
            {'$set': {'certificate': cert_data, 'status': 1}}
        )

        # Tạo tệp ZIP chứa cả hai chứng chỉ
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
            zip_file.writestr(f"{school_name}.crt", cert_data)
            zip_file.writestr("RootCA.crt", rootca_data)
        
        zip_buffer.seek(0)

        # Xóa các tệp tạm sau khi đã sử dụng xong
        os.remove(csr_path)
        os.remove(certificate_path)

        # Trả về tệp ZIP chứa cả hai chứng chỉ
        return send_file(
            zip_buffer,
            as_attachment=True,
            download_name=f"{school_name}_with_RootCA.zip",
            mimetype='application/zip'
        )
    except Exception as e:
        logger.error(f"Error signing certificate: {e}")
        return jsonify({'error': f'Failed to sign certificate: {str(e)}'}), 500



def detachPubKeyFromCert(cert_data, public_key_path):
    with tempfile.NamedTemporaryFile(delete=False, suffix='.crt') as cert_file:
        cert_file.write(cert_data)
        cert_file_path = cert_file.name

    command = f"{pathOpenssl}x509 -in {cert_file_path} -pubkey -noout -out {public_key_path}"
    subprocess.run(command, shell=True, check=True)

    os.remove(cert_file_path)

@school_bp.route('/create_school', methods=['POST'])
def create_school():
    try:
        school_name = request.form['school_name']
        db = get_db()
        school_collection = db.school
        existing_school = school_collection.find_one({'school_name': school_name})
        if existing_school:

            return jsonify({'error': 'School name already exists'}), 400
        # Lấy chứng chỉ từ cơ sở dữ liệu
        cert_collection = db.certificate
        cert_entry = cert_collection.find_one({'school_name': school_name, 'status': 1})
        
        if not cert_entry:
            return jsonify({'error': 'Certificate not found or not signed'}), 404

        cert_data = cert_entry['certificate']
        


        temp_public_path = f"temp/{school_name}_public.key"  

        detachPubKeyFromCert(cert_data, temp_public_path)
        
        # Đọc khóa công khai từ tệp tạm
        with open(temp_public_path, 'rb') as pub_file:
            public_key_data = pub_file.read()
        
        # Xóa tệp tạm
        os.remove(temp_public_path)
        
        # Thêm trường vào cơ sở dữ liệu
        school_collection = db.school
        school_collection.insert_one({
            'school_name': school_name,
            'auth_name': cert_entry['auth_name'],
            'auth_email': cert_entry['auth_email'],
            'certificate': cert_data,
            'public_key': public_key_data
        })

        return jsonify({'success': 'School created successfully'})
    except Exception as e:
        logger.error(f"Error creating school: {e}")
        return jsonify({'error': f'Error creating school: {str(e)}'}), 500


def getCert(privateKeyPath, certificateName, subj_fields, csr_only=False):
    # Tạo chuỗi thông tin về đối tượng chứng chỉ
    subj_str = "/".join([f"{k}={v}" for k, v in subj_fields.items()])

    # Lệnh tạo CSR
    command = f"{pathOpenssl}req -new -key {privateKeyPath} -out {certificateName} -nodes -subj \"/{subj_str}\" -config {configOpenssl}"
    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to run command: {command}")
        logger.error(f"Error: {e}")
        return False

    if csr_only:
        return True
    
    # Lệnh tạo chứng chỉ từ CSR
    command1 = f"{pathOpenssl}x509 -req -in {certificateName} -out {certificateName}.crt -CA test/RootCA.crt -CAkey test/RootCA.key -CAcreateserial -days 365"
    try:
        subprocess.run(command1, shell=True, check=True)
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to run command: {command1}")
        logger.error(f"Error: {e}")
        return False



import os
@school_bp.route('/get_school_info', methods=['GET'])
def get_school_info():
    try:
        school_name = request.args.get('school_name')
        db = get_db()
        school_collection = db.school
        school = school_collection.find_one({'school_name': school_name})

        if not school:
            return jsonify({'error': 'School not found'}), 404

        # Thông tin cơ bản về trường
        school_info = {
            'school_name': school['school_name'],
            'auth_name': school['auth_name'],
            'auth_email': school['auth_email']
        }

        return jsonify({'school_info': school_info}), 200

    except Exception as e:
        print(f"Error retrieving school info: {e}")
        return jsonify({'error': f'Failed to retrieve school info: {str(e)}'}), 500



@school_bp.route('/get_school_certificate', methods=['GET'])
def get_school_certificate():
    try:
        school_name = request.args.get('school_name')
        db = get_db()
        school_collection = db.school
        school = school_collection.find_one({'school_name': school_name})

        if not school:
            return jsonify({'error': 'School not found'}), 404

        # Lấy dữ liệu chứng chỉ và khóa công khai
        certificate_data = school['certificate']
        public_key_data = school['public_key']

        # Tạo một tệp ZIP để gộp cả chứng chỉ và khóa công khai
        zip_io = io.BytesIO()
        with zipfile.ZipFile(zip_io, 'w') as zip_file:
            zip_file.writestr(f"{school_name}.crt", certificate_data)
            zip_file.writestr(f"{school_name}_public.key", public_key_data)

        zip_io.seek(0)

        # Trả về tệp ZIP dưới dạng tệp đính kèm
        return send_file(
            zip_io,
            as_attachment=True,
            download_name=f"{school_name}_cert_and_pubkey.zip",
            mimetype='application/zip'
        )

    except Exception as e:
        print(f"Error retrieving school certificate: {e}")
        return jsonify({'error': f'Failed to retrieve school certificate: {str(e)}'}), 500
