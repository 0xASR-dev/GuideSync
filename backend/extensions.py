from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_caching import Cache

# These are the shared extension objects.
# They are created here (empty) and connected to the app inside create_app().
db = SQLAlchemy()      # database / ORM
jwt = JWTManager()     # JWT login tokens
cache = Cache()        # Redis cache
