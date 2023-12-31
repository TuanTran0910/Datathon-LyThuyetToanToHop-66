from flask import Flask, g
from flask_cors import CORS
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
import os
import shutil
import signal
# init SQLAlchemy so we can use it later in our models
db = SQLAlchemy()


def create_app():
    app = Flask(__name__, template_folder='templates')
    CORS(app)
    # app.config['TESTING'] = True
    # app.config['LOGIN_DISABLED'] = True
    app.config['SECRET_KEY'] = 'secret-key-goes-here'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'

    db.init_app(app)
    from . import models
    with app.app_context():
        db.create_all()

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.get(int(user_id))

    # blueprint for auth routes in our app
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # blueprint for non-auth parts of app
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app


def clear_static_pose_folder(exception=None):
    # Check if an exception occurred during the request
    if exception is None:
        # Clear the contents of the static/pose folder
        clear_folder(os.path.join(os.path.dirname(__file__), 'static', 'pose'))
        # clear_folder(os.path.join(os.path.dirname(__file__), 'try_on'))
        # clear_folder(os.path.join(os.path.dirname(
        #     os.path.dirname(__file__)), 'DM_VTON_new', 'dataset', 'VITON-Clean', 'VITON_test', 'test_img'))

# Helper function to clear the contents of a folder


def clear_folder(folder_path):
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                os.rmdir(file_path)
        except Exception as e:
            print(f"Error clearing {file_path}: {e}")


def signal_handler(signum, frame):
    clear_static_pose_folder()
    print("Cleanup complete. Exiting...")
    exit()


signal.signal(signal.SIGINT, signal_handler)

if __name__ == '__main__':
    app.run(debug=True)
