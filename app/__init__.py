from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_wtf import CSRFProtect
from flask_socketio import SocketIO
from datetime import datetime

# -------------------------------
# Initialize extensions
# -------------------------------
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
csrf = CSRFProtect()

# SocketIO → required for real-time notifications
socketio = SocketIO(async_mode="eventlet")  

# -------------------------------
# App factory
# -------------------------------
def create_app(testing: bool = False):
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'supersecretkey'

    if testing:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///task_scheduler.db'

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['DEBUG'] = True

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    socketio.init_app(app)  # <-- attach to Flask app

    # LoginManager settings
    login_manager.login_view = "main.login"
    login_manager.login_message_category = "info"

    # User loader
    from app.models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register blueprints
    from app import routes
    app.register_blueprint(routes.bp)

    # Create DB tables & start scheduler
    from app.scheduler import start_scheduler
    with app.app_context():
        db.create_all()
        if not testing:
            start_scheduler(app, socketio)  # pass socketio too

    # Footer year context
    @app.context_processor
    def inject_now():
        return {'current_year': datetime.utcnow().year}

    return app
