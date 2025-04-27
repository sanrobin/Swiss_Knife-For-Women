"""
Emergency routes for the SOS alert system
"""

from flask import Blueprint, request, jsonify, session
import os
import uuid
from datetime import datetime
from app import db
from models.user import User
from models.emergency_contact import EmergencyContact
from models.safety_alert import SafetyAlert
from config import active_config

emergency_bp = Blueprint('emergency', __name__, url_prefix='/emergency')

@emergency_bp.route('/contacts', methods=['GET', 'POST'])
def manage_contacts():
    """Manage emergency contacts"""
    # Check if user is logged in
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    user_id = session['user_id']
    
    if request.method == 'POST':
        # Add new emergency contact
        data = request.json
        
        # Validate contact data
        if not data or 'name' not in data or 'phone_number' not in data:
            return jsonify({'error': 'Name and phone number are required'}), 400
        
        # Check if maximum number of contacts reached
        contact_count = EmergencyContact.query.filter_by(user_id=user_id).count()
        if contact_count >= active_config.MAX_EMERGENCY_CONTACTS:
            return jsonify({'error': f'Maximum number of contacts ({active_config.MAX_EMERGENCY_CONTACTS}) reached'}), 400
        
        # Create new emergency contact
        contact = EmergencyContact(
            user_id=user_id,
            name=data['name'],
            phone_number=data['phone_number'],
            relationship=data.get('relationship'),
            email=data.get('email'),
            is_primary=data.get('is_primary', False),
            notify_on_sos=data.get('notify_on_sos', True),
            notify_on_location_share=data.get('notify_on_location_share', True)
        )
        
        # If this is the first contact or is_primary is True, make it primary
        if contact_count == 0 or contact.is_primary:
            # Reset all other contacts to non-primary
            if contact.is_primary:
                EmergencyContact.query.filter_by(user_id=user_id, is_primary=True).update({'is_primary': False})
            contact.is_primary = True
        
        # Add contact to database
        db.session.add(contact)
        db.session.commit()
        
        return jsonify({'message': 'Contact added successfully', 'contact_id': contact.id}), 201
    
    # GET request - return all contacts
    contacts = EmergencyContact.query.filter_by(user_id=user_id).all()
    contacts_dict = [contact.to_dict() for contact in contacts]
    
    return jsonify({'contacts': contacts_dict}), 200

@emergency_bp.route('/contacts/<int:contact_id>', methods=['GET', 'PUT', 'DELETE'])
def manage_contact(contact_id):
    """Manage a specific emergency contact"""
    # Check if user is logged in
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    user_id = session['user_id']
    
    # Get contact from database
    contact = EmergencyContact.query.filter_by(id=contact_id, user_id=user_id).first()
    
    if not contact:
        return jsonify({'error': 'Contact not found'}), 404
    
    if request.method == 'PUT':
        # Update contact
        data = request.json
        
        if 'name' in data:
            contact.name = data['name']
        
        if 'phone_number' in data:
            contact.phone_number = data['phone_number']
        
        if 'relationship' in data:
            contact.relationship = data['relationship']
        
        if 'email' in data:
            contact.email = data['email']
        
        if 'is_primary' in data and data['is_primary']:
            # Reset all other contacts to non-primary
            EmergencyContact.query.filter_by(user_id=user_id, is_primary=True).update({'is_primary': False})
            contact.is_primary = True
        
        if 'notify_on_sos' in data:
            contact.notify_on_sos = data['notify_on_sos']
        
        if 'notify_on_location_share' in data:
            contact.notify_on_location_share = data['notify_on_location_share']
        
        db.session.commit()
        
        return jsonify({'message': 'Contact updated successfully'}), 200
    
    elif request.method == 'DELETE':
        # Delete contact
        was_primary = contact.is_primary
        
        db.session.delete(contact)
        db.session.commit()
        
        # If the deleted contact was primary, make another contact primary
        if was_primary:
            new_primary = EmergencyContact.query.filter_by(user_id=user_id).first()
            if new_primary:
                new_primary.is_primary = True
                db.session.commit()
        
        return jsonify({'message': 'Contact deleted successfully'}), 200
    
    # GET request - return contact details
    return jsonify(contact.to_dict()), 200

@emergency_bp.route('/sos', methods=['POST'])
def trigger_sos():
    """Trigger SOS alert"""
    # Check if user is logged in
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    user_id = session['user_id']
    data = request.json or {}
    
    # Get user
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Create SOS alert
    alert = SafetyAlert(
        user_id=user_id,
        alert_type='sos',
        severity='danger',
        message='SOS alert triggered',
        latitude=data.get('latitude'),
        longitude=data.get('longitude')
    )
    
    # Handle audio recording if provided
    if 'audio' in request.files:
        audio_file = request.files['audio']
        filename = f"sos_{user_id}_{uuid.uuid4()}.webm"
        filepath = os.path.join('static', 'uploads', 'audio', filename)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Save audio file
        audio_file.save(filepath)
        alert.audio_file_path = filepath
    
    # Add alert to database
    db.session.add(alert)
    db.session.commit()
    
    # Get emergency contacts to notify
    contacts = EmergencyContact.query.filter_by(user_id=user_id, notify_on_sos=True).all()
    
    # In a real application, we would send SMS/email notifications here
    # For now, we'll just mark the alert as notified
    if contacts:
        alert.contacts_notified = True
        db.session.commit()
    
    return jsonify({
        'message': 'SOS alert triggered successfully',
        'alert_id': alert.id,
        'contacts_notified': len(contacts)
    }), 201

@emergency_bp.route('/alerts', methods=['GET'])
def get_alerts():
    """Get user's safety alerts"""
    # Check if user is logged in
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    user_id = session['user_id']
    
    # Get query parameters
    limit = request.args.get('limit', 10, type=int)
    offset = request.args.get('offset', 0, type=int)
    include_resolved = request.args.get('include_resolved', 'false').lower() == 'true'
    
    # Build query
    query = SafetyAlert.query.filter_by(user_id=user_id)
    
    if not include_resolved:
        query = query.filter_by(is_resolved=False)
    
    # Get alerts from database
    alerts = query.order_by(SafetyAlert.created_at.desc()).limit(limit).offset(offset).all()
    
    # Convert to dictionary
    alerts_dict = [alert.to_dict() for alert in alerts]
    
    return jsonify({'alerts': alerts_dict}), 200

@emergency_bp.route('/alerts/<int:alert_id>/resolve', methods=['POST'])
def resolve_alert(alert_id):
    """Resolve a safety alert"""
    # Check if user is logged in
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    user_id = session['user_id']
    
    # Get alert from database
    alert = SafetyAlert.query.filter_by(id=alert_id, user_id=user_id).first()
    
    if not alert:
        return jsonify({'error': 'Alert not found'}), 404
    
    # Resolve alert
    alert.resolve()
    
    return jsonify({'message': 'Alert resolved successfully'}), 200