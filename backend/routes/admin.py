from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash
from extensions import db, cache
from models import User, StaffProfile, Trek, Booking, parse_dt, fmt_dt
from routes.utils import role_required
from routes import cache_service

admin_bp = Blueprint('admin', __name__)


# ==========================================================================
# DASHBOARD
# Global (same for every admin) -> @cache.cached() decorator.
# Invalidated on writes via cache.delete(KEY_ADMIN_DASHBOARD).
# ==========================================================================
@admin_bp.route('/dashboard', methods=['GET'])
@jwt_required()
@role_required('admin')
@cache.cached(timeout=120, key_prefix=cache_service.KEY_ADMIN_DASHBOARD)
def dashboard():
    data = {
        'total_treks': Trek.query.filter_by(is_deleted=False).count(),
        'total_trekkers': User.query.filter_by(role='trekker', is_deleted=False).count(),
        'total_staff': User.query.filter_by(role='staff', is_deleted=False).count(),
        'total_bookings': Booking.query.count(),
    }
    return jsonify(data), 200


# ==========================================================================
# TREK CRUD
# ==========================================================================
@admin_bp.route('/treks', methods=['GET'])
@jwt_required()
@role_required('admin')
def list_treks():
    treks = Trek.query.filter_by(is_deleted=False).order_by(Trek.id.desc()).all()
    result = []
    for t in treks:
        staff = User.query.get(t.assigned_staff_id) if t.assigned_staff_id else None
        result.append({
            'id': t.id,
            'name': t.name,
            'location': t.location,
            'difficulty': t.difficulty,
            'duration_days': t.duration_days,
            'total_slots': t.total_slots,
            'available_slots': t.available_slots,
            'price': t.price,
            'status': t.status,
            'start_date': fmt_dt(t.start_date),
            'end_date': fmt_dt(t.end_date),
            'assigned_staff': staff.full_name if staff else None,
            'assigned_staff_id': t.assigned_staff_id,
        })
    return jsonify({'treks': result}), 200


@admin_bp.route('/treks', methods=['POST'])
@jwt_required()
@role_required('admin')
def create_trek():
    data = request.get_json() or {}
    if not data.get('name') or not data.get('location'):
        return jsonify({'message': 'name and location are required'}), 400

    total = int(data.get('total_slots', 0))
    trek = Trek(
        name=data['name'],
        location=data['location'],
        description=data.get('description', ''),
        difficulty=data.get('difficulty', 'Easy'),
        duration_days=int(data.get('duration_days', 1)),
        total_slots=total,
        available_slots=total,               # start full
        price=float(data.get('price', 0)),
        status='Approved',                   # not bookable until staff assigned
        start_date=parse_dt(data.get('start_date')),
        end_date=parse_dt(data.get('end_date')),
        created_by_admin_id=get_jwt_identity(),
    )
    db.session.add(trek)
    db.session.commit()
    cache_service.clear_all_trek_caches()
    return jsonify({'message': 'Trek created', 'trek_id': trek.id}), 201


@admin_bp.route('/treks/<int:trek_id>', methods=['PUT'])
@jwt_required()
@role_required('admin')
def update_trek(trek_id):
    trek = Trek.query.get(trek_id)
    if not trek:
        return jsonify({'message': 'Trek not found'}), 404

    data = request.get_json() or {}
    trek.name = data.get('name', trek.name)
    trek.location = data.get('location', trek.location)
    trek.description = data.get('description', trek.description)
    trek.difficulty = data.get('difficulty', trek.difficulty)
    trek.duration_days = int(data.get('duration_days', trek.duration_days))
    trek.price = float(data.get('price', trek.price))
    if 'start_date' in data:
        trek.start_date = parse_dt(data['start_date'])
    if 'end_date' in data:
        trek.end_date = parse_dt(data['end_date'])

    # if admin changes total slots, adjust available slots by the same difference
    if 'total_slots' in data:
        new_total = int(data['total_slots'])
        booked = trek.total_slots - trek.available_slots
        trek.total_slots = new_total
        trek.available_slots = max(new_total - booked, 0)

    db.session.commit()
    cache_service.clear_all_trek_caches()
    return jsonify({'message': 'Trek updated'}), 200


@admin_bp.route('/treks/<int:trek_id>', methods=['DELETE'])
@jwt_required()
@role_required('admin')
def delete_trek(trek_id):
    trek = Trek.query.filter_by(id=trek_id, is_deleted=False).first()
    if not trek:
        return jsonify({'message': 'Trek not found'}), 404
    # Soft delete: keep the row (and its bookings) for historical analytics,
    # just hide it from active listings. The cascade relationship is still
    # configured so a real db.session.delete(trek) would clean up bookings.
    trek.is_deleted = True
    db.session.commit()
    cache_service.clear_all_trek_caches()
    return jsonify({'message': 'Trek deleted'}), 200


# Assign staff to a trek -> trek becomes 'Open' (now visible/bookable)
@admin_bp.route('/treks/<int:trek_id>/assign-staff', methods=['POST'])
@jwt_required()
@role_required('admin')
def assign_staff(trek_id):
    trek = Trek.query.get(trek_id)
    if not trek:
        return jsonify({'message': 'Trek not found'}), 404

    data = request.get_json() or {}
    staff = User.query.filter_by(id=data.get('staff_user_id'), role='staff').first()
    if not staff:
        return jsonify({'message': 'Staff not found'}), 404

    trek.assigned_staff_id = staff.id
    trek.status = 'Open'
    db.session.commit()
    cache_service.clear_all_trek_caches()
    return jsonify({'message': 'Staff assigned, trek is now Open'}), 200


# ==========================================================================
# STAFF ACCOUNTS
# ==========================================================================
@admin_bp.route('/staff', methods=['GET'])
@jwt_required()
@role_required('admin')
def list_staff():
    staff_users = User.query.filter_by(role='staff', is_deleted=False).all()
    result = []
    for u in staff_users:
        profile = StaffProfile.query.filter_by(user_id=u.id).first()
        result.append({
            'id': u.id,
            'full_name': u.full_name,
            'email': u.email,
            'phone': u.phone,
            'is_active': u.is_active,
            'is_blacklisted': u.is_blacklisted,
            'bio': profile.bio if profile else '',
        })
    return jsonify({'staff': result}), 200


@admin_bp.route('/staff', methods=['POST'])
@jwt_required()
@role_required('admin')
def create_staff():
    data = request.get_json() or {}
    if not data.get('email') or not data.get('password') or not data.get('full_name'):
        return jsonify({'message': 'email, password and full_name are required'}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'Email already exists'}), 400

    user = User(
        email=data['email'],
        password=generate_password_hash(data['password']),
        full_name=data['full_name'],
        phone=data.get('phone', ''),
        role='staff',
    )
    db.session.add(user)
    db.session.commit()

    profile = StaffProfile(
        user_id=user.id,
        emergency_contact=data.get('emergency_contact', ''),
        bio=data.get('bio', ''),
        status='active',
    )
    db.session.add(profile)
    db.session.commit()
    return jsonify({'message': 'Staff created', 'staff_id': user.id}), 201


# ==========================================================================
# USERS  (list + deactivate + blacklist)
# ==========================================================================
@admin_bp.route('/users', methods=['GET'])
@jwt_required()
@role_required('admin')
def list_users():
    users = User.query.filter_by(role='trekker', is_deleted=False).all()
    result = [{
        'id': u.id,
        'full_name': u.full_name,
        'email': u.email,
        'phone': u.phone,
        'is_active': u.is_active,
        'is_blacklisted': u.is_blacklisted,
    } for u in users]
    return jsonify({'users': result}), 200


@admin_bp.route('/users/<int:user_id>/deactivate', methods=['PATCH'])
@jwt_required()
@role_required('admin')
def toggle_deactivate(user_id):
    user = User.query.get(user_id)
    if not user or user.role == 'admin':
        return jsonify({'message': 'User not found'}), 404
    user.is_active = not user.is_active   # toggle on/off
    db.session.commit()
    return jsonify({'message': 'active' if user.is_active else 'deactivated'}), 200


@admin_bp.route('/users/<int:user_id>/blacklist', methods=['PATCH'])
@jwt_required()
@role_required('admin')
def toggle_blacklist(user_id):
    user = User.query.get(user_id)
    if not user or user.role == 'admin':
        return jsonify({'message': 'User not found'}), 404
    user.is_blacklisted = not user.is_blacklisted   # toggle on/off
    db.session.commit()
    return jsonify({'message': 'blacklisted' if user.is_blacklisted else 'un-blacklisted'}), 200


# ==========================================================================
# ALL BOOKINGS
# ==========================================================================
@admin_bp.route('/bookings', methods=['GET'])
@jwt_required()
@role_required('admin')
def list_bookings():
    bookings = Booking.query.order_by(Booking.id.desc()).all()
    result = []
    for b in bookings:
        user = User.query.get(b.user_id)
        trek = Trek.query.get(b.trek_id)
        result.append({
            'id': b.id,
            'trekker': user.full_name if user else 'Unknown',
            'trek': trek.name if trek else 'Unknown',
            'status': b.status,
            'booking_date': b.booking_date.strftime('%Y-%m-%d') if b.booking_date else '',
        })
    return jsonify({'bookings': result}), 200


# ==========================================================================
# SEARCH  ?type=user|staff|trek&q=...
# ==========================================================================
@admin_bp.route('/search', methods=['GET'])
@jwt_required()
@role_required('admin')
def search():
    kind = request.args.get('type', 'trek')
    q = request.args.get('q', '')
    like = f'%{q}%'
    result = []

    if kind == 'trek':
        for t in Trek.query.filter(Trek.name.like(like)).all():
            result.append({'id': t.id, 'name': t.name, 'location': t.location, 'status': t.status})
    elif kind == 'staff':
        for u in User.query.filter(User.role == 'staff', User.full_name.like(like)).all():
            result.append({'id': u.id, 'full_name': u.full_name, 'email': u.email})
    else:  # user / trekker
        for u in User.query.filter(User.role == 'trekker', User.full_name.like(like)).all():
            result.append({'id': u.id, 'full_name': u.full_name, 'email': u.email})

    return jsonify({'results': result}), 200


# ==========================================================================
# ANALYTICS  (optional feature - data shaped for Chart.js)
# ==========================================================================
@admin_bp.route('/reports/analytics', methods=['GET'])
@jwt_required()
@role_required('admin')
def analytics():
    # Popular treks = number of bookings per trek
    treks = Trek.query.filter_by(is_deleted=False).all()
    labels = []
    counts = []
    for t in treks:
        labels.append(t.name)
        counts.append(Booking.query.filter_by(trek_id=t.id).count())

    return jsonify({
        'popular_treks': {'labels': labels, 'counts': counts},
        'booking_status': {
            'Booked': Booking.query.filter_by(status='Booked').count(),
            'Cancelled': Booking.query.filter_by(status='Cancelled').count(),
            'Completed': Booking.query.filter_by(status='Completed').count(),
        },
    }), 200


# ==========================================================================
# SYSTEM SUMMARY  (a full snapshot of the whole system for the Report page)
# ==========================================================================
@admin_bp.route('/reports/summary', methods=['GET'])
@jwt_required()
@role_required('admin')
def summary():
    treks = Trek.query.filter_by(is_deleted=False).all()
    bookings = Booking.query.all()

    # count treks grouped by their lifecycle status
    trek_by_status = {}
    for t in treks:
        trek_by_status[t.status] = trek_by_status.get(t.status, 0) + 1

    # count bookings grouped by status
    booking_by_status = {}
    for b in bookings:
        booking_by_status[b.status] = booking_by_status.get(b.status, 0) + 1

    # estimated revenue from active + completed bookings
    price_by_trek = {t.id: t.price for t in treks}
    revenue = sum(
        price_by_trek.get(b.trek_id, 0)
        for b in bookings if b.status in ('Booked', 'Completed')
    )

    trekkers = User.query.filter_by(role='trekker', is_deleted=False).all()
    staff = User.query.filter_by(role='staff', is_deleted=False).all()

    # top 5 popular treks by total bookings
    popularity = sorted(
        ((t.name, Booking.query.filter_by(trek_id=t.id).count()) for t in treks),
        key=lambda x: x[1], reverse=True,
    )[:5]

    return jsonify({
        'treks': {
            'total': len(treks),
            'by_status': trek_by_status,
            'open': trek_by_status.get('Open', 0),
        },
        'bookings': {
            'total': len(bookings),
            'by_status': booking_by_status,
        },
        'users': {
            'trekkers': len(trekkers),
            'active_trekkers': sum(1 for u in trekkers if u.is_active and not u.is_blacklisted),
            'blacklisted': sum(1 for u in trekkers if u.is_blacklisted),
        },
        'staff': {
            'total': len(staff),
            'active': sum(1 for u in staff if u.is_active and not u.is_blacklisted),
        },
        'revenue_estimate': round(revenue, 2),
        'top_treks': [{'name': n, 'bookings': c} for n, c in popularity],
    }), 200


# ==========================================================================
# BACKGROUND JOB TRIGGERS  (run the scheduled email jobs on demand so they
# can be tested manually — the results land in Mailhog: http://localhost:8025)
# ==========================================================================
@admin_bp.route('/jobs/daily-reminders', methods=['POST'])
@jwt_required()
@role_required('admin')
def trigger_daily_reminders():
    from tasks import send_daily_reminders     # local import avoids circular import
    task = send_daily_reminders.delay()
    return jsonify({'task_id': task.id}), 202


@admin_bp.route('/jobs/monthly-report', methods=['POST'])
@jwt_required()
@role_required('admin')
def trigger_monthly_report():
    from tasks import generate_monthly_report
    task = generate_monthly_report.delay()
    return jsonify({'task_id': task.id}), 202


@admin_bp.route('/jobs/<task_id>', methods=['GET'])
@jwt_required()
@role_required('admin')
def job_status(task_id):
    from celery_app import celery
    result = celery.AsyncResult(task_id)
    payload = {'status': result.state}
    if result.state in ('SUCCESS', 'FAILURE'):
        payload['result'] = str(result.result)
    return jsonify(payload), 200
