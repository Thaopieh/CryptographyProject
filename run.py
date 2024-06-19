from flask import Flask, render_template
from routes.qualificate_routes import qualificate_bp
from  routes.school_routes import school_bp
from routes.student_routes import student_bp
from  routes.authen_routes import authen_bp
from middleware.auth import before_request,verifier_required, login_required, already_logged_in,comfirm_issuer

from flask_cors import CORS
app = Flask(__name__)
CORS(app)
# Register blueprints

app.register_blueprint(qualificate_bp, url_prefix='/qualificate')
app.register_blueprint(school_bp, url_prefix='/school')
app.register_blueprint(authen_bp, url_prefix='/authen')
app.register_blueprint(student_bp, url_prefix='/student')


app.before_request(before_request)

@app.route('/signing')
@login_required
def signing():
    return render_template('signing.html')

@app.route('/getqua')
@login_required
def getqua():
    return render_template('get.html')

@app.route('/verify')
@verifier_required
def verify():
    return render_template('verify.html')
@app.route('/verifykey')
@verifier_required
def verifykey():
    return render_template('verifykey.html')

@app.route('/School')
@verifier_required
@comfirm_issuer
def School():
    return render_template('School.html')

@app.route('/CreateRequestCertificate')
@verifier_required
@comfirm_issuer
def CreateRequestCertificate():
    return render_template('CreateRequestCertificate.html')

@app.route('/createcert')
@verifier_required
@comfirm_issuer
def createcert():
    return render_template('CreateCertificate.html')

@app.route('/Createkey')
@verifier_required
@comfirm_issuer
def Createkey():
    return render_template('CreateKey.html')

@app.route('/issue')
@verifier_required
@comfirm_issuer
def issue():
    return render_template('IssueQualification.html')

@app.route('/useall')
@already_logged_in
def useall():
    return render_template('Company.html')

@app.route('/GetSchool')
@verifier_required
def GetSchool():
    return render_template('GetSchool.html')

@app.route('/account')
@already_logged_in
def account():
    return render_template('account.html')

@app.route('/login')
@already_logged_in
def login():
    return render_template('login.html')

@app.route('/loginverify')
@already_logged_in
def loginverify():
    return render_template('loginverify.html')

@app.route('/register')
@already_logged_in
def register():
    return render_template('register.html')
@app.route('/home')
@already_logged_in
def home():
    return render_template('index.html')
@app.route('/use')
@verifier_required
def use():
    return render_template('dashboardverify.html')

@app.route('/signup')
@already_logged_in
def signup():
    return render_template('registerverify.html')

if __name__ == '__main__':
    app.run(debug=True)