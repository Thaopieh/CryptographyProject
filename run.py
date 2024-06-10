from flask import Flask, render_template
from routes.qualificate_routes import qualificate_bp
from  routes.school_routes import school_bp
from routes.student_routes import student_bp
from  routes.authen_routes import authen_bp
from flask_cors import CORS
app = Flask(__name__)
CORS(app)
# Register blueprints
app.register_blueprint(qualificate_bp, url_prefix='/qualificate')
app.register_blueprint(school_bp, url_prefix='/school')
app.register_blueprint(authen_bp, url_prefix='/authen')
app.register_blueprint(student_bp, url_prefix='/student')
app.secret_key = "demommhnhom16"
@app.route('/home')
def home():
    return render_template('index.html')
@app.route('/signing')
def signing():
    return render_template('signing.html')
@app.route('/getqua')
def getqua():
    return render_template('get.html')
@app.route('/verify')
def verify():
    return render_template('verify.html')

@app.route('/School')
def School():
    return render_template('School.html')
@app.route('/CreateRequestCertificate')
def CreateRequestCertificate():
    return render_template('CreateRequestCertificate.html')
@app.route('/createcert')
def createcert():
    return render_template('CreateCertificate.html')
@app.route('/Createkey')
def Createkey():
    return render_template('CreateKey.html')
@app.route('/issue')
def issue():
    return render_template('IssueQualification.html')
@app.route('/company')
def company():
    return render_template('Company.html')
@app.route('/CreateSchool')
def CreateSchool():
    return render_template('CreateSchool.html')
@app.route('/GetSchool')
def GetSchool():
    return render_template('GetSchool.html')
@app.route('/account')
def account():
    return render_template('account.html')
@app.route('/login')
def login():
    return render_template('login.html')
@app.route('/register')
def register():
    return render_template('register.html')
if __name__ == '__main__':
    app.run(debug=True)