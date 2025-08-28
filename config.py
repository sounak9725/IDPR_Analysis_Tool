#!/usr/bin/env python3
"""
Configuration file for IPDR Analysis Tool
Centralized configuration for all components
"""

import os
from typing import Dict, Any

class Config:
    """Configuration class for IPDR Analysis Tool"""
    
    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY', 'ipdr-hackathon-2024')
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Server Configuration
    HOST = os.environ.get('HOST', '0.0.0.0')
    PORT = int(os.environ.get('PORT', 5000))
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
    # SocketIO Configuration
    SOCKETIO_PING_TIMEOUT = 60
    SOCKETIO_PING_INTERVAL = 25
    SOCKETIO_CORS_ORIGINS = "*"
    
    # Data Configuration
    DATA_DIR = os.environ.get('DATA_DIR', 'data')
    RAW_DATA_DIR = os.path.join(DATA_DIR, 'raw')
    PROCESSED_DATA_DIR = os.path.join(DATA_DIR, 'processed')
    OUTPUT_DIR = os.environ.get('OUTPUT_DIR', 'outputs')
    
    # Default data file
    DEFAULT_DATA_FILE = 'hackathon_ipdr_main.csv'
    
    # Analysis Configuration
    MAX_RECORDS_DISPLAY = 1000
    MAX_NETWORK_NODES = 300
    MAX_NETWORK_EDGES = 10000
    
    # Logging Configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = 'ipdr_analysis.log'
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Security Configuration
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Rate Limiting
    RATELIMIT_ENABLED = os.environ.get('RATELIMIT_ENABLED', 'True').lower() == 'true'
    RATELIMIT_STORAGE_URL = 'memory://'
    
    # External API Configuration
    IP_GEO_API_URL = os.environ.get('IP_GEO_API_URL', 'http://ip-api.com/json/')
    IP_GEO_TIMEOUT = int(os.environ.get('IP_GEO_TIMEOUT', 10))
    
    # Case Management Configuration
    CASE_DATA_DIR = os.path.join(DATA_DIR, 'cases')
    MAX_CASE_EVIDENCE = 1000
    MAX_CASE_SIZE = 50 * 1024 * 1024  # 50MB
    
    # Filtering Configuration
    MAX_FILTERS = 50
    MAX_FILTER_RESULTS = 10000
    
    @classmethod
    def get_data_file_path(cls) -> str:
        """Get the full path to the default data file"""
        return os.path.join(cls.RAW_DATA_DIR, cls.DEFAULT_DATA_FILE)
    
    @classmethod
    def ensure_directories(cls) -> None:
        """Ensure all required directories exist"""
        directories = [
            cls.DATA_DIR,
            cls.RAW_DATA_DIR,
            cls.PROCESSED_DATA_DIR,
            cls.OUTPUT_DIR,
            cls.CASE_DATA_DIR
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    @classmethod
    def to_dict(cls) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            'secret_key': cls.SECRET_KEY,
            'debug': cls.DEBUG,
            'host': cls.HOST,
            'port': cls.PORT,
            'data_dir': cls.DATA_DIR,
            'output_dir': cls.OUTPUT_DIR,
            'log_level': cls.LOG_LEVEL,
            'max_records_display': cls.MAX_RECORDS_DISPLAY,
            'max_network_nodes': cls.MAX_NETWORK_NODES,
            'max_network_edges': cls.MAX_NETWORK_EDGES
        }

# Development configuration
class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'
    SESSION_COOKIE_SECURE = False

# Production configuration
class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    LOG_LEVEL = 'WARNING'
    SESSION_COOKIE_SECURE = True
    RATELIMIT_ENABLED = True

# Testing configuration
class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True
    LOG_LEVEL = 'DEBUG'
    DATA_DIR = 'test_data'
    OUTPUT_DIR = 'test_outputs'

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config(config_name: str = None) -> Config:
    """Get configuration class by name"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')
    
    return config.get(config_name, config['default'])
