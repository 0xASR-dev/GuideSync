from flask_jwt_extended import get_jwt
from functools import wraps


# Decorator that blocks a route unless the logged-in user has the given role.
# The role is stored inside the JWT token when the user logs in.
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
