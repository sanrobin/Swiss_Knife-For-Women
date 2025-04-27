#!/usr/bin/env python3
"""
Swiss Knife for Women - Main Application
A safety app for women traveling alone
"""

import os
from flask import Flask, render_template, request, jsonify, session
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
import json
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(16))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///swiss_knife.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Import models after initializing db
from models.user import User
from models.emergency_contact import EmergencyContact
from models.location_history import LocationHistory
from models.safety_alert import SafetyAlert

# Import routes
from routes.auth import auth_bp
from routes.map import map_bp
from routes.emergency import emergency_bp
from routes.location import location_bp
from routes.safety import safety_bp

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(map_bp)
app.register_blueprint(emergency_bp)
app.register_blueprint(location_bp)
app.register_blueprint(safety_bp)

@app.route('/')
def index():
    """Render the main page of the application"""
    return render_template('index.html')

@app.route('/profile')
def profile():
    """Render the user profile page"""
    return render_template('profile.html')

@app.route('/safety-map')
def safety_map():
    """Render the safety map page"""
    return render_template('safety_map.html')

@app.route('/emergency')
def emergency():
    """Render the emergency page"""
    return render_template('emergency.html')

@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors"""
    return render_template('500.html'), 500

# WebSocket event handlers
@socketio.on('connect')
def handle_connect():
    """Handle client connection to WebSocket"""
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection from WebSocket"""
    print('Client disconnected')

@socketio.on('join_tracking')
def handle_join_tracking(data):
    """Handle joining a tracking room"""
    room = data['tracking_id']
    join_room(room)
    emit('tracking_joined', {'status': 'success'}, room=room)

@socketio.on('location_update')
def handle_location_update(data):
    """Handle location updates from clients"""
    room = data['tracking_id']
    emit('location_updated', {
        'latitude': data['latitude'],
        'longitude': data['longitude'],
        'timestamp': datetime.now().isoformat()
    }, room=room)

# Create database tables
@app.before_first_request
def create_tables():
    """Create database tables before first request"""
    db.create_all()

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)