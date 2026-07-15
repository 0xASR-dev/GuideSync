from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db, cache
from models import Trek, Booking, User
from routes.utils import role_required
from routes import cache_service
from routes.trekker import _user_bookings

tstaff_bp = Blueprint('tstaff', __name__)

STAFF_STATUSES = ['Open', 'Closed', 'Started', 'Completed']



def _get_own_trek(trek_id):
    staff_id = int(get_jwt_identity())
    trek = Trek.query.get(trek_id)
    if not trek:
        return None, (jsonify({'message': 'Trek not found'}), 404)
    if trek.assigned_staff_id != staff_id:
        return None, (jsonify({'message': 'This trek is not assigned to you'}), 403)
    return trek, None


# Dashboard -----------------
@tstaff_bp.route('/dashboard', methods=['GET'])
@jwt_required()
@role_required('staff')
def dashboard():
    staff_id = int(get_jwt_identity())
    treks = Trek.query.filter_by(assigned_staff_id=staff_id, is_deleted=False).all()
    result = []
    for t in treks:
        booked = Booking.query.filter_by(trek_id=t.id, status='Booked').count()
        result.append({
            'id': t.id,
            'name': t.name,
            'status': t.status,
            'available_slots': t.available_slots,
            'total_slots': t.total_slots,
            'booked_count': booked,
        })
    return jsonify({'treks': result}), 200


# List treks ----------------------------------------------
@tstaff_bp.route('/treks', methods=['GET'])
@jwt_required()
@role_required('staff')
def my_treks():
    staff_id = int(get_jwt_identity())
    treks = Trek.query.filter_by(assigned_staff_id=staff_id, is_deleted=False).all()
    result = [{
        'id': t.id,
        'name': t.name,
        'location': t.location,
        'status': t.status,
        'available_slots': t.available_slots,
        'total_slots': t.total_slots,
    } for t in treks]
    return jsonify({'treks': result}), 200


# Update  slots ----------------------------------------------
@tstaff_bp.route('/treks/<int:trek_id>/slots', methods=['PATCH'])
@jwt_required()
@role_required('staff')
def update_slots(trek_id):
    trek, error = _get_own_trek(trek_id)
    if error:
        return error

    data = request.get_json() or {}
    new_available = int(data.get('available_slots', trek.available_slots))

    
    if new_available < 0 or new_available > trek.total_slots:
        return jsonify({'message': 'available_slots must be between 0 and total_slots'}), 400

    trek.available_slots = new_available
    db.session.commit()
    cache_service.clear_all_trek_caches()
    return jsonify({'message': 'Slots updated'}), 200


# change trek status -------------
@tstaff_bp.route('/treks/<int:trek_id>/status', methods=['PATCH'])
@jwt_required()
@role_required('staff')
def update_status(trek_id):
    trek, error = _get_own_trek(trek_id)
    if error:
        return error

    data = request.get_json() or {}
    new_status = data.get('status')
    if new_status not in STAFF_STATUSES:
        return jsonify({'message': 'Invalid status'}), 400

    trek.status = new_status

    
    affected_users = []
    if new_status == 'Completed':
        active = Booking.query.filter_by(trek_id=trek.id, status='Booked').all()
        for b in active:
            b.status = 'Completed'
            affected_users.append(b.user_id)

    db.session.commit()
    cache_service.clear_all_trek_caches()
    for uid in set(affected_users):
        cache.delete_memoized(_user_bookings, uid)
    return jsonify({'message': f'Trek marked {new_status}'}), 200


# Participant list trek---------------------------------------
@tstaff_bp.route('/treks/<int:trek_id>/participants', methods=['GET'])
@jwt_required()
@role_required('staff')
def participants(trek_id):
    trek, error = _get_own_trek(trek_id)
    if error:
        return error

    bookings = Booking.query.filter_by(trek_id=trek.id).all()
    result = []
    for b in bookings:
        user = User.query.get(b.user_id)
        result.append({
            'booking_id': b.id,
            'name': user.full_name if user else 'Unknown',
            'email': user.email if user else '',
            'phone': user.phone if user else '',
            'status': b.status,
        })
    return jsonify({'trek': trek.name, 'participants': result}), 200
