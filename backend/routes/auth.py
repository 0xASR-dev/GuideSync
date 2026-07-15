from flask import Blueprint, request, jsonify
from extensions import db
from models import User
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

auth_bp = Blueprint('auth', __name__)


# Trekker-registration -------------------------------------------

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}

    email = data.get('email')
    password = data.get('password')
    full_name = data.get('full_name')

    if not email or not password or not full_name:
        return jsonify({'message': 'email, password and full_name are required'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'message': 'Email already registered'}), 400

    user = User(
        email=email,
        password=generate_password_hash(password),
        full_name=full_name,
        phone=data.get('phone', ''),
        role='trekker',
    )
    db.session.add(user)
    db.session.commit()

    return jsonify({'message': 'Registered successfully'}), 201


#login ---------------------------------------------------------------
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    user = User.query.filter_by(email=data.get('email')).first()


    if not user or not check_password_hash(user.password, data.get('password', '')):
        return jsonify({'message': 'Invalid credentials'}), 401

    
    if user.is_blacklisted:
        return jsonify({'message': 'Your account is blacklisted'}), 403

    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={'role': user.role},
    )
    return jsonify({
        'access_token': access_token,
        'role': user.role,
        'full_name': user.full_name,
        'email': user.email,
    }), 200


# ---- Logout ---------------------------------------------------------------

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    return jsonify({'message': 'Logged out'}), 200


# Current user  -------------------------------------------------
@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404
    return jsonify({
        'id': user.id,
        'email': user.email,
        'full_name': user.full_name,
        'phone': user.phone,
        'role': user.role,
    }), 200
