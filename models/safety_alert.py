"""
Safety Alert model for storing safety alerts and recommendations
"""

from datetime import datetime
from extensions import db

class SafetyAlert(db.Model):
    """Safety Alert model for storing safety alerts and recommendations"""
    __tablename__ = 'safety_alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    alert_type = db.Column(db.String(50), nullable=False)  # 'sos', 'time', 'location', 'behavior'
    severity = db.Column(db.String(20), nullable=False)    # 'info', 'warning', 'danger'
    message = db.Column(db.Text, nullable=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    is_resolved = db.Column(db.Boolean, default=False)
    resolved_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # For SOS alerts
    audio_file_path = db.Column(db.String(255))
    contacts_notified = db.Column(db.Boolean, default=False)
    
    def __init__(self, user_id, alert_type, severity, message, latitude=None, longitude=None, 
                 audio_file_path=None, contacts_notified=False):
        self.user_id = user_id
        self.alert_type = alert_type
        self.severity = severity
        self.message = message
        self.latitude = latitude
        self.longitude = longitude
        self.audio_file_path = audio_file_path
        self.contacts_notified = contacts_notified
    
    def resolve(self):
        """Mark the alert as resolved"""
        self.is_resolved = True
        self.resolved_at = datetime.utcnow()
        db.session.commit()
    
    def to_dict(self):
        """Convert safety alert object to dictionary (for API responses)"""
        return {
            'id': self.id,
            'alert_type': self.alert_type,
            'severity': self.severity,
            'message': self.message,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'is_resolved': self.is_resolved,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'contacts_notified': self.contacts_notified
        }
    
    def __repr__(self):
        return f'<SafetyAlert {self.alert_type} ({self.severity}) at {self.created_at}>'
