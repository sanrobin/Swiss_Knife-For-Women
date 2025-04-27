"""
Location service for handling location-related functionality
"""

import math
import requests
from datetime import datetime, timedelta
from extensions import db
from models.location_history import LocationHistory
from config import active_config

class LocationService:
    """Service for handling location-related functionality"""
    
    @staticmethod
    def calculate_distance(lat1, lon1, lat2, lon2):
        """Calculate distance between two points using Haversine formula"""
        # Earth radius in meters
        R = 6371000
        
        # Convert latitude and longitude from degrees to radians
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        # Differences
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        # Haversine formula
        a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        distance = R * c
        
        return distance
    
    @staticmethod
    def calculate_speed(location1, location2):
        """Calculate speed between two location points"""
        # Calculate distance
        distance = LocationService.calculate_distance(
            location1.latitude, location1.longitude,
            location2.latitude, location2.longitude
        )
        
        # Calculate time difference in seconds
        time_diff = (location2.timestamp - location1.timestamp).total_seconds()
        
        # Avoid division by zero
        if time_diff <= 0:
            return 0
        
        # Calculate speed in m/s
        speed = distance / time_diff
        
        return speed
    
    @staticmethod
    def calculate_heading(lat1, lon1, lat2, lon2):
        """Calculate heading (direction) between two points"""
        # Convert latitude and longitude from degrees to radians
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        # Calculate heading
        y = math.sin(lon2_rad - lon1_rad) * math.cos(lat2_rad)
        x = math.cos(lat1_rad) * math.sin(lat2_rad) - math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(lon2_rad - lon1_rad)
        heading = math.atan2(y, x)
        
        # Convert from radians to degrees
        heading = math.degrees(heading)
        
        # Normalize to 0-360
        heading = (heading + 360) % 360
        
        return heading
    
    @staticmethod
    def clean_old_locations(user_id):
        """Remove old location history entries"""
        # Calculate cutoff date
        cutoff_date = datetime.utcnow() - timedelta(days=active_config.LOCATION_HISTORY_RETENTION_DAYS)
        
        # Delete old entries
        LocationHistory.query.filter_by(user_id=user_id) \
            .filter(LocationHistory.timestamp < cutoff_date).delete()
        
        db.session.commit()
    
    @staticmethod
    def get_nearby_places(latitude, longitude, place_type, radius=1000):
        """Get nearby places using Overpass API"""
        overpass_url = "https://overpass-api.de/api/interpreter"
        
        # Define the Overpass query based on place type
        if place_type == 'police':
            query = f"""
            [out:json];
            node["amenity"="police"](around:{radius},{latitude},{longitude});
            out body;
            """
        elif place_type == 'hospital':
            query = f"""
            [out:json];
            node["amenity"="hospital"](around:{radius},{latitude},{longitude});
            out body;
            """
        elif place_type == 'shelter':
            query = f"""
            [out:json];
            node["social_facility"="shelter"](around:{radius},{latitude},{longitude});
            out body;
            """
        else:
            return []
        
        try:
            response = requests.post(overpass_url, data={"data": query})
            data = response.json()
            
            # Extract relevant information
            places = []
            for element in data.get('elements', []):
                if element.get('type') == 'node':
                    places.append({
                        'id': element.get('id'),
                        'name': element.get('tags', {}).get('name', 'Unknown'),
                        'latitude': element.get('lat'),
                        'longitude': element.get('lon'),
                        'type': place_type,
                        'address': element.get('tags', {}).get('addr:full', ''),
                        'phone': element.get('tags', {}).get('phone', '')
                    })
            
            return places
        
        except Exception as e:
            print(f"Error fetching nearby places: {str(e)}")
            return []
    
    @staticmethod
    def get_country_from_coordinates(latitude, longitude):
        """Get country code from coordinates using Geoapify API"""
        if not active_config.GEOAPIFY_API_KEY:
            return 'US'  # Default to US if no API key
        
        try:
            url = f"https://api.geoapify.com/v1/geocode/reverse?lat={latitude}&lon={longitude}&apiKey={active_config.GEOAPIFY_API_KEY}"
            response = requests.get(url)
            data = response.json()
            
            # Extract country code
            country_code = data.get('features', [{}])[0].get('properties', {}).get('country_code', 'US').upper()
            
            return country_code
        
        except Exception as e:
            print(f"Error getting country from coordinates: {str(e)}")
            return 'US'  # Default to US on error
