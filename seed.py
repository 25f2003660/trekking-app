from app import app, db, User, StaffProfile, Trek, Booking

with app.app_context():
    db.drop_all()
    db.create_all()

    admin = User(username="admin", role="Admin")
    admin.set_password("admin")

    staff_user = User(username="staff1", role="Staff")
    staff_user.set_password("staffpass")

    staff_user2 = User(username="staff2", role="Staff")
    staff_user2.set_password("staffpass")

    trekker1 = User(username="user1", role="User")
    trekker1.set_password("userpass")

    trekker2 = User(username="user2", role="User")
    trekker2.set_password("userpass")

    db.session.add_all([admin, staff_user, staff_user2, trekker1, trekker2])
    db.session.commit()

    staff_profile1 = StaffProfile(
        user_id=staff_user.id,
        name="Alex Kumar",
        status='Approved',
    )
    staff_profile2 = StaffProfile(
        user_id=staff_user2.id,
        name="Priya Sharma",
        status='Pending',
    )
    db.session.add_all([staff_profile1, staff_profile2])
    db.session.commit()

    trek1 = Trek(
        name='Roopkund Pass',
        location='Uttarakhand, India',
        difficulty='Hard',
        duration=8,
        slots=15,
        status='Open',
        assigned_staff_id=staff_user.id,
        start_date='01-07-2026',
        end_date='08-07-2026',
    )
    trek2 = Trek(
        name='Manali Valley',
        location='Uttarakhand, India',
        difficulty='Moderate',
        duration=6,
        slots=8,
        status='Pending',
        start_date='15-07-2026',
        end_date='20-07-2026',
    )
    trek3 = Trek(
        name='Himalaya',
        location='Himachal Pradesh, India',
        difficulty='Moderate',
        duration=5,
        slots=12,
        status='Open',
        assigned_staff_id=staff_user.id,
        start_date='05-07-2026',
        end_date='09-07-2026',
    )
    db.session.add_all([trek1, trek2, trek3])
    db.session.commit()

    booking1 = Booking(
        user_id=trekker1.id,
        trek_id=trek1.id,
        booking_date='10-06-2026',
        status='Booked',
    )
    db.session.add(booking1)
    db.session.commit()

    print("Database seeded successfully.")