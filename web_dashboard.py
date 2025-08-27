#!/usr/bin/env python3
"""
IPDR Analysis Web Dashboard Launcher
Start the interactive web dashboard for IPDR analysis
"""

import os
import sys
import webbrowser
import threading
import time

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def check_web_dependencies():
    """Check if web dependencies are installed"""
    try:
        import flask
        import flask_socketio
        print("✅ Web dependencies found")
        return True
    except ImportError as e:
        print(f"❌ Missing web dependencies: {e}")
        print("Install with: pip install flask flask-socketio")
        return False

def launch_web_dashboard():
    """Launch the web dashboard"""
    try:
        from src.web.app import create_app
        
        app, socketio = create_app()
        
        # Open browser after a short delay
        def open_browser():
            time.sleep(2)
            webbrowser.open('http://localhost:5000')
        
        # Start browser thread
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        print("🚀 Starting IPDR Analysis Web Dashboard...")
        print("📊 Dashboard will open automatically in your browser")
        print("🌐 Access at: http://localhost:5000")
        print("⏹️  Press Ctrl+C to stop the server")
        print("-" * 50)
        
        # Run the Flask app
        socketio.run(app, debug=False, host='0.0.0.0', port=5000)
        
    except Exception as e:
        print(f"❌ Error starting web dashboard: {e}")
        return False

def main():
    """Main function"""
    print("🌐 IPDR Analysis Web Dashboard")
    print("=" * 40)
    
    # Check dependencies
    if not check_web_dependencies():
        return
    
    # Launch dashboard
    launch_web_dashboard()

if __name__ == "__main__":
    main()
