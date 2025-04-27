"""
Configuration settings for the Swiss Knife for Women application
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

class Config:
    """Base configuration class"""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-for-development-only')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///swiss_knife.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Emergency services API configuration
    EMERGENCY_API_KEY = os.environ.get('EMERGENCY_API_KEY', '')
    
    # Geolocation API configuration
    GEOAPIFY_API_KEY = os.environ.get('GEOAPIFY_API_KEY', '')
    
    # Application settings
    MAX_EMERGENCY_CONTACTS = 5
    LOCATION_HISTORY_RETENTION_DAYS = 7
    SOS_AUDIO_MAX_DURATION_SECONDS = 30
    
    # Safety thresholds
    NIGHT_START_HOUR = 22  # 10 PM
    NIGHT_END_HOUR = 6     # 6 AM
    ISOLATED_AREA_THRESHOLD_METERS = 500  # Distance from populated areas

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    
    # In production, ensure these are set in environment variables
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

# Set the active configuration based on environment
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

active_config = config[os.environ.get('FLASK_ENV', 'default')]