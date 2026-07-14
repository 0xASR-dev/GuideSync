"""
Seed script.

Run this once to create the database tables and fill in some sample data
so the demo has treks, a staff account, and a trekker to log in with.

    python seed.py

It is safe to run again - it skips anything that already exists.
Login details created here:
    admin   -> admin@gmail.com  / admin123
    staff   -> staff@gmail.com  / staff123
    trekker -> trekker@gmail.com / trek123
"""
from datetime import datetime
from werkzeug.security import generate_password_hash
from app import app
from extensions import db
from models import User, StaffProfile, Trek, create_admin


def get_or_create_user(email, password, full_name, role, phone=''):
    user = User.query.filter_by(email=email).first()
    if user:
        return user
    user = User(
        email=email,
        password=generate_password_hash(password),
        full_name=full_name,
        role=role,
        phone=phone,
    )
    db.session.add(user)
    db.session.commit()
    return user


with app.app_context():
    db.create_all()

    # 1) the single admin
    create_admin()

    # 2) a staff account (+ profile)
    staff = get_or_create_user('staff@gmail.com', 'staff123', 'Sam Staff', 'staff', '9990001111')
    if not StaffProfile.query.filter_by(user_id=staff.id).first():
        db.session.add(StaffProfile(user_id=staff.id, bio='Experienced mountain guide', status='active'))
        db.session.commit()

    # 3) a trekker account
    get_or_create_user('trekker@gmail.com', 'trek123', 'Tina Trekker', 'trekker', '8880002222')

    # 4) a couple of treks (one Open and assigned to staff, one still Approved)
    if not Trek.query.first():
        t1 = Trek(
            name='Triund Trek', location='Himachal Pradesh',
            description='Beginner friendly trek with great views.',
            difficulty='Easy', duration_days=2,
            total_slots=10, available_slots=10, price=1500,
            status='Open',
            start_date=datetime(2026, 8, 1, 6, 0),
            end_date=datetime(2026, 8, 2, 18, 0),
            assigned_staff_id=staff.id, created_by_admin_id=1,
        )
        t2 = Trek(
            name='Hampta Pass', location='Manali',
            description='Moderate crossover trek.',
            difficulty='Moderate', duration_days=5,
            total_slots=8, available_slots=8, price=8500,
            status='Approved',
            start_date=datetime(2026, 9, 10, 6, 0),
            end_date=datetime(2026, 9, 15, 18, 0),
            created_by_admin_id=1,
        )
        db.session.add_all([t1, t2])
        db.session.commit()

    print('Seed complete. Admin: admin@gmail.com/admin123, '
          'Staff: staff@gmail.com/staff123, Trekker: trekker@gmail.com/trek123')
