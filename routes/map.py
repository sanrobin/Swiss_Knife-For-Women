"""
Map routes for the interactive safety map feature
"""

from flask import Blueprint, request, jsonify, session
import requests
from extensions import db
from models.user import User
from models.location_history import LocationHistory
from config import active_config

map_bp = Blueprint('map', __name__, url_prefix='/map')

@map_bp.route('/save-location', methods=['POST'])
def save_location():
    """Save user's current location to the database"""
    # Check if user is logged in
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    user_id = session['user_id']
    data = request.json
    
    # Validate location data
    if not data or 'latitude' not in data or 'longitude' not in data:
        return jsonify({'error': 'Invalid location data'}), 400
    
    # Create new location history entry
    location = LocationHistory(
        user_id=user_id,
        latitude=data['latitude'],
        longitude=data['longitude'],
        accuracy=data.get('accuracy'),
        altitude=data.get('altitude'),
        speed=data.get('speed'),
        heading=data.get('heading'),
        ip_address=request.remote_addr,
        device_info=request.user_agent.string
    )
    
    # Add location to database
    db.session.add(location)
    db.session.commit()
    
    return jsonify({'message': 'Location saved successfully', 'location_id': location.id}), 201

@map_bp.route('/location-history', methods=['GET'])
def get_location_history():
    """Get user's location history"""
    # Check if user is logged in
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    user_id = session['user_id']
    
    # Get query parameters
    limit = request.args.get('limit', 10, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    # Get location history from database
    locations = LocationHistory.query.filter_by(user_id=user_id) \
        .order_by(LocationHistory.timestamp.desc()) \
        .limit(limit).offset(offset).all()
    
    # Convert to dictionary
    locations_dict = [location.to_dict() for location in locations]
    
    return jsonify({'locations': locations_dict}), 200

@map_bp.route('/nearby-places', methods=['GET'])
def get_nearby_places():
    """Get nearby places (police stations, hospitals, etc.)"""
    # Get query parameters
    latitude = request.args.get('latitude', type=float)
    longitude = request.args.get('longitude', type=float)
    radius = request.args.get('radius', 1000, type=int)  # Default 1km radius
    place_type = request.args.get('type', 'police')  # Default to police stations
    
    # Validate parameters
    if not latitude or not longitude:
        return jsonify({'error': 'Latitude and longitude are required'}), 400
    
    # Use Overpass API to get nearby places
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
        return jsonify({'error': 'Invalid place type'}), 400
    
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
        
        return jsonify({'places': places}), 200
    
    except Exception as e:
        return jsonify({'error': f'Failed to fetch nearby places: {str(e)}'}), 500

@map_bp.route('/emergency-numbers', methods=['GET'])
def get_emergency_numbers():
    """Get emergency numbers based on country code"""
    # Get query parameters
    country_code = request.args.get('country', 'US')  # Default to US
    
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
        'default': {
            'police': '112',
            'ambulance': '112',
            'fire': '112'
        }
    }
    
    # Get emergency numbers for the specified country
    numbers = emergency_numbers.get(country_code, emergency_numbers['default'])
    
    return jsonify({'country': country_code, 'emergency_numbers': numbers}), 200
