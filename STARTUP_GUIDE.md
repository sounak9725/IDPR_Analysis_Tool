# 🚀 IPDR Analysis Tool - Startup Guide

This guide covers different ways to start and deploy the IPDR Analysis Tool.

## 🏃‍♂️ Quick Start (Development)

### 1. Basic Web Dashboard
```bash
# Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Start web dashboard
python web_dashboard.py
```

### 2. Web Dashboard with Options
```bash
# Start on different port
python web_dashboard.py --port 8080

# Start without auto-browser
python web_dashboard.py --no-browser

# Auto-find available port
python web_dashboard.py --auto-port

# Enable debug mode
python web_dashboard.py --debug
```

## 🏭 Production Deployment

### 1. Production Server
```bash
# Set production environment
set FLASK_ENV=production  # Windows
export FLASK_ENV=production  # Linux/Mac

# Start production server
python start_production.py
```

### 2. Docker Deployment
```bash
# Build and run with Docker
docker build -t ipdr-analysis .
docker run -p 5000:5000 ipdr-analysis

# Or use Docker Compose
docker-compose up -d
```

### 3. Environment Variables
```bash
# Production configuration
set SECRET_KEY=your-secure-secret-key
set FLASK_DEBUG=False
set LOG_LEVEL=WARNING
set HOST=0.0.0.0
set PORT=5000
```

## 🔧 Configuration Options

### 1. Configuration File
The tool uses `config.py` for centralized configuration:
- **Development**: Debug mode, detailed logging
- **Production**: Optimized for performance and security
- **Testing**: Isolated environment for testing

### 2. Environment Variables
```bash
# Flask Configuration
FLASK_ENV=production
SECRET_KEY=your-secret-key
FLASK_DEBUG=False

# Server Configuration
HOST=0.0.0.0
PORT=5000

# Data Configuration
DATA_DIR=data
OUTPUT_DIR=outputs

# Logging
LOG_LEVEL=INFO
```

## 📊 Health Monitoring

### 1. Health Check Endpoint
```bash
# Check if service is running
curl http://localhost:5000/health

# Get detailed status
curl http://localhost:5000/status
```

### 2. Log Files
- **Web Dashboard**: `web_dashboard.log`
- **Production**: `logs/production.log`
- **Application**: `ipdr_analysis.log`

## 🐳 Docker Commands

### 1. Build and Run
```bash
# Build image
docker build -t ipdr-analysis .

# Run container
docker run -d -p 5000:5000 --name ipdr-dashboard ipdr-analysis

# View logs
docker logs ipdr-dashboard

# Stop container
docker stop ipdr-dashboard
```

### 2. Docker Compose
```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild and restart
docker-compose up -d --build
```

## 🔒 Security Considerations

### 1. Production Security
- Change default `SECRET_KEY`
- Use HTTPS in production
- Enable rate limiting
- Set secure cookie options
- Use non-root user in Docker

### 2. Network Security
- Bind to specific interfaces if needed
- Use firewall rules
- Consider reverse proxy (nginx)
- Enable CORS appropriately

## 📈 Performance Optimization

### 1. Server Settings
- Use production WSGI server (gunicorn)
- Enable worker processes
- Configure proper timeouts
- Use Redis for session storage

### 2. Data Handling
- Limit result sizes
- Implement pagination
- Use database indexing
- Cache frequently accessed data

## 🚨 Troubleshooting

### 1. Common Issues
```bash
# Port already in use
python web_dashboard.py --auto-port

# Missing dependencies
pip install -r requirements.txt

# Permission issues (Docker)
docker run --user root -p 5000:5000 ipdr-analysis

# Data file not found
python demo_runner.py  # Generate sample data first
```

### 2. Debug Mode
```bash
# Enable debug logging
set LOG_LEVEL=DEBUG
python web_dashboard.py --debug

# Check logs
tail -f web_dashboard.log
```

## 📚 Additional Resources

- **README.md**: Complete project documentation
- **config.py**: Configuration options
- **requirements.txt**: Python dependencies
- **Dockerfile**: Container configuration
- **docker-compose.yml**: Multi-service setup

## 🎯 Next Steps

1. **Customize Configuration**: Modify `config.py` for your environment
2. **Add Authentication**: Implement user login system
3. **Database Integration**: Connect to external databases
4. **API Documentation**: Generate OpenAPI/Swagger docs
5. **Monitoring**: Add Prometheus metrics and Grafana dashboards
6. **CI/CD**: Set up automated testing and deployment

---

**Need Help?** Check the logs and health endpoints for troubleshooting information.
