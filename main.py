import os
import logging
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from marshmallow import Schema, fields, ValidationError
from werkzeug.exceptions import HTTPException
from functools import wraps
import jwt
from datetime import datetime, timedelta

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your_jwt_secret_key')
app.config['RATE_LIMIT'] = os.getenv('RATE_LIMIT', '100/hour')

# Initialize database
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Logger setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Custom Exception Classes
class CustomException(Exception):
    """Base class for custom exceptions."""
    pass

class NotFoundException(CustomException):
    """Exception raised for not found errors."""
    pass

class ValidationException(CustomException):
    """Exception raised for validation errors."""
    pass

class UnauthorizedException(CustomException):
    """Exception raised for unauthorized access."""
    pass

# Middleware for error handling
@app.errorhandler(CustomException)
def handle_custom_exception(error):
    response = {
        "code": type(error).__name__,
        "message": str(error),
        "details": "An error occurred while processing your request."
    }
    return jsonify(response), 400

@app.errorhandler(HTTPException)
def handle_http_exception(error):
    response = {
        "code": error.name,
        "message": error.description
    }
    return jsonify(response), error.code

# Database Models
class Simulation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class SimulationSchema(Schema):
    id = fields.Int()
    name = fields.Str(required=True)

# Authentication Decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            raise UnauthorizedException("Token is missing.")
        try:
            data = jwt.decode(token, app.config['JWT_SECRET_KEY'], algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            raise UnauthorizedException("Token has expired.")
        except jwt.InvalidTokenError:
            raise UnauthorizedException("Invalid token.")
        return f(*args, **kwargs)
    return decorated

# API Endpoints
@app.route('/api/v1/simulations', methods=['POST'])
@token_required
def create_simulation():
    """Create a new simulation."""
    json_data = request.get_json()
    try:
        simulation_data = SimulationSchema().load(json_data)
    except ValidationError as err:
        raise ValidationException(err.messages)

    simulation = Simulation(name=simulation_data['name'])
    db.session.add(simulation)
    db.session.commit()
    return jsonify(SimulationSchema().dump(simulation)), 201

@app.route('/api/v1/simulations/<int:simulation_id>', methods=['GET'])
@token_required
def get_simulation(simulation_id):
    """Get a simulation by ID."""
    simulation = Simulation.query.get(simulation_id)
    if not simulation:
        raise NotFoundException("Simulation not found.")
    return jsonify(SimulationSchema().dump(simulation)), 200

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy"}), 200

@app.route('/readiness', methods=['GET'])
def readiness_check():
    """Readiness check endpoint."""
    return jsonify({"status": "ready"}), 200

# Main entry point
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)), debug=True)