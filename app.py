import os
import logging
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_restx import Api
from flask_login import LoginManager
from datetime import timedelta
from models import User
from storage import storage

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Configure app
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'dev-secret-key')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-session-secret")

# Initialize extensions
jwt = JWTManager(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Por favor, faça login para acessar esta página.'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return storage.get_user_by_id(user_id)

# Initialize API with swagger documentation
authorizations = {
    'Bearer': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization',
        'description': "Type in the *'Value'* input box below: **'Bearer &lt;JWT&gt;'**, where JWT is the token"
    }
}

api = Api(
    app,
    version='1.0',
    title='My Bank API',
    description='API bancária REST com autenticação JWT',
    doc='/docs',
    authorizations=authorizations,
    security='Bearer'
)

# Register blueprints
from views import auth, main
app.register_blueprint(auth)
app.register_blueprint(main)

# Import routes after app initialization to avoid circular imports
from routes import initialize_routes
initialize_routes(api)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)