from flask import Flask
import os
from models import db, User

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trekking.db'
app.config['SECRET_KEY'] = 'siddhartham'

db.init_app(app)


def init_database():
    os.makedirs(app.instance_path, exist_ok=True)

    with app.app_context():
        db.create_all()

        admin_user = User.query.filter_by(role='Admin', username='admin').first()
        if not admin_user:
            seeded_admin = User(username='admin', password='', role='Admin')
            seeded_admin.set_password("admin")
            db.session.add(seeded_admin)
            db.session.commit()

# Import routes at the end to avoid circular dependency
from routes import *

if __name__ == '__main__':
    init_database()
    app.run(debug=True)