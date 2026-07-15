import os
from flask import Blueprint, request, jsonify, send_file, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db, cache
from models import Trek, Booking, User, fmt_dt
from routes.utils import role_required
from routes import cache_service

trekker_bp = Blueprint('trekker', __name__)


def _trek_dict(t):
    return {
        'id': t.id,
        'name': t.name,
        'location': t.location,
        'description': t.description,
        'difficulty': t.difficulty,
        'duration_days': t.duration_days,
        'available_slots': t.available_slots,
        'total_slots': t.total_slots,
        'price': t.price,
        'status': t.status,
        'start_date': fmt_dt(t.start_date),
        'end_date': fmt_dt(t.end_date),
    }



@cache.memoize(timeout=60)
def _user_bookings(user_id):
    bookings = Booking.query.filter_by(user_id=user_id).order_by(Booking.id.desc()).all()
    result = []
    for b in bookings:
        trek = Trek.query.get(b.trek_id)
        result.append({
            'id': b.id,
            'trek_name': trek.name if trek else 'Unknown',
            'location': trek.location if trek else '',
            'status': b.status,
            'booking_date': b.booking_date.strftime('%Y-%m-%d') if b.booking_date else '',
            'start_date': fmt_dt(trek.start_date) if trek else '',
        })
    return result


#Dashboard- open treks + my bookings 
@trekker_bp.route('/dashboard', methods=['GET'])
@jwt_required()
@role_required('trekker')
def dashboard():
    user_id = int(get_jwt_identity())
    open_treks = Trek.query.filter_by(status='Open', is_deleted=False).all()
    my_bookings = Booking.query.filter_by(user_id=user_id).count()
    return jsonify({
        'open_treks': [_trek_dict(t) for t in open_treks],
        'my_bookings_count': my_bookings,
    }), 200


# list open treks ------------------------------------------

@trekker_bp.route('/treks', methods=['GET'])
@jwt_required()
@role_required('trekker')
def list_treks():
    difficulty = request.args.get('difficulty')
    location = request.args.get('location')
    duration = request.args.get('duration')

    no_filters = not (difficulty or location or duration)

    
    if no_filters:
        cached = cache_service.get(cache_service.KEY_OPEN_TREKS)
        if cached:
            return jsonify({'treks': cached}), 200

    query = Trek.query.filter_by(status='Open', is_deleted=False)
    if difficulty:
        query = query.filter_by(difficulty=difficulty)
    if location:
        query = query.filter(Trek.location.like(f'%{location}%'))
    if duration:
        query = query.filter_by(duration_days=int(duration))

    treks = [_trek_dict(t) for t in query.all()]

    if no_filters:
        cache_service.set(cache_service.KEY_OPEN_TREKS, treks, timeout=300)

    return jsonify({'treks': treks}), 200


#  Booking a trek  --------------------------
@trekker_bp.route('/bookings', methods=['POST'])
@jwt_required()
@role_required('trekker')
def book_trek():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    
    if not user or user.is_blacklisted:
        return jsonify({'message': 'Your account cannot make bookings'}), 403

    data = request.get_json() or {}
    trek = Trek.query.get(data.get('trek_id'))
    if not trek or trek.is_deleted:
        return jsonify({'message': 'Trek not found'}), 404

    
    if trek.status != 'Open':
        return jsonify({'message': 'This trek is not open for booking'}), 400

    
    if trek.available_slots <= 0:
        return jsonify({'message': 'No slots available'}), 409

    
    existing = Booking.query.filter_by(
        user_id=user_id, trek_id=trek.id, status='Booked'
    ).first()
    if existing:
        return jsonify({'message': 'You already booked this trek'}), 409

    booking = Booking(user_id=user_id, trek_id=trek.id, status='Booked')
    trek.available_slots -= 1
    if trek.available_slots == 0:      
        trek.status = 'Closed'

    db.session.add(booking)
    db.session.commit()

    cache_service.clear_all_trek_caches()
    cache.delete_memoized(_user_bookings, user_id)
    return jsonify({'message': 'Trek booked successfully', 'booking_id': booking.id}), 201


# Cancel a booking 
@trekker_bp.route('/bookings/<int:booking_id>/cancel', methods=['PATCH'])
@jwt_required()
@role_required('trekker')
def cancel_booking(booking_id):
    user_id = int(get_jwt_identity())
    booking = Booking.query.get(booking_id)

    if not booking or booking.user_id != user_id:
        return jsonify({'message': 'Booking not found'}), 404
    if booking.status != 'Booked':
        return jsonify({'message': f'Cannot cancel a {booking.status} booking'}), 400

    booking.status = 'Cancelled'

    trek = Trek.query.get(booking.trek_id)
    if trek:
        trek.available_slots += 1
        
        if trek.status == 'Closed' and trek.available_slots > 0:
            trek.status = 'Open'

    db.session.commit()
    cache_service.clear_all_trek_caches()
    cache.delete_memoized(_user_bookings, user_id)
    return jsonify({'message': 'Booking cancelled'}), 200


# Booking history ------------------------------------------------------
@trekker_bp.route('/bookings', methods=['GET'])
@jwt_required()
@role_required('trekker')
def my_bookings():
    user_id = int(get_jwt_identity())
    return jsonify({'bookings': _user_bookings(user_id)}), 200


#  Edit  profile -----------------------------------------------------
@trekker_bp.route('/profile', methods=['PUT'])
@jwt_required()
@role_required('trekker')
def edit_profile():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    data = request.get_json() or {}
    user.full_name = data.get('full_name', user.full_name)
    user.phone = data.get('phone', user.phone)
    db.session.commit()
    return jsonify({'message': 'Profile updated'}), 200


# CSV EXPORT------------

@trekker_bp.route('/export/bookings', methods=['POST'])
@jwt_required()
@role_required('trekker')
def start_export():
    user_id = int(get_jwt_identity())
    
    from tasks import export_bookings_csv
    task = export_bookings_csv.delay(user_id)
    return jsonify({'task_id': task.id}), 202


@trekker_bp.route('/export/<task_id>', methods=['GET'])
@jwt_required()
@role_required('trekker')
def export_status(task_id):
    from celery_app import celery
    result = celery.AsyncResult(task_id)
    if result.state == 'SUCCESS':
        return jsonify({
            'status': 'SUCCESS',
            'download_url': f'/trekker/export/{task_id}/download',
        }), 200
    if result.state == 'FAILURE':
        return jsonify({'status': 'FAILURE'}), 200
    return jsonify({'status': 'PENDING'}), 200


@trekker_bp.route('/export/<task_id>/download', methods=['GET'])
@jwt_required()
@role_required('trekker')
def export_download(task_id):
    path = os.path.join(current_app.config['EXPORT_FOLDER'], f'{task_id}.csv')
    if not os.path.exists(path):
        return jsonify({'message': 'File not ready'}), 404
    return send_file(path, mimetype='text/csv',
                     as_attachment=True, download_name='my_bookings.csv')
