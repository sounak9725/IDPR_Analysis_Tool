"""
Production server startup script for Railway deployment
"""

import os
import sys
from src.web.app import create_app

def main():
    """Start the production server"""
    port = int(os.environ.get('PORT', 5000))
    
    app, socketio = create_app()
    
    app.config['DEBUG'] = False
    app.config['TESTING'] = False
    
    print(f"Starting IPDR Analysis System on port {port}")
    print(f"Environment: {os.environ.get('FLASK_ENV', 'production')}")
    
    socketio.run(
        app,
        host='0.0.0.0',
        port=port,
        debug=False,
        allow_unsafe_werkzeug=True
    )

if __name__ == '__main__':
    main()
