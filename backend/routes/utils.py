from flask_jwt_extended import get_jwt
from functools import wraps



def role_required(role):
    def wrapper(fn):
        @wraps(fn)
        def decorated(*args, **kwargs):
            claims = get_jwt()
            if claims.get('role') != role:
                return {'message': 'Access denied'}, 403
            return fn(*args, **kwargs)
        return decorated
    return wrapper
