"""
Emergency service for handling SOS alerts and emergency contacts
"""

import os
import uuid
from datetime import datetime
from extensions import db
from models.emergency_contact import EmergencyContact
from models.safety_alert import SafetyAlert
from models.location_history import LocationHistory
from services.location_service import LocationService
from config import active_config

class EmergencyService:
    """Service for handling emergency situations"""
    
    @staticmethod
    def get_emergency_contacts(user_id, notify_on_sos=None):
        """Get emergency contacts for a user"""
        query = EmergencyContact.query.filter_by(user_id=user_id)
        
        if notify_on_sos is not None:
            query = query.filter_by(notify_on_sos=notify_on_sos)
        
        contacts = query.order_by(EmergencyContact.is_primary.desc()).all()
        return contacts
    
    @staticmethod
    def get_primary_contact(user_id):
        """Get primary emergency contact for a user"""
        return EmergencyContact.query.filter_by(user_id=user_id, is_primary=True).first()
    
    @staticmethod
    def create_sos_alert(user_id, latitude=None, longitude=None, message=None, audio_file=None):
        """Create an SOS alert"""
        # Get latest location if not provided
        if latitude is None or longitude is None:
            latest_location = LocationHistory.query.filter_by(user_id=user_id) \
                .order_by(LocationHistory.timestamp.desc()).first()
            
            if latest_location:
                latitude = latest_location.latitude
                longitude = latest_location.longitude
        
        # Create default message if not provided
        if not message:
            message = "SOS alert triggered. User may be in danger."
        
        # Create alert
        alert = SafetyAlert(
            user_id=user_id,
            alert_type='sos',
            severity='danger',
            message=message,
            latitude=latitude,
            longitude=longitude
        )
        
        # Handle audio recording if provided
        if audio_file:
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
        contacts = EmergencyService.get_emergency_contacts(user_id, notify_on_sos=True)
        
        # In a real application, we would send SMS/email notifications here
        # For now, we'll just mark the alert as notified
        if contacts:
            alert.contacts_notified = True
            db.session.commit()
        
        return alert, contacts
    
    @staticmethod
    def get_emergency_numbers(country_code='US'):
        """Get emergency numbers for a country"""
        # Define emergency numbers for common countries
        emergency_numbers = {
            'US': {
                'police': '911',
                'ambulance': '911',
                'fire': '911'
            },
            'UK': {
                'police': '999',
                'ambulance': '999',
                'fire': '999'
            },
            'AU': {
                'police': '000',
                'ambulance': '000',
                'fire': '000'
            },
            'IN': {
                'police': '100',
                'ambulance': '108',
                'fire': '101',
                'women_helpline': '1091'
            },
            'CA': {
                'police': '911',
                'ambulance': '911',
                'fire': '911'
            },
            'NZ': {
                'police': '111',
                'ambulance': '111',
                'fire': '111'
            },
            'default': {
                'police': '112',
                'ambulance': '112',
                'fire': '112'
            }
        }
        
        # Get emergency numbers for the specified country
        return emergency_numbers.get(country_code, emergency_numbers['default'])
    
    @staticmethod
    def get_women_specific_helplines(country_code='US'):
        """Get women-specific helplines for a country"""
        # Define women-specific helplines for common countries
        women_helplines = {
            'US': {
                'domestic_violence': '1-800-799-7233',
                'sexual_assault': '1-800-656-4673'
            },
            'UK': {
                'domestic_violence': '0808 2000 247',
                'sexual_assault': '0808 802 9999'
            },
            'IN': {
                'women_helpline': '1091',
                'domestic_violence': '181'
            },
            'AU': {
                'domestic_violence': '1800 737 732',
                'sexual_assault': '1800 737 732'
            },
            'CA': {
                'domestic_violence': '1-800-363-9010',
                'sexual_assault': '1-888-933-9007'
            },
            'default': {}
        }
        
        # Get women-specific helplines for the specified country
        return women_helplines.get(country_code, women_helplines.get('default', {}))
    
    @staticmethod
    def resolve_alert(alert_id, user_id):
        """Resolve a safety alert"""
        alert = SafetyAlert.query.filter_by(id=alert_id, user_id=user_id).first()
        
        if alert:
            alert.resolve()
            return True
        
        return False
