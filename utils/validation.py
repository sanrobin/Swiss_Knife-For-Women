"""
Validation utilities for form validation
"""

import re
from flask import request, jsonify

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone_number(phone_number):
    """Validate phone number format"""
    # Remove common separators
    cleaned = re.sub(r'[\s\-\(\)]', '', phone_number)
    # Check if it's a valid phone number (simple check)
    pattern = r'^[+]?[0-9]{8,15}$'
    return re.match(pattern, cleaned) is not None

def validate_password(password):
    """Validate password strength"""
    # At least 8 characters, 1 uppercase, 1 lowercase, 1 number
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one number"
    
    return True, "Password is valid"

def validate_registration_form(form_data):
    """Validate registration form data"""
    errors = {}
    
    # Required fields
    required_fields = ['username', 'email', 'password']
    for field in required_fields:
        if field not in form_data or not form_data[field]:
            errors[field] = f"{field.capitalize()} is required"
    
    # If required fields are missing, return early
    if errors:
        return False, errors
    
    # Username validation
    if len(form_data['username']) < 3:
        errors['username'] = "Username must be at least 3 characters long"
    
    # Email validation
    if not validate_email(form_data['email']):
        errors['email'] = "Invalid email format"
    
    # Password validation
    is_valid, message = validate_password(form_data['password'])
    if not is_valid:
        errors['password'] = message
    
    # Phone number validation (if provided)
    if 'phone_number' in form_data and form_data['phone_number']:
        if not validate_phone_number(form_data['phone_number']):
            errors['phone_number'] = "Invalid phone number format"
    
    return len(errors) == 0, errors

def validate_contact_form(form_data):
    """Validate emergency contact form data"""
    errors = {}
    
    # Required fields
    required_fields = ['name', 'phone_number']
    for field in required_fields:
        if field not in form_data or not form_data[field]:
            errors[field] = f"{field.capitalize()} is required"
    
    # If required fields are missing, return early
    if errors:
        return False, errors
    
    # Name validation
    if len(form_data['name']) < 2:
        errors['name'] = "Name must be at least 2 characters long"
    
    # Phone number validation
    if not validate_phone_number(form_data['phone_number']):
        errors['phone_number'] = "Invalid phone number format"
    
    # Email validation (if provided)
    if 'email' in form_data and form_data['email']:
        if not validate_email(form_data['email']):
            errors['email'] = "Invalid email format"
    
    return len(errors) == 0, errors

def validate_location_data(location_data):
    """Validate location data"""
    errors = {}
    
    # Required fields
    required_fields = ['latitude', 'longitude']
    for field in required_fields:
        if field not in location_data:
            errors[field] = f"{field.capitalize()} is required"
    
    # If required fields are missing, return early
    if errors:
        return False, errors
    
    # Latitude validation
    try:
        lat = float(location_data['latitude'])
        if lat < -90 or lat > 90:
            errors['latitude'] = "Latitude must be between -90 and 90"
    except (ValueError, TypeError):
        errors['latitude'] = "Latitude must be a valid number"
    
    # Longitude validation
    try:
        lon = float(location_data['longitude'])
        if lon < -180 or lon > 180:
            errors['longitude'] = "Longitude must be between -180 and 180"
    except (ValueError, TypeError):
        errors['longitude'] = "Longitude must be a valid number"
    
    return len(errors) == 0, errors

def json_response(success, message=None, data=None, status_code=200):
    """Generate a standardized JSON response"""
    response = {
        'success': success
    }
    
    if message:
        response['message'] = message
    
    if data:
        response['data'] = data
    
    return jsonify(response), status_code