from extensions import db
from werkzeug.security import generate_password_hash
from datetime import datetime



def parse_dt(value):
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    for mask in ('%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M', '%Y-%m-%d'):
        try:
            return datetime.strptime(value, mask)
        except (ValueError, TypeError):
            continue
    return None


def fmt_dt(value):
    """Serialize a datetime back to the "%Y-%m-%d" string the UI expects."""
    if isinstance(value, datetime):
        return value.strftime('%Y-%m-%d')
    return value or ''



class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)   # login id
    password = db.Column(db.String(200), nullable=False)             # hashed
    full_name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20))
    role = db.Column(db.String(20), nullable=False, default='trekker')  # admin/staff/trekker
    is_blacklisted = db.Column(db.Boolean, default=False)  # blacklist flag
    is_deleted = db.Column(db.Boolean, default=False)      # soft-delete flag
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    bookings = db.relationship(
        'Booking', backref='trekker',
        foreign_keys='Booking.user_id',
        cascade='all, delete-orphan', lazy=True,
    )
    staff_profile = db.relationship(
        'StaffProfile', backref='user',
        cascade='all, delete-orphan', uselist=False, lazy=True,
    )




class StaffProfile(db.Model):
    __tablename__ = 'staff_profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True)
    emergency_contact = db.Column(db.String(50))
    bio = db.Column(db.Text)
    status = db.Column(db.String(20), default='active')  # active/on_leave/inactive



class Trek(db.Model):
    __tablename__ = 'treks'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    location = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    difficulty = db.Column(db.String(20), default='Easy')   # Easy/Moderate/Hard
    duration_days = db.Column(db.Integer, default=1)
    total_slots = db.Column(db.Integer, default=0)
    available_slots = db.Column(db.Integer, default=0)   # goes down on booking
    price = db.Column(db.Float, default=0.0)
    assigned_staff_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # nullable
    status = db.Column(db.String(20), default='Approved')
    start_date = db.Column(db.DateTime)   # real datetime (time-series)
    end_date = db.Column(db.DateTime)
    created_by_admin_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    is_deleted = db.Column(db.Boolean, default=False)   # soft-delete flag
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # A trek owns its bookings: deleting a trek cascades to its bookings.
    bookings = db.relationship(
        'Booking', backref='trek',
        cascade='all, delete-orphan', lazy=True,
    )



class Booking(db.Model):
    __tablename__ = 'bookings'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    trek_id = db.Column(db.Integer, db.ForeignKey('treks.id'), nullable=False)
    booking_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='Booked')   # Booked/Cancelled/Completed
    payment_status = db.Column(db.String(20), default='Pending')  # optional
    notes = db.Column(db.Text)



def create_admin():
    admin = User.query.filter_by(role='admin').first()
    if not admin:
        admin = User(
            email='admin@gmail.com',
            password=generate_password_hash('admin123'),
            full_name='Admin User',
            role='admin',
        )
        db.session.add(admin)
        db.session.commit()
    return admin
