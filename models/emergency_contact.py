"""
Emergency Contact model for storing user's emergency contacts
"""

from datetime import datetime
from extensions import db

class EmergencyContact(db.Model):
    """Emergency Contact model for storing user's emergency contacts"""
    __tablename__ = 'emergency_contacts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(64), nullable=False)
    relationship = db.Column(db.String(64))
    phone_number = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120))
    is_primary = db.Column(db.Boolean, default=False)
    notify_on_sos = db.Column(db.Boolean, default=True)
    notify_on_location_share = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, user_id, name, phone_number, relationship=None, email=None, 
                 is_primary=False, notify_on_sos=True, notify_on_location_share=True):
        self.user_id = user_id
        self.name = name
        self.phone_number = phone_number
        self.relationship = relationship
        self.email = email
        self.is_primary = is_primary
        self.notify_on_sos = notify_on_sos
        self.notify_on_location_share = notify_on_location_share
    
    def to_dict(self):
        """Convert emergency contact object to dictionary (for API responses)"""
        return {
            'id': self.id,
            'name': self.name,
            'relationship': self.relationship,
            'phone_number': self.phone_number,
            'email': self.email,
            'is_primary': self.is_primary,
            'notify_on_sos': self.notify_on_sos,
            'notify_on_location_share': self.notify_on_location_share
        }
    
    def __repr__(self):
        return f'<EmergencyContact {self.name} for User {self.user_id}>'
