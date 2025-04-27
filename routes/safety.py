"""
Safety routes for AI-powered safety recommendations
"""

from flask import Blueprint, request, jsonify, session
from datetime import datetime
from app import db
from models.user import User
from models.location_history import LocationHistory
from models.safety_alert import SafetyAlert
from config import active_config

safety_bp = Blueprint('safety', __name__, url_prefix='/safety')

@safety_bp.route('/recommendations', methods=['GET'])
def get_recommendations():
    """Get safety recommendations based on user's location and time"""
    # Check if user is logged in
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    user_id = session['user_id']
    
    # Get location parameters
    latitude = request.args.get('latitude', type=float)
    longitude = request.args.get('longitude', type=float)
    
    # If location not provided, get latest location from database
    if not latitude or not longitude:
        latest_location = LocationHistory.query.filter_by(user_id=user_id) \
            .order_by(LocationHistory.timestamp.desc()).first()
        
        if latest_location:
            latitude = latest_location.latitude
            longitude = latest_location.longitude
    
    # If still no location, return error
    if not latitude or not longitude:
        return jsonify({'error': 'Location not available'}), 400
    
    # Get current time
    current_time = datetime.utcnow()
    current_hour = current_time.hour
    
    # Generate safety recommendations based on time and location
    recommendations = []
    
    # Time-based recommendations
    if current_hour >= active_config.NIGHT_START_HOUR or current_hour < active_config.NIGHT_END_HOUR:
        recommendations.append({
            'type': 'time',
            'severity': 'warning',
            'message': 'It\'s late at night. Stay in well-lit areas and avoid walking alone.'
        })
    
    # Location-based recommendations (simplified for demo)
    # In a real application, we would use crime data or known unsafe zones
    
    # Behavior-based recommendations
    # Get recent locations to calculate movement patterns
    recent_locations = LocationHistory.query.filter_by(user_id=user_id) \
        .order_by(LocationHistory.timestamp.desc()).limit(5).all()
    
    if len(recent_locations) >= 2:
        # Calculate speed between last two locations
        loc1 = recent_locations[0]
        loc2 = recent_locations[1]
        
        if loc1.speed and loc1.speed > 20:  # Speed > 20 m/s (72 km/h)
            recommendations.append({
                'type': 'behavior',
                'severity': 'info',
                'message': 'You appear to be moving quickly. If you\'re in a vehicle, ensure you\'re with a trusted driver.'
            })
    
    # General safety tips
    recommendations.append({
        'type': 'general',
        'severity': 'info',
        'message': 'Share your location with a trusted contact when traveling in unfamiliar areas.'
    })
    
    recommendations.append({
        'type': 'general',
        'severity': 'info',
        'message': 'Keep your phone charged and easily accessible for emergencies.'
    })
    
    return jsonify({'recommendations': recommendations}), 200

@safety_bp.route('/report', methods=['POST'])
def report_safety_issue():
    """Report a safety issue"""
    # Check if user is logged in
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    user_id = session['user_id']
    data = request.json
    
    # Validate report data
    if not data or 'message' not in data:
        return jsonify({'error': 'Message is required'}), 400
    
    # Create safety alert
    alert = SafetyAlert(
        user_id=user_id,
        alert_type=data.get('type', 'user_report'),
        severity=data.get('severity', 'warning'),
        message=data['message'],
        latitude=data.get('latitude'),
        longitude=data.get('longitude')
    )
    
    # Add alert to database
    db.session.add(alert)
    db.session.commit()
    
    return jsonify({'message': 'Safety issue reported successfully', 'alert_id': alert.id}), 201

@safety_bp.route('/safe-areas', methods=['GET'])
def get_safe_areas():
    """Get safe areas near the user's location"""
    # Get location parameters
    latitude = request.args.get('latitude', type=float)
    longitude = request.args.get('longitude', type=float)
    radius = request.args.get('radius', 1000, type=int)  # Default 1km radius
    
    # Validate parameters
    if not latitude or not longitude:
        return jsonify({'error': 'Latitude and longitude are required'}), 400
    
    # In a real application, we would use crime data or known safe zones
    # For now, we'll return some example safe areas
    
    safe_areas = [
        {
            'name': 'Police Station',
            'type': 'police',
            'latitude': latitude + 0.01,
            'longitude': longitude + 0.01,
            'distance': 500  # meters
        },
        {
            'name': 'Hospital',
            'type': 'hospital',
            'latitude': latitude - 0.01,
            'longitude': longitude - 0.01,
            'distance': 800  # meters
        },
        {
            'name': 'Shopping Mall',
            'type': 'public',
            'latitude': latitude + 0.005,
            'longitude': longitude - 0.005,
            'distance': 300  # meters
        }
    ]
    
    return jsonify({'safe_areas': safe_areas}), 200