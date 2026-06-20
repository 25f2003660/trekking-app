from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trekking.db'
db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(12), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(12), nullable=False)


class StaffProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    status = db.Column(db.String(20), default='Pending') 

class Trek(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    difficulty = db.Column(db.String(20), default='Moderate')
    slots = db.Column(db.Integer, default=10)
    status = db.Column(db.String(20), default='Open')
    assigned_staff_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

class Booking(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    trek_id = db.Column(db.Integer, db.ForeignKey('trek.id'), nullable=False)
    status = db.Column(db.String(20), default='Booked')

def init_database():
    os.makedirs(app.instance_path, exist_ok=True)

    with app.app_context():
        db.create_all()        
        admin_user = User.query.filter_by(role='Admin', username='admin').first()
        if not admin_user:
            hashed_password = generate_password_hash("admin")
            seeded_admin = User(username='admin',password=hashed_password, role='Admin')
            seeded_admin.set_password("admin")
            db.session.add(seeded_admin)
            db.session.commit()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/register-submit', methods=['GET', 'POST'])
def register_submit():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')
        if role == 'admin':
            return redirect('/register')
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return redirect('/register')

        new_user = User(username=username, password=password, role=role)
        db.session.add(new_user)
        db.session.commit()

        return redirect('/')

    return render_template('register.html')


@app.route('/login-submit', methods=['POST'])
def login_submit():
    username = request.form.get('username')
    password = request.form.get('password')
    selected_role = request.form.get('role')

    if not username or not password or not selected_role:
        return redirect('/')

    user = User.query.filter_by(username=username, role=selected_role).first()
<<<<<<< HEAD
    print("-----------------------------------------\n\n\n")
    print(user)
    print("\n\n\n-----------------------------------------")
=======
>>>>>>> 6a295b1 (templates created)
    if not user:
        return redirect('/')

    if not user.password == password:
        return redirect('/')

    if selected_role == 'Admin':
        return redirect('/admin')
    elif selected_role == 'Staff':
        return redirect(f'/staff/dashboard/{user.id}')
    elif selected_role == 'User':
        return redirect(f'/user/dashboard/{user.id}')

    return redirect('/')

@app.route('/admin')
def admin_dashboard():
    total_treks = Trek.query.count()
    total_users = User.query.count()
    treks = Trek.query.all()
    return render_template('admin_dashboard.html', total_treks=total_treks, total_users=total_users, treks=treks)


@app.route('/staff/dashboard/<int:user_id>')
def staff_dashboard(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('staff_dashboard.html', user=user)


@app.route('/user/dashboard/<int:user_id>')
def user_dashboard(user_id):
    user = User.query.get_or_404(user_id)
    open_treks = Trek.query.filter_by(status='Open').all()
    bookings = Booking.query.filter_by(user_id=user_id).all()
    return render_template('user_dashboard.html', user=user, open_treks=open_treks, bookings=bookings)



if __name__ == '__main__':
    app.run(debug=True)
