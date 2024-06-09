from flask import Blueprint, request, send_file, jsonify
from pdfrw import PdfReader, PdfWriter, PageMerge, PdfString
import io
from qrcode import QRCode, constants
import qrcode.image.pil
from PIL import ImageFont 
from config import get_db
import logging
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import json
from datetime import datetime
from bson.objectid import ObjectId

import tempfile
from io import BytesIO

import os
import base64
import requests
import string
import random

import subprocess
import time
import os


current_dir = os.path.dirname(os.path.abspath(__file__))
pathOpenssl = os.path.join(current_dir, "..", "bin", "openssl ")
configOpenssl = os.path.join(current_dir, "..", "ssl", "openssl.cnf")



def create_test_directory():
    if not os.path.exists("test"):
        os.makedirs("test")


def detachPubKeyFromCert(cert_file, public_key_file):
    command = f"{pathOpenssl}x509 -in {cert_file} -pubkey -noout -out {public_key_file}"
    subprocess.run(command, shell=True, check=True)


def signData(privateKey, dataFile, signatureFile):
    command = pathOpenssl + "dgst -sha256 -sign " + privateKey + " -out " + signatureFile + " " + dataFile
    subprocess.run(command, shell=True)


def verifySignature(public_key_path, qualificate_path, signature_path):
    try:
        # Combine the certificate and the signature into a single file for verification
        command = (
            f"{pathOpenssl}dgst -sha256 -verify {public_key_path} "
            f"-signature {signature_path} {qualificate_path}"
        )
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return 'Verified OK' in result.stdout
    except subprocess.CalledProcessError as e:
        logger.error(f"OpenSSL error: {e}")
        return False




def generate_random_id(length=8):
    """
    Tạo một ID ngẫu nhiên gồm 8 chữ số.
    """
    characters = string.digits
    random_id = ''.join(random.choice(characters) for _ in range(length))
    return random_id

import tempfile
from pdfrw import PdfReader, PdfWriter,  PdfDict, PdfName



def embed_signature_in_pdf(pdf_data, signature_base64):
    try:
        # Đọc PDF từ dữ liệu nhị phân
        pdf_reader = PdfReader(fdata=pdf_data.getvalue())
        
        # Thêm chữ ký vào metadata
        if not pdf_reader.Info:
            pdf_reader.Info = PdfDict()
        pdf_reader.Info.Signature = PdfString(signature_base64)
        
        # Tạo tệp tạm thời để lưu PDF đã chỉnh sửa
        temp_pdf_file = io.BytesIO()
        pdf_writer = PdfWriter(temp_pdf_file)
        pdf_writer.addpages(pdf_reader.pages)
        pdf_writer.trailer = pdf_reader.trailer
        
        # Trả về dữ liệu nhị phân của PDF
        pdf_writer.write()
        temp_pdf_file.seek(0)
        return temp_pdf_file
    except Exception as e:
        logger.error(f"Error embedding signature in PDF: {e}")
        return None



qualificate_bp = Blueprint('qualificate', __name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Function to create QR code

def create_qr_code(data):
    try:
        # Tạo một mã QR với PIL để hỗ trợ tiếng Việt
        qr = QRCode(
            version=1,
            error_correction=constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data.encode('utf-8'))
        qr.make(fit=True)
        
        # Tạo ảnh từ mã QR
        img = qr.make_image(fill='black', back_color='white')

        return img
    except Exception as e:
        logger.error(f"Error creating QR code: {e}")
        return None
    
    
def embed_qr_in_existing_pdf(pdf_stream, qr_img):
    try:
        # Convert PIL image to file-like object
        qr_img_byte_arr = io.BytesIO()
        qr_img.save(qr_img_byte_arr, format='PNG')
        qr_img_byte_arr.seek(0)

        # Create a PDF with the QR code
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=A4)
        
        # QR code dimensions
        qr_size = 100  # Size of the QR code in points
        
        # Draw QR code on the canvas in the bottom-left corner
        qr_img_reader = ImageReader(qr_img_byte_arr)
        can.drawImage(qr_img_reader, 10, 10, width=qr_size, height=qr_size)
        can.save()
        
        # Move to the beginning of the StringIO buffer
        packet.seek(0)
        qr_pdf = PdfReader(packet)
        qr_page = qr_pdf.pages[0]

        # Read the existing PDF
        existing_pdf = PdfReader(pdf_stream)
        output = PdfWriter()

        # Merge the QR code with the first page
        if len(existing_pdf.pages) > 0:
            first_page = existing_pdf.pages[0]
            PageMerge(first_page).add(qr_page, prepend=False).render()

        # Add the merged first page and the rest of the pages
        output.addpage(first_page)
        for page in existing_pdf.pages[1:]:
            output.addpage(page)

        # Output the final PDF
        output_stream = io.BytesIO()
        output.write(output_stream)
        output_stream.seek(0)

        return output_stream
    except Exception as e:
        logger.error(f"Error embedding QR code in PDF: {e}")
        return None

@qualificate_bp.route('/issue_qualificate', methods=['POST'])
def issue_qualificate():
    try:
        school_name = request.form['school_name']
        student_id = request.form['student_id']
        student_name = request.form['student_name']
        pdf_file = request.files['qualificate'].read()
        private_key_file = request.files['private_key']

        school_response = requests.get(
            'http://localhost:5000/school/get_school_info',
            params={'school_name': school_name}
        )
        if school_response.status_code == 404:
            return jsonify({'error': 'School not found'}), 404

        school_info = school_response.json().get('school_info')
        auth_name = school_info.get('auth_name')
        auth_email = school_info.get('auth_email')

        private_key_path = f"temp/{school_name}_private.key"
        with open(private_key_path, 'wb') as f:
            f.write(private_key_file.read())

        student_response = requests.get(
            'http://localhost:5000/student/get_student',
            params={'student_id': student_id}
        )
        if student_response.status_code == 404:
            student_response = requests.post(
                'http://localhost:5000/student/create_student',
                data={'student_name': student_name, 'student_id': student_id, 'student_school': school_name}
            )
            if student_response.status_code != 200:
                return jsonify({'error': 'Failed to create student'}), student_response.status_code

        signature_path = os.path.join('test', 'signature')

        qualificate_id = generate_random_id()
        qr_data = json.dumps({
            "school_name": school_name,
            "auth_name": auth_name,
            "auth_email": auth_email,
            "student_id": student_id,
            "qualificate_id": qualificate_id,
            "student_name": student_name,
            "issued_date": str(datetime.now())
        }, ensure_ascii=False)

        qr_img = create_qr_code(qr_data)
        if qr_img is None:
            return jsonify({'error': 'Failed to create QR code'}), 500

        pdf_stream = io.BytesIO(pdf_file)
        pdf_data = embed_qr_in_existing_pdf(pdf_stream, qr_img)
        if pdf_data is None:
            return jsonify({'error': 'Failed to create PDF with QR code'}), 500

        temp_pdf_path = 'temp.pdf'
        with open(temp_pdf_path, 'wb') as f:
            f.write(pdf_data.getvalue())

        signData(private_key_path, temp_pdf_path, signature_path)

        with open(signature_path, 'rb') as sig_file:
            signature = sig_file.read()

        db = get_db()
        qualification = db.qualification
        qualification.insert_one({
            'qualificate_id': qualificate_id,
            'student_id': student_id,
            'qualificate': pdf_data.getvalue(),
            'signature': signature
        })

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
            zip_file.writestr(f"{school_name}_certificate.pdf", pdf_data.getvalue())
            zip_file.writestr(f"{school_name}_signature.sig", signature)

        zip_buffer.seek(0)

        os.remove(temp_pdf_path)
        os.remove(signature_path)
        os.remove(private_key_path)

        return send_file(
            zip_buffer,
            as_attachment=True,
            download_name=f"{school_name}_certificate_with_signature.zip",
            mimetype='application/zip'
        )
    except Exception as e:
        logger.error(f"Failed to issue certificate: {e}")
        return jsonify({'error': f'Failed to issue certificate: {str(e)}'}), 500

import zipfile

@qualificate_bp.route('/get_qualificate', methods=['GET'])
def get_qualificate_file():
    try:
        db = get_db()
        collection = db.qualification
        student = db.students
        student_id = request.args.get('student_id')
        qualificate_id = request.args.get('qualificate_id')    
        school_name = request.args.get('school_name')
        
        # Check if all parameters are provided
        if not student_id or not qualificate_id or not school_name:
            return jsonify({'error': 'Missing required parameters'}), 400
        
        logger.info(f"Retrieving qualificate for student_id: {student_id}, qualificate_id: {qualificate_id}, school_name: {school_name}")
        
        query = {'student_id': student_id, 'student_school': school_name}
        item = student.find_one(query)
        
        if not item:
            logger.error(f"Student not found: {student_id} in school: {school_name}")
            return jsonify({'error': 'Student not found'}), 404
        
        # Find the qualificate based on student_id and qualificate_id
        query = {'student_id': student_id, 'qualificate_id': qualificate_id}
        items = collection.find_one(query)
        
        if not items or 'qualificate' not in items:
            logger.error(f"Qualificate not found: {qualificate_id} for student: {student_id}")
            return jsonify({'error': 'Qualificate not found'}), 404
        
        pdf_data = items['qualificate']

        # Retrieve the school's certificate
        school_response = requests.get(
            'http://localhost:5000/school/get_school_certificate',
            params={'school_name': school_name}
        )
        
        if school_response.status_code != 200:
            logger.error(f"Failed to retrieve school certificate for: {school_name}, status_code: {school_response.status_code}")
            return jsonify({'error': 'Failed to retrieve school certificate'}), school_response.status_code
        
        certificate_data = school_response.content

        # Create temporary files for qualificate and certificate
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as qualificate_file:
            qualificate_file.write(pdf_data)
            qualificate_file_path = qualificate_file.name
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.crt') as certificate_file:
            certificate_file.write(certificate_data)
            certificate_file_path = certificate_file.name
        
        # Create a ZIP file containing both files
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
            zip_file.write(qualificate_file_path, arcname=f'{student_id}_qualificate.pdf')
            zip_file.write(certificate_file_path, arcname=f'{school_name}.crt')
        
        zip_buffer.seek(0)

        # Clean up temporary files
        os.remove(qualificate_file_path)
        os.remove(certificate_file_path)
        
        logger.info(f"Successfully retrieved qualificate and created ZIP for student_id: {student_id}, qualificate_id: {qualificate_id}, school_name: {school_name}")
        
        # Return the ZIP file
        return send_file(
            zip_buffer,
            as_attachment=True,
            download_name=f'{student_id}_qualificate_and_certificate.zip',
            mimetype='application/zip'
        ), 200
        
    except Exception as e:
        logger.error(f"Failed to retrieve qualificate: {e}")
        return jsonify({'error': f'Failed to retrieve qualificate: {str(e)}'}), 500


@qualificate_bp.route('/get_signature', methods=['GET'])
def get_signature_file():
    try:
        db = get_db()
        collection = db.qualification
        qualificate_id = request.args.get('qualificate_id')
        
        # Tìm chứng chỉ dựa trên qualificate_id
        query = {'qualificate_id': qualificate_id}
        qualificate = collection.find_one(query)
                
        if qualificate and 'signature' in qualificate:
            # Lấy dữ liệu của tệp chữ ký
            signature_data = qualificate['signature']
            
            # Trả về tệp chữ ký trực tiếp từ dữ liệu trong cơ sở dữ liệu
            return send_file(io.BytesIO(signature_data), as_attachment=True, download_name='signature.bin'), 200
        else:
            return jsonify({'error': 'Signature not found'}), 404
    except Exception as e:
        logger.error(f"Failed to retrieve signature: {e}")
        return jsonify({'error': f'Failed to retrieve signature: {str(e)}'}), 500





@qualificate_bp.route('/verify_qualificate', methods=['POST'])
def verify_qualificate():
    try:
        qualificate_id = request.form['qualificate_id']
        qualificate = request.files['qualificate']
        public_key = request.files['public_key']
        
        temp_pub_key_file = f"temp/{qualificate_id}_public.key"
        temp_qualificate_file = f"temp/{qualificate_id}_qualificate.pdf"
        temp_signature_file = f"temp/{qualificate_id}_signature.sig"

        # Save public key to a temporary file
        with open(temp_pub_key_file, 'wb') as f:
            f.write(public_key.read())
        
        # Save qualificate to a temporary file
        with open(temp_qualificate_file, 'wb') as f:
            f.write(qualificate.read())
        
        # Load signature from database
        signature_response = requests.get(
            'http://localhost:5000/qualificate/get_signature', 
            params={'qualificate_id': qualificate_id}
        )
        
        if signature_response.status_code != 200:
            return jsonify({'error': 'Failed to retrieve signature'}), signature_response.status_code
        
        with open(temp_signature_file, 'wb') as f:
            f.write(signature_response.content)
        
        # Verify the signature
        is_valid_pdf = verifySignature(temp_pub_key_file, temp_qualificate_file, temp_signature_file)
        
        # Clean up temporary files
        os.remove(temp_pub_key_file)
        os.remove(temp_qualificate_file)
        os.remove(temp_signature_file)
        
        return jsonify({'valid_pdf': is_valid_pdf})
    except Exception as e:
        logger.error(f"Error verifying certificate: {e}")
        return jsonify({'error': 'Failed to verify certificate'}), 500



@qualificate_bp.route('/certificate', methods=['GET'])
def get_qualificate():
    try:
        student_name = request.args.get('student_name')
        db = get_db()
        certificates = db.certificates
        certificate = certificates.find_one({'student_name': student_name})
        if certificate:
            pdf_data = io.BytesIO(certificate['pdf'])
            pdf_data.seek(0)
            return send_file(pdf_data, as_attachment=True, download_name='certificate.pdf')
        else:
            return jsonify({'error': 'Certificate not found'}), 404
    except Exception as e:
        logger.error(f"Error getting certificate: {e}")
        return jsonify({'error': 'Failed to get certificate'}), 500

# Ensure UuidRepresentation is defined
from pymongo import common
if not hasattr(common, 'UuidRepresentation'):
    class UuidRepresentation:
        STANDARD = 'standard'
        PYTHON_LEGACY = 'pythonLegacy'
        JAVA_LEGACY = 'javaLegacy'
        C_SHARP_LEGACY = 'csharpLegacy'
        UNSPECIFIED = 'unspecified'
    common.UuidRepresentation = UuidRepresentation
