# Swiss Knife for Women

A responsive web application designed to support women traveling alone by offering safety features, real-time tracking, and emergency tools.

## Features

- **Interactive Safety Map**: Shows user's live location and nearby safety points
- **Emergency Speed Dial Panel**: Quick access to emergency contacts and services
- **Real-Time Location Sharing**: Share location with trusted contacts
- **SOS Alert System**: Trigger emergency alerts with location data
- **Offline Support**: Access critical features without internet
- **AI-Powered Safety Recommendations**: Get safety tips based on location and time

## Tech Stack

- **Frontend**: HTML, CSS, JavaScript, Leaflet.js
- **Backend**: Python (Flask)
- **Database**: SQLite
- **APIs**: OpenStreetMap, Overpass API, Geoapify
- **Other**: WebSockets (for live sharing), MediaRecorder API (for SOS audio)
- **Async**: gevent for asynchronous WebSocket support

## Installation

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set environment variable: `export GEVENT_SUPPORT=True` (for Unix/Linux/Mac) or `set GEVENT_SUPPORT=True` (for Windows)
4. Run the application: `python app.py`
5. Access the application at `http://localhost:5000`

## Project Structure

```
.
├── app.py                  # Main Flask application
├── config.py               # Configuration settings
├── extensions.py           # Flask extensions
├── requirements.txt        # Dependencies
├── static/                 # Static files
│   ├── css/                # Stylesheets
│   ├── js/                 # JavaScript files
│   └── images/             # Image assets
├── templates/              # HTML templates
├── models/                 # Database models
├── routes/                 # API routes
├── services/               # Business logic
└── utils/                  # Helper functions
```

## Environment Variables

- `GEVENT_SUPPORT=True`: Required for gevent monkey-patching support in the debugger
- `FLASK_ENV`: Set to 'development', 'testing', or 'production'
- `SECRET_KEY`: Secret key for session management
- `DATABASE_URL`: Database connection string (defaults to SQLite)
- `EMERGENCY_API_KEY`: API key for emergency services
- `GEOAPIFY_API_KEY`: API key for geolocation services

## This project is created using Amazon Q

