import os
from flask import Flask
from dotenv import load_dotenv


def create_app():
    load_dotenv()

    app = Flask(__name__, instance_relative_config=True)

    # Config
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "change-me")
    app.config["ADMIN_USER"] = os.getenv("ADMIN_USER", "admin")
    app.config["ADMIN_PASS"] = os.getenv("ADMIN_PASS", "change-me")

    # Ensure instance folder exists
    os.makedirs(app.instance_path, exist_ok=True)

    # DB init
    from .db import init_db
    init_db(app)

    # Blueprints
    from .routes import bp as main_bp
    from .admin import bp as admin_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)

    return app
