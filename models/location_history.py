"""
Location History model for storing user's location data
"""

from datetime import datetime
from extensions import db

class LocationHistory(db.Model):
    """Location History model for storing user's location data"""
    __tablename__ = 'location_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    accuracy = db.Column(db.Float)  # Accuracy in meters
    altitude = db.Column(db.Float)  # Altitude in meters
    speed = db.Column(db.Float)     # Speed in m/s
    heading = db.Column(db.Float)   # Direction in degrees
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(45))  # IPv4 or IPv6 address
    device_info = db.Column(db.String(255))  # User agent or device identifier
    
    def __init__(self, user_id, latitude, longitude, accuracy=None, altitude=None, 
                 speed=None, heading=None, ip_address=None, device_info=None):
        self.user_id = user_id
        self.latitude = latitude
        self.longitude = longitude
        self.accuracy = accuracy
        self.altitude = altitude
        self.speed = speed
        self.heading = heading
        self.ip_address = ip_address
        self.device_info = device_info
    
    def to_dict(self):
        """Convert location history object to dictionary (for API responses)"""
        return {
            'id': self.id,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'accuracy': self.accuracy,
            'altitude': self.altitude,
            'speed': self.speed,
            'heading': self.heading,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }
    
    def __repr__(self):
        return f'<LocationHistory {self.latitude},{self.longitude} at {self.timestamp}>'
