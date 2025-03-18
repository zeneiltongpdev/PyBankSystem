import os
import logging
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_restx import Api
from datetime import timedelta

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Configure app
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'dev-secret-key')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-session-secret")

# Initialize JWT
jwt = JWTManager(app)

# Initialize API with swagger documentation
api = Api(app, version='1.0', title='Banking API',
          description='A simple banking API with JWT authentication',
          doc='/docs')

# Import routes after app initialization to avoid circular imports
from routes import initialize_routes
initialize_routes(api)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
