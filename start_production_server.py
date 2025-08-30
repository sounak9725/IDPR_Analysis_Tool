#!/usr/bin/env python3
"""
Production server startup script for Railway deployment
"""

import os
import sys
from src.web.app import create_app

def main():
    """Start the production server"""
    # Get port from environment variable (Railway sets this)
    port = int(os.environ.get('PORT', 5000))
    
    # Create the Flask app
    app, socketio = create_app()
    
    # Configure for production
    app.config['DEBUG'] = False
    app.config['TESTING'] = False
    
    # Start the server
    print(f"Starting IPDR Analysis System on port {port}")
    print(f"Environment: {os.environ.get('FLASK_ENV', 'production')}")
    
    # Use socketio.run for WebSocket support
    socketio.run(
        app,
        host='0.0.0.0',
        port=port,
        debug=False,
        allow_unsafe_werkzeug=True
    )

if __name__ == '__main__':
    main()
