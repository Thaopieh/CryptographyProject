from flask import Blueprint, request, jsonify
import logging
from config import get_db

student_bp = Blueprint('student', __name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@student_bp.route('/create_student', methods=['POST'])
def create_student():
    try:
        student_name = request.form['student_name']
        student_id = request.form['student_id']
        student_school = request.form['student_school']

        db = get_db()
        students = db.students

        students.insert_one({
            'student_name': student_name,
            'student_id': student_id,
            'student_school': student_school

        })

        return jsonify({'message': 'Student created successfully'}), 200
    except Exception as e:
        logger.error(f"Error creating student: {e}")
        return jsonify({'error': f'Failed to create student: {str(e)}'}), 500

@student_bp.route('/get_student', methods=['GET'])
def get_student():
    try:
        student_id = request.args.get('student_id')
        db = get_db()
        students = db.students
        student = students.find_one({'student_id': student_id})
        if not student:
            return jsonify({'error': 'Student not found'}), 404

        return jsonify({
            'student_name': student['student_name'],
            'student_id': student['student_id'],
            'student_school': student['student_school']
        }), 200
    except Exception as e:
        logger.error(f"Error retrieving student: {e}")
        return jsonify({'error': f'Failed to retrieve student: {str(e)}'}), 500
