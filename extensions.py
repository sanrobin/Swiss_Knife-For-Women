"""
Extensions for the Swiss Knife for Women application
This file contains Flask extensions that can be imported by other modules
"""

import os

# Ensure gevent support is enabled
if os.environ.get('GEVENT_SUPPORT') != 'True':
    os.environ['GEVENT_SUPPORT'] = 'True'

from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO

# Initialize extensions without binding to an app
db = SQLAlchemy()
socketio = SocketIO(async_mode='gevent')  # Explicitly set async_mode to gevent
