"""
Safety service for handling safety recommendations
"""

from datetime import datetime
from app import db
from models.safety_alert import SafetyAlert
from models.location_history import LocationHistory
from services.location_service import LocationService
from config import active_config

class SafetyService:
    """Service for handling safety recommendations"""
    
    @staticmethod
    def generate_time_based_recommendations(user_id, current_hour=None):
        """Generate safety recommendations based on time of day"""
        if current_hour is None:
            current_hour = datetime.utcnow().hour
        
        recommendations = []
        
        # Night time recommendations
        if current_hour >= active_config.NIGHT_START_HOUR or current_hour < active_config.NIGHT_END_HOUR:
            recommendations.append({
                'type': 'time',
                'severity': 'warning',
                'message': 'It\'s late at night. Stay in well-lit areas and avoid walking alone.'
            })
            
            recommendations.append({
                'type': 'time',
                'severity': 'info',
                'message': 'Consider using ride-sharing services or taxis instead of walking.'
            })
        
        # Early morning recommendations
        if 5 <= current_hour < 8:
            recommendations.append({
                'type': 'time',
                'severity': 'info',
                'message': 'Good morning! If you\'re out for a morning walk or jog, stick to populated areas.'
            })
        
        # Evening recommendations
        if 17 <= current_hour < 20:
            recommendations.append({
                'type': 'time',
                'severity': 'info',
                'message': 'As it gets darker, be aware of your surroundings and stay in well-lit areas.'
            })
        
        return recommendations
    
    @staticmethod
    def generate_location_based_recommendations(user_id, latitude, longitude):
        """Generate safety recommendations based on location"""
        recommendations = []
        
        # Get nearby safe places
        nearby_police = LocationService.get_nearby_places(latitude, longitude, 'police', radius=2000)
        nearby_hospitals = LocationService.get_nearby_places(latitude, longitude, 'hospital', radius=2000)
        
        # If no police stations nearby
        if not nearby_police:
            recommendations.append({
                'type': 'location',
                'severity': 'warning',
                'message': 'No police stations detected nearby. Stay vigilant and keep your phone charged.'
            })
        else:
            closest_police = min(nearby_police, key=lambda x: x.get('distance', float('inf')))
            recommendations.append({
                'type': 'location',
                'severity': 'info',
                'message': f"Nearest police station: {closest_police.get('name', 'Unknown')} ({int(closest_police.get('distance', 0))} meters away)"
            })
        
        # If no hospitals nearby
        if not nearby_hospitals:
            recommendations.append({
                'type': 'location',
                'severity': 'info',
                'message': 'No hospitals detected nearby. Be extra cautious and avoid risky activities.'
            })
        
        # Check if in isolated area (simplified for demo)
        # In a real application, we would use population density data
        if not nearby_police and not nearby_hospitals:
            recommendations.append({
                'type': 'location',
                'severity': 'warning',
                'message': 'You appear to be in an isolated area. Consider sharing your location with a trusted contact.'
            })
        
        return recommendations
    
    @staticmethod
    def generate_behavior_based_recommendations(user_id):
        """Generate safety recommendations based on user behavior"""
        recommendations = []
        
        # Get recent locations to analyze movement patterns
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
            
            # Check for erratic movement
            if len(recent_locations) >= 3:
                # Calculate heading changes
                heading_changes = []
                for i in range(len(recent_locations) - 2):
                    loc1 = recent_locations[i]
                    loc2 = recent_locations[i + 1]
                    loc3 = recent_locations[i + 2]
                    
                    heading1 = LocationService.calculate_heading(
                        loc1.latitude, loc1.longitude,
                        loc2.latitude, loc2.longitude
                    )
                    
                    heading2 = LocationService.calculate_heading(
                        loc2.latitude, loc2.longitude,
                        loc3.latitude, loc3.longitude
                    )
                    
                    # Calculate absolute heading change
                    heading_change = abs(heading2 - heading1)
                    if heading_change > 180:
                        heading_change = 360 - heading_change
                    
                    heading_changes.append(heading_change)
                
                # If significant heading changes detected
                if any(change > 90 for change in heading_changes):
                    recommendations.append({
                        'type': 'behavior',
                        'severity': 'info',
                        'message': 'Your movement pattern appears erratic. If you\'re lost, consider using the map to find your way.'
                    })
        
        return recommendations
    
    @staticmethod
    def generate_general_recommendations():
        """Generate general safety recommendations"""
        recommendations = [
            {
                'type': 'general',
                'severity': 'info',
                'message': 'Share your location with a trusted contact when traveling in unfamiliar areas.'
            },
            {
                'type': 'general',
                'severity': 'info',
                'message': 'Keep your phone charged and easily accessible for emergencies.'
            },
            {
                'type': 'general',
                'severity': 'info',
                'message': 'Trust your instincts. If a situation feels unsafe, leave immediately.'
            },
            {
                'type': 'general',
                'severity': 'info',
                'message': 'Stay in well-lit, populated areas, especially at night.'
            }
        ]
        
        return recommendations
    
    @staticmethod
    def get_all_recommendations(user_id, latitude=None, longitude=None):
        """Get all safety recommendations for a user"""
        # Get current time
        current_time = datetime.utcnow()
        current_hour = current_time.hour
        
        # Get latest location if not provided
        if latitude is None or longitude is None:
            latest_location = LocationHistory.query.filter_by(user_id=user_id) \
                .order_by(LocationHistory.timestamp.desc()).first()
            
            if latest_location:
                latitude = latest_location.latitude
                longitude = latest_location.longitude
        
        # Generate recommendations
        recommendations = []
        
        # Time-based recommendations
        time_recommendations = SafetyService.generate_time_based_recommendations(user_id, current_hour)
        recommendations.extend(time_recommendations)
        
        # Location-based recommendations (if location available)
        if latitude is not None and longitude is not None:
            location_recommendations = SafetyService.generate_location_based_recommendations(user_id, latitude, longitude)
            recommendations.extend(location_recommendations)
        
        # Behavior-based recommendations
        behavior_recommendations = SafetyService.generate_behavior_based_recommendations(user_id)
        recommendations.extend(behavior_recommendations)
        
        # General recommendations (always include at least one)
        general_recommendations = SafetyService.generate_general_recommendations()
        if not recommendations:
            recommendations.extend(general_recommendations)
        else:
            recommendations.append(general_recommendations[current_hour % len(general_recommendations)])
        
        return recommendations
    
    @staticmethod
    def create_safety_alert(user_id, alert_type, severity, message, latitude=None, longitude=None):
        """Create a safety alert"""
        alert = SafetyAlert(
            user_id=user_id,
            alert_type=alert_type,
            severity=severity,
            message=message,
            latitude=latitude,
            longitude=longitude
        )
        
        db.session.add(alert)
        db.session.commit()
        
        return alert