import os
from werkzeug.utils import secure_filename
from flask import send_file
from cryptography.fernet import Fernet
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cloudvault.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ENCRYPTION_KEY = Fernet.generate_key()
cipher = Fernet(ENCRYPTION_KEY)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='user')

class FileRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200), nullable=False)
    stored_filename = db.Column(db.String(200), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    upload_time = db.Column(db.DateTime, default=db.func.current_timestamp())
    encrypted = db.Column(db.Boolean, default=True)

class AccessRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_id = db.Column(db.Integer, db.ForeignKey('file_record.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    status = db.Column(db.String(20), default='Pending')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def home():
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        if not username or not email or not password:
            flash('All fields are required.')
            return redirect(url_for('register'))

        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()

        if existing_user:
            flash('Username or email already exists.')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password)

        new_user = User(
            username=username,
            email=email,
            password=hashed_password,
            role='user'
        )

        db.session.add(new_user)
        db.session.commit()

        flash('Account created. Please login.')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if not user or not check_password_hash(user.password, password):
            flash('Invalid username or password.')
            return redirect(url_for('login'))

        login_user(user)
        return redirect(url_for('dashboard'))

    return render_template('login.html')


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.')
    return redirect(url_for('login'))

@app.route('/request-access', methods=['GET', 'POST'])
@login_required
def request_access():
    files = FileRecord.query.all()

    if request.method == 'POST':
        file_id = request.form.get('file_id')

        new_request = AccessRequest(
            file_id=file_id,
            user_id=current_user.id
        )

        db.session.add(new_request)
        db.session.commit()

        flash('Access request submitted.')
        return redirect(url_for('dashboard'))

    return render_template('request_access.html', files=files)

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        uploaded_file = request.files.get('file')

        if not uploaded_file or uploaded_file.filename == '':
            flash('Please select a file.')
            return redirect(url_for('upload'))

        filename = secure_filename(uploaded_file.filename)
        file_data = uploaded_file.read()
        encrypted_data = cipher.encrypt(file_data)

        stored_filename = f"{current_user.id}_{filename}.enc"
        file_path = os.path.join(UPLOAD_FOLDER, stored_filename)

        with open(file_path, 'wb') as f:
            f.write(encrypted_data)

        file_record = FileRecord(
            filename=filename,
            stored_filename=stored_filename,
            owner_id=current_user.id
        )

        db.session.add(file_record)
        db.session.commit()

        flash('File uploaded and encrypted successfully.')
        return redirect(url_for('my_files'))

    return render_template('upload.html')

@app.route('/approve/<int:request_id>')
@login_required
def approve_request(request_id):
    if current_user.role != 'admin':
        return redirect(url_for('dashboard'))

    req = AccessRequest.query.get(request_id)
    req.status = 'Approved'
    db.session.commit()

    return redirect(url_for('admin'))


@app.route('/deny/<int:request_id>')
@login_required
def deny_request(request_id):
    if current_user.role != 'admin':
        return redirect(url_for('dashboard'))

    req = AccessRequest.query.get(request_id)
    req.status = 'Denied'
    db.session.commit()

    return redirect(url_for('admin'))

@app.route('/my-files')
@login_required
def my_files():
    files = FileRecord.query.filter_by(owner_id=current_user.id).all()
    return render_template('my_files.html', files=files)

@app.route('/admin')
@login_required
def admin():
    if current_user.role != 'admin':
        flash('Admin access only.')
        return redirect(url_for('dashboard'))

    users = User.query.all()
    requests = AccessRequest.query.all()

    return render_template('admin.html', users=users, requests=requests)

@app.route('/my-requests')
@login_required
def my_requests():
    requests = AccessRequest.query.filter_by(user_id=current_user.id).all()
    return render_template('my_requests.html', requests=requests)


@app.route('/download-request/<int:request_id>')
@login_required
def download_request(request_id):
    access_request = AccessRequest.query.get_or_404(request_id)

    if access_request.user_id != current_user.id:
        flash('You are not allowed to access this request.')
        return redirect(url_for('dashboard'))

    if access_request.status != 'Approved':
        flash('This request is not approved yet.')
        return redirect(url_for('my_requests'))

    file_record = FileRecord.query.get_or_404(access_request.file_id)
    encrypted_path = os.path.join(UPLOAD_FOLDER, file_record.stored_filename)

    with open(encrypted_path, 'rb') as f:
        encrypted_data = f.read()

    decrypted_data = cipher.decrypt(encrypted_data)

    temp_path = os.path.join(UPLOAD_FOLDER, "decrypted_" + file_record.filename)

    with open(temp_path, 'wb') as f:
        f.write(decrypted_data)

    return send_file(temp_path, as_attachment=True, download_name=file_record.filename)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(
                username='admin',
                email='admin@cloudvault.com',
                password=generate_password_hash('admin123'),
                role='admin'
            )
            db.session.add(admin_user)
            db.session.commit()

    app.run(debug=True)
