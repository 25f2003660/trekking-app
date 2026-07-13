from flask import render_template, request, redirect
from app import app
from models import db, User, StaffProfile, Trek, Booking
from datetime import datetime

@app.route('/')
def home():
    return render_template('home.html', hide_home=True)


@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/register-submit', methods=['GET', 'POST'])
def register_submit():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')
        if role == 'admin' or role == 'Admin':
            return redirect('/register')
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return redirect('/register')

        new_user = User(username=username, role=role)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        if role == 'Staff':
            profile = StaffProfile(user_id=new_user.id, name=username, status='Pending')
            db.session.add(profile)
            db.session.commit()

        return redirect('/')

    return render_template('register.html')


@app.route('/login-submit', methods=['POST'])
def login_submit():
    username = request.form.get('username')
    password = request.form.get('password')
    selected_role = request.form.get('role')

    if not username or not password or not selected_role:
        return render_template('home.html', error="Please provide username, password, and role.", hide_home=True)

    user = User.query.filter_by(username=username, role=selected_role).first()
    if not user:
        return render_template('home.html', error="Invalid username or role.", hide_home=True)

    if not user.check_password(password):
        return render_template('home.html', error="Incorrect password.", hide_home=True)

    if user.is_blacklisted:
        return render_template('home.html', error="Your account has been blacklisted.", hide_home=True)
    if selected_role == 'Admin':
        return redirect('/admin')
        
    elif selected_role == 'Staff':
        profile = StaffProfile.query.filter_by(user_id=user.id).first()
        if not profile or profile.status != 'Approved':
            return render_template('staff_pending.html', username=user.username)
        return redirect(f'/staff/dashboard/{user.id}')
    elif selected_role == 'User':
        return redirect(f'/user/dashboard/{user.id}')
    
    return redirect('/')

def _safe_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return -1

#admin

@app.route('/admin')
def admin_dashboard():
    search = request.args.get('search', '').strip()

    treks_query = Trek.query
    staff_query = StaffProfile.query.join(User)
    users_query = User.query.filter_by(role='User')

    if search:
        like = f"%{search}%"
        treks_query = treks_query.filter(
            db.or_(Trek.name.ilike(like), Trek.location.ilike(like), Trek.id == _safe_int(search))
        )
        staff_query = staff_query.filter(
            db.or_(User.username.ilike(like), User.id == _safe_int(search))
        )
        users_query = users_query.filter(
            db.or_(User.username.ilike(like), User.id == _safe_int(search))
        )

    treks = treks_query.all()
    staff_profiles = staff_query.all()
    users = users_query.all()

    total_treks = Trek.query.count()
    pending_staff = StaffProfile.query.filter_by(status='Pending').count()
    active_bookings = Booking.query.filter_by(status='Booked').count()

    approved_staff = (
        User.query.join(StaffProfile, User.id == StaffProfile.user_id)
        .filter(StaffProfile.status == 'Approved', User.is_blacklisted.is_(False))
        .all()
    )

    return render_template(
        'admin_dashboard.html',
        treks=treks,
        staff_profiles=staff_profiles,
        users=users,
        total_treks=total_treks,
        pending_staff=pending_staff,
        active_bookings=active_bookings,
        approved_staff=approved_staff,
        search=search,
        show_logout=True,
    )


@app.route('/admin/trek/add', methods=['POST'])
def admin_add_trek():
    name = request.form.get('name')
    location = request.form.get('location')
    difficulty = request.form.get('difficulty', 'Moderate')
    duration = request.form.get('duration', type=int) or 1
    slots = request.form.get('slots', type=int) or 10
    status = request.form.get('status', 'Pending')
    start_date = request.form.get('start_date', '')
    end_date = request.form.get('end_date', '')

    if name and location:
        trek = Trek(
            name=name,
            location=location,
            difficulty=difficulty,
            duration=duration,
            slots=slots,
            status=status,
            start_date=start_date,
            end_date=end_date,
        )
        db.session.add(trek)
        db.session.commit()

    return redirect('/admin')


@app.route('/admin/trek/edit/<int:trek_id>', methods=['POST'])
def admin_edit_trek(trek_id):
    trek = Trek.query.get_or_404(trek_id)

    trek.name = request.form.get('name', trek.name)
    trek.location = request.form.get('location', trek.location)
    trek.difficulty = request.form.get('difficulty', trek.difficulty)
    duration = request.form.get('duration', type=int)
    if duration is not None:
        trek.duration = duration
    slots = request.form.get('slots', type=int)
    if slots is not None:
        trek.slots = slots
    trek.status = request.form.get('status', trek.status)
    if trek.status == 'Closed' or trek.status == 'Completed' or trek.status == 'Ongoing':
        trek.slots = 0
    
    trek.start_date = request.form.get('start_date', trek.start_date)
    trek.end_date = request.form.get('end_date', trek.end_date)

    db.session.commit()
    return redirect('/admin')


@app.route('/admin/trek/remove/<int:trek_id>', methods=['POST'])
def admin_remove_trek(trek_id):
    trek = Trek.query.get_or_404(trek_id)
    Booking.query.filter_by(trek_id=trek.id).delete()
    db.session.delete(trek)
    db.session.commit()
    return redirect('/admin')


@app.route('/admin/trek/assign/<int:trek_id>', methods=['POST'])
def admin_assign_staff(trek_id):
    trek = Trek.query.get_or_404(trek_id)
    staff_id = request.form.get('staff_id', type=int)
    trek.assigned_staff_id = staff_id
    db.session.commit()
    return redirect('/admin')


@app.route('/admin/staff/approve/<int:user_id>', methods=['POST'])
def admin_approve_staff(user_id):
    profile = StaffProfile.query.filter_by(user_id=user_id).first_or_404()
    profile.status = 'Approved'
    db.session.commit()
    return redirect('/admin')


@app.route('/admin/staff/blacklist/<int:user_id>', methods=['POST'])
def admin_blacklist_staff(user_id):
    profile = StaffProfile.query.filter_by(user_id=user_id).first_or_404()
    profile.status = 'Blacklisted'
    user = User.query.get(user_id)
    if user:
        user.is_blacklisted = True
    db.session.commit()
    return redirect('/admin')

@app.route('/admin/staff/unblacklist/<int:user_id>', methods=['POST'])
def admin_unblacklist_staff(user_id):
    profile = StaffProfile.query.filter_by(user_id=user_id).first_or_404()
    profile.status = 'Approved'
    user = User.query.get(user_id)
    if user:
        user.is_blacklisted = False
    db.session.commit()
    return redirect('/admin')


@app.route('/admin/user/blacklist/<int:user_id>', methods=['POST'])
def admin_blacklist_user(user_id):
    user = User.query.get_or_404(user_id)
    user.is_blacklisted = True
    db.session.commit()
    return redirect('/admin')


@app.route('/admin/user/unblacklist/<int:user_id>', methods=['POST'])
def admin_unblacklist_user(user_id):
    user = User.query.get_or_404(user_id)
    user.is_blacklisted = False
    db.session.commit()
    return redirect('/admin')

#staff

@app.route('/staff/dashboard/<int:user_id>')
def staff_dashboard(user_id):
    user = User.query.get_or_404(user_id)
    assigned_treks = Trek.query.filter_by(assigned_staff_id=user_id).all()


    trek_ids = [t.id for t in assigned_treks]
    registered_bookings = []
    if trek_ids:
        registered_bookings = Booking.query.filter(Booking.trek_id.in_(trek_ids)).all()

    return render_template(
        'staff_dashboard.html',
        user=user,
        username=user.username,
        assigned_treks=assigned_treks,
        registered_bookings=registered_bookings,
        show_logout=True,
    )


@app.route('/staff/trek/update/<int:trek_id>', methods=['POST'])
def staff_update_trek(trek_id):
    trek = Trek.query.get_or_404(trek_id)
    user_id = request.form.get('user_id', type=int)

    slots = request.form.get('slots', type=int)
    if slots is not None:
        trek.slots = slots

    new_status = request.form.get('new_status')
    if new_status:
        trek.status = new_status
    if trek.status == 'Closed' or trek.status == 'Completed' or trek.status == 'Ongoing':
        trek.slots = 0

    db.session.commit()
    return redirect(f'/staff/dashboard/{user_id}')


#user

@app.route('/user/dashboard/<int:user_id>')
def user_dashboard(user_id):
    user = User.query.get_or_404(user_id)

    difficulty = request.args.get('difficulty', '').strip()
    location = request.args.get('location', '').strip()

    open_treks_query = Trek.query.filter_by(status='Open')
    if difficulty:
        open_treks_query = open_treks_query.filter(Trek.difficulty == difficulty)
    if location:
        open_treks_query = open_treks_query.filter(Trek.location.ilike(f"%{location}%"))

    open_treks = open_treks_query.all()
    bookings = Booking.query.filter_by(user_id=user_id).all()

    return render_template(
        'user_dashboard.html',
        user=user,
        username=user.username,
        open_treks=open_treks,
        bookings=bookings,
        difficulty=difficulty,
        location=location,
        show_logout=True,
    )


@app.route('/user/trek/book/<int:trek_id>', methods=['POST'])
def user_book_trek(trek_id):
    user_id = request.form.get('user_id', type=int)
    trek = Trek.query.get_or_404(trek_id)

    if trek.status == 'Open' and trek.slots > 0:
        return render_template('payment.html', trek=trek, user_id=user_id, show_logout=True)

    return redirect(f'/user/dashboard/{user_id}')


@app.route('/user/payment/confirm', methods=['POST'])
def user_payment_confirm():
    user_id = request.form.get('user_id', type=int)
    trek_id = request.form.get('trek_id', type=int)
    payment_id = request.form.get('payment_id', '').strip()

    if not payment_id:
        trek = Trek.query.get_or_404(trek_id)
        return render_template('payment.html', trek=trek, user_id=user_id, show_logout=True, error='Payment ID is required.')

    trek = Trek.query.get_or_404(trek_id)
    if trek.status == 'Open' and trek.slots > 0:
        booking = Booking(
            user_id=user_id,
            trek_id=trek_id,
            booking_date=datetime.utcnow().strftime('%d-%m-%Y'),
            status='Booked',
            payment_id=payment_id,
        )
        trek.slots -= 1
        db.session.add(booking)
        db.session.commit()

    return redirect(f'/user/dashboard/{user_id}')


@app.route('/user/profile/<int:user_id>', methods=['GET', 'POST'])
def user_profile(user_id):
    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        new_username = request.form.get('username', '').strip()
        new_password = request.form.get('password', '').strip()
        new_email = request.form.get('email', '').strip()
        new_phone = request.form.get('phone', '').strip()

        if new_username and new_username != user.username:
            existing = User.query.filter_by(username=new_username).first()
            if not existing:
                user.username = new_username

        if new_password:
            user.set_password(new_password)

        user.email = new_email
        user.phone = new_phone
        db.session.commit()
        return redirect(f'/user/dashboard/{user_id}')

    return render_template('user_profile.html', user=user, show_logout=True)


@app.route('/user/booking/cancel/<int:booking_id>', methods=['POST'])
def user_cancel_booking(booking_id):
    user_id = request.form.get('user_id', type=int)
    booking = Booking.query.get_or_404(booking_id)

    if booking.status == 'Booked':
        booking.status = 'Cancelled'
        trek = Trek.query.get(booking.trek_id)
        if trek:
            trek.slots += 1
        db.session.commit()

    return redirect(f'/user/dashboard/{user_id}')
