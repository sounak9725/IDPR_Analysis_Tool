"""
Production startup script for IPDR Analysis Web Dashboard
Includes proper logging, process management, and configuration
"""

import os
import sys
import logging
import signal
import time
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def setup_logging():
    """Setup comprehensive logging for production"""
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / 'production.log'),
            logging.StreamHandler()
        ]
    )
    
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    logging.getLogger('socketio').setLevel(logging.INFO)
    logging.getLogger('engineio').setLevel(logging.INFO)
    
    return logging.getLogger(__name__)

def check_environment():
    """Check production environment requirements"""
    logger = logging.getLogger(__name__)
    
    if sys.version_info < (3, 8):
        logger.error("Python 3.8+ required")
        return False
    
    required_dirs = ['data', 'outputs', 'logs']
    for dir_name in required_dirs:
        if not os.path.exists(dir_name):
            logger.warning(f"Directory {dir_name} does not exist, creating...")
            os.makedirs(dir_name, exist_ok=True)
    
    data_file = 'data/raw/hackathon_ipdr_main.csv'
    if not os.path.exists(data_file):
        logger.warning(f"Data file {data_file} not found")
        logger.info("You may need to run demo_runner.py first to generate sample data")
    
    return True

def start_production_server():
    """Start the production server"""
    logger = logging.getLogger(__name__)
    
    try:
        from src.web.app import create_app
        from config import get_config
        
        config = get_config('production')
        
        config.ensure_directories()
        
        app, socketio = create_app()
        
        app.config.from_object(config)
        
        logger.info("🚀 Starting IPDR Analysis Web Dashboard (Production Mode)")
        logger.info(f"📊 Dashboard will be available at: http://{config.HOST}:{config.PORT}")
        logger.info(f"🔧 Environment: {os.environ.get('FLASK_ENV', 'production')}")
        logger.info(f"📁 Data directory: {config.DATA_DIR}")
        logger.info(f"📁 Output directory: {config.OUTPUT_DIR}")
        logger.info("⏹️  Press Ctrl+C to stop the server")
        logger.info("-" * 50)
        
        socketio.run(
            app, 
            debug=config.DEBUG, 
            host=config.HOST, 
            port=config.PORT,
            log_output=True
        )
        
    except Exception as e:
        logger.error(f"❌ Error starting production server: {e}")
        return False

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    logger = logging.getLogger(__name__)
    logger.info("🛑 Received shutdown signal, shutting down gracefully...")
    
    time.sleep(1)
    sys.exit(0)

def main():
    """Main production startup function"""
    logger = setup_logging()
    
    logger.info("🌐 IPDR Analysis Web Dashboard - Production Startup")
    logger.info("=" * 60)
    
    if not check_environment():
        logger.error("❌ Environment check failed")
        sys.exit(1)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    if not start_production_server():
        logger.error("❌ Failed to start production server")
        sys.exit(1)

if __name__ == "__main__":
    main()
