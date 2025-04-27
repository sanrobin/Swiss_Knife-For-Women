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

## Installation

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run the application: `python app.py`
4. Access the application at `http://localhost:5000`

## Project Structure

```
.
├── app.py                  # Main Flask application
├── config.py               # Configuration settings
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

## License

MIT

