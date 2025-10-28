from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime
from models import db, User, Absensi
from werkzeug.security import generate_password_hash, check_password_hash
import base64
import os

app = Flask(__name__)
app.secret_key = 'secret-key-absensi'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://absensi_user:absensi12345@localhost/absensi_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Login manager setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Login gagal, periksa username dan password.', 'danger')
    return render_template('login.html')
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if User.query.filter_by(username=username).first():
            flash('Username sudah terdaftar!')
            return redirect(url_for('register'))

        new_user = User(username=username, password=generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()
        flash('Pendaftaran berhasil, silakan login.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/reset', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        username = request.form['username']
        new_password = request.form['new_password']
        user = User.query.filter_by(username=username).first()

        if not user:
            flash('Username tidak ditemukan!')
            return redirect(url_for('reset_password'))

        user.password = generate_password_hash(new_password)
        db.session.commit()
        flash('Password berhasil direset, silakan login.')
        return redirect(url_for('login'))
    return render_template('reset.html')

@app.route('/dashboard')
@login_required
def dashboard():
    absensi = Absensi.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', absensi=absensi)

@app.route('/checkin', methods=['POST'])
@login_required
def checkin():
    latitude = request.form['latitude']
    longitude = request.form['longitude']
    image_data = request.form['image']
    if image_data:
        image_data = image_data.split(",")[1]
        image_bytes = base64.b64decode(image_data)
        filename = f"static/checkin_{current_user.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
        os.makedirs("static", exist_ok=True)
        with open(filename, "wb") as f:
            f.write(image_bytes)
    else:
        filename = None
    now = datetime.now()
    telat = now.hour > 8 or (now.hour == 8 and now.minute > 0)
    absensi = Absensi(user_id=current_user.id, checkin_time=datetime.now(),
                      latitude=latitude, longitude=longitude, image_path=filename)
    db.session.add(absensi)
    db.session.commit()
    if telat:
        flash('⚠️ Datang Telat! Check-in setelah jam 08:00.', 'danger')
    else:
        flash('✅ Check-in berhasil, tepat waktu.', 'success')
    return redirect(url_for('dashboard'))

@app.route('/checkout/<int:id>', methods=['POST'])
@login_required
def checkout(id):
    absensi = Absensi.query.get(id)
    now = datetime.now()
    absensi.checkout_time = datetime.now()
    db.session.commit()
    if now.hour < 17:
        flash('⚠️ Pulang lebih cepat dari jam 17:00.', 'warning')
    else:
        flash('✅ Checkout berhasil, sampai besok!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)


