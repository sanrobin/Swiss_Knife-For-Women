"""
Location sharing routes for real-time location tracking
"""

from flask import Blueprint, request, jsonify, session, url_for, render_template
import uuid
import secrets
from datetime import datetime, timedelta
from extensions import db
from models.user import User
from models.emergency_contact import EmergencyContact
from models.location_history import LocationHistory

location_bp = Blueprint('location', __name__, url_prefix='/location')

# Dictionary to store active tracking sessions
# Format: {tracking_id: {'user_id': user_id, 'expires_at': datetime}}
active_tracking_sessions = {}

@location_bp.route('/share', methods=['POST'])
def share_location():
    """Create a location sharing session"""
    # Check if user is logged in
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    user_id = session['user_id']
    data = request.json or {}
    
    # Get duration in hours (default: 1 hour)
    duration_hours = data.get('duration', 1)
    
    # Validate duration
    if duration_hours <= 0 or duration_hours > 24:
        return jsonify({'error': 'Duration must be between 1 and 24 hours'}), 400
    
    # Generate tracking ID
    tracking_id = secrets.token_urlsafe(16)
    
    # Set expiration time
    expires_at = datetime.utcnow() + timedelta(hours=duration_hours)
    
    # Store tracking session
    active_tracking_sessions[tracking_id] = {
        'user_id': user_id,
        'expires_at': expires_at
    }
    
    # Generate tracking URL
    tracking_url = url_for('location.track_location', tracking_id=tracking_id, _external=True)
    
    # Get contact IDs to notify
    contact_ids = data.get('contact_ids', [])
    
    # In a real application, we would send the tracking URL to the contacts
    # For now, we'll just return the URL
    
    return jsonify({
        'tracking_id': tracking_id,
        'tracking_url': tracking_url,
        'expires_at': expires_at.isoformat(),
        'contacts_notified': len(contact_ids)
    }), 201

@location_bp.route('/track/<tracking_id>', methods=['GET'])
def track_location(tracking_id):
    """Get tracking page for a specific tracking ID"""
    # Check if tracking ID exists and is valid
    if tracking_id not in active_tracking_sessions:
        return jsonify({'error': 'Invalid tracking ID'}), 404
    
    # Check if tracking session has expired
    if datetime.utcnow() > active_tracking_sessions[tracking_id]['expires_at']:
        # Remove expired session
        active_tracking_sessions.pop(tracking_id)
        return jsonify({'error': 'Tracking session has expired'}), 410
    
    # Return tracking page
    return render_template('location/track.html', tracking_id=tracking_id)

@location_bp.route('/track/<tracking_id>/status', methods=['GET'])
def get_tracking_status(tracking_id):
    """Get status of a tracking session"""
    # Check if tracking ID exists and is valid
    if tracking_id not in active_tracking_sessions:
        return jsonify({'error': 'Invalid tracking ID'}), 404
    
    # Check if tracking session has expired
    if datetime.utcnow() > active_tracking_sessions[tracking_id]['expires_at']:
        # Remove expired session
        active_tracking_sessions.pop(tracking_id)
        return jsonify({'error': 'Tracking session has expired'}), 410
    
    # Get user ID
    user_id = active_tracking_sessions[tracking_id]['user_id']
    
    # Get user
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Get latest location
    latest_location = LocationHistory.query.filter_by(user_id=user_id) \
        .order_by(LocationHistory.timestamp.desc()).first()
    
    # Return tracking status
    return jsonify({
        'tracking_id': tracking_id,
        'user': {
            'first_name': user.first_name,
            'last_name': user.last_name
        },
        'expires_at': active_tracking_sessions[tracking_id]['expires_at'].isoformat(),
        'latest_location': latest_location.to_dict() if latest_location else None
    }), 200

@location_bp.route('/stop-sharing/<tracking_id>', methods=['POST'])
def stop_sharing(tracking_id):
    """Stop a location sharing session"""
    # Check if user is logged in
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    user_id = session['user_id']
    
    # Check if tracking ID exists and is valid
    if tracking_id not in active_tracking_sessions:
        return jsonify({'error': 'Invalid tracking ID'}), 404
    
    # Check if user owns the tracking session
    if active_tracking_sessions[tracking_id]['user_id'] != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Remove tracking session
    active_tracking_sessions.pop(tracking_id)
    
    return jsonify({'message': 'Location sharing stopped successfully'}), 200

@location_bp.route('/active-sessions', methods=['GET'])
def get_active_sessions():
    """Get user's active location sharing sessions"""
    # Check if user is logged in
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    user_id = session['user_id']
    
    # Get current time
    now = datetime.utcnow()
    
    # Filter active sessions for the user
    user_sessions = []
    for tracking_id, session_data in active_tracking_sessions.items():
        if session_data['user_id'] == user_id and session_data['expires_at'] > now:
            user_sessions.append({
                'tracking_id': tracking_id,
                'expires_at': session_data['expires_at'].isoformat(),
                'tracking_url': url_for('location.track_location', tracking_id=tracking_id, _external=True)
            })
    
    return jsonify({'active_sessions': user_sessions}), 200

