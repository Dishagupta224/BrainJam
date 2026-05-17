from flask import Flask
from .config import Config
from .extensions import cors, db, migrate
from .common.error_handlers import register_error_handlers


def create_app(config_object: type[Config] | None = None) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_object or Config)

    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})
    db.init_app(app)
    migrate.init_app(app, db)

    register_error_handlers(app)

    # Ensure models are registered for migrations.
    from . import models as _models  # noqa: F401

    from .common.routes import bp as common_bp
    from .auth.routes import bp as auth_bp
    from .users.routes import bp as users_bp
    from .puzzles.routes import bp as puzzles_bp
    from .rooms.routes import bp as rooms_bp
    from .realtime.routes import bp as realtime_bp

    app.register_blueprint(common_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(puzzles_bp)
    app.register_blueprint(rooms_bp)
    app.register_blueprint(realtime_bp)

    # Seed puzzle catalog if DB is ready.
    try:
        with app.app_context():
            from .puzzles.seed import ensure_seed_puzzles

            ensure_seed_puzzles()
    except Exception:
        # Keep startup resilient; seeding should never block the app.
        pass

    return app
