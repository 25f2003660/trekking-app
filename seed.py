<<<<<<< HEAD
from app import app, db, User, StaffProfile, Trek
=======
from app import app, db, User, StaffProfile, Trek, Booking
>>>>>>> 6a295b1 (templates created)

with app.app_context():
    db.drop_all()
    db.create_all()

    admin = User(username="admin", password="adminpass", role="Admin")
    staff_user = User(username="alex", password="staffpass", role="Staff")
    staff_profile = StaffProfile(user_id=1, status='Approved')
        
    db.session.add_all([admin, staff_user, staff_profile])
    db.session.commit()

    trek1 = Trek(
        name='Roopkund Pass',
        location='Uttarakhand, India',
        difficulty='Hard',
        slots=15,
        status='Open'
    )
    trek2 = Trek(
        name='Valley of Flowers',
        location='Uttarakhand, India',
        difficulty='Moderate',
        slots=8,
        status='Pending'
    )
    db.session.add_all([trek1, trek2])
    db.session.commit()
