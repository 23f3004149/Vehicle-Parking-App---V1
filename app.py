from flask import Flask, session,render_template
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from models import db, User,Admin
from flask_migrate import Migrate
from flask_cors import CORS
from flask_restful import Api

app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vechile_parking.db'
app.config['SECRET_KEY'] = 'your_secret_key_here'

api = Api(app)
CORS(app)
db.init_app(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    user_type = session.get('user_type')
    if user_type == 'user':
        return User.query.get(int(user_id))
    elif user_type == 'admin':
        return Admin.query.get(int(user_id))
    return None

from controllers.auth import auth_bp
from controllers.admin import admin_bp
from controllers.user import user_bp
from controllers.api import api_bp
app.register_blueprint(api_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(user_bp)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
