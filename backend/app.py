from flask import Flask, jsonify
from config import config
from extensions import db, jwt, cache
from models import create_admin
from flask_cors import CORS


def create_app():
    app = Flask(__name__)
    app.config.from_object(config)
    CORS(app)   # allow the Vue frontend to call the API

    # connect the extensions to the app
    db.init_app(app)
    jwt.init_app(app)
    cache.init_app(app)

    # create tables + seed the single admin
    with app.app_context():
        db.create_all()
        create_admin()

    # register all route blueprints
    from routes.auth import auth_bp
    from routes.admin import admin_bp
    from routes.trekker import trekker_bp
    from routes.tstaff import tstaff_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(trekker_bp, url_prefix='/trekker')
    app.register_blueprint(tstaff_bp, url_prefix='/tstaff')

    return app


app = create_app()


@app.route('/')
def home():
    return jsonify({'message': 'Welcome to the GuideSync Trekking Management API'}), 200


@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy'}), 200


if __name__ == '__main__':
    app.run(debug=True)
