"""
IPDR Analysis Web Dashboard Launcher
Start the interactive web dashboard for IPDR analysis
"""

import os
import sys
import webbrowser
import threading
import time
import argparse
import signal
import socket

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def check_port_available(port):
    """Check if a port is available"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', port))
            return True
    except OSError:
        return False

def find_available_port(start_port=5000):
    """Find an available port starting from start_port"""
    port = start_port
    while port < start_port + 100:
        if check_port_available(port):
            return port
        port += 1
    return None

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

def launch_web_dashboard(port=5000, host='0.0.0.0', debug=False, auto_browser=True):
    """Launch the web dashboard"""
    try:
        from src.web.app import create_app
        
        app, socketio = create_app()
        
        if auto_browser:
            def open_browser():
                time.sleep(2)
                try:
                    webbrowser.open(f'http://localhost:{port}')
                except Exception as e:
                    print(f"⚠️  Could not open browser automatically: {e}")
                    print(f"🌐 Please open manually: http://localhost:{port}")
            
            browser_thread = threading.Thread(target=open_browser)
            browser_thread.daemon = True
            browser_thread.start()
        
        print("🚀 Starting IPDR Analysis Web Dashboard...")
        print(f"📊 Dashboard will be available at: http://localhost:{port}")
        if auto_browser:
            print("🌐 Browser will open automatically")
        print("⏹️  Press Ctrl+C to stop the server")
        print("-" * 50)
        
        socketio.run(app, debug=debug, host=host, port=port)
        
    except Exception as e:
        print(f"❌ Error starting web dashboard: {e}")
        return False

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    print("\n🛑 Shutting down web dashboard...")
    sys.exit(0)

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='IPDR Analysis Web Dashboard')
    parser.add_argument('--port', type=int, default=5000, help='Port to run on (default: 5000)')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to (default: 0.0.0.0)')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--no-browser', action='store_true', help='Do not open browser automatically')
    parser.add_argument('--auto-port', action='store_true', help='Automatically find available port')
    
    args = parser.parse_args()
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("🌐 IPDR Analysis Web Dashboard")
    print("=" * 40)
    
    if not check_web_dependencies():
        return
    
    port = args.port
    if args.auto_port:
        available_port = find_available_port(port)
        if available_port:
            port = available_port
            print(f"🔍 Found available port: {port}")
        else:
            print(f"❌ No available ports found starting from {port}")
            return
    
    if not check_port_available(port):
        print(f"❌ Port {port} is already in use")
        if not args.auto_port:
            print("💡 Use --auto-port to find an available port automatically")
        return
    
    # launching the dashboard
    launch_web_dashboard(
        port=port,
        host=args.host,
        debug=args.debug,
        auto_browser=not args.no_browser
    )

if __name__ == "__main__":
    main()
