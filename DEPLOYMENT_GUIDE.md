# IPDR Analysis System - Deployment Guide

## Overview

This guide provides step-by-step instructions for deploying the IPDR Analysis System to various hosting platforms. The system is designed to work with Flask applications and supports WebSocket connections for real-time features.

## Prerequisites

- GitHub repository with your code
- Python 3.8+ compatibility
- Environment variables configured
- Data files uploaded to the platform

## Platform Recommendations

### 1. Railway (Recommended for Small Teams)

**Best for:** Small teams, easy deployment, free tier available

#### Setup Steps:

1. **Prepare Your Repository:**
   ```bash
   # Ensure these files are in your repo:
   - railway.json (already created)
   - requirements.txt
   - runtime.txt
   ```

2. **Deploy to Railway:**
   - Go to [railway.app](https://railway.app)
   - Sign up with GitHub
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your repository
   - Railway will auto-detect and deploy

3. **Configure Environment Variables:**
   ```bash
   # In Railway dashboard, add these variables:
   SECRET_KEY=your-production-secret-key
   FLASK_ENV=production
   ADMIN_PASSWORD=your-admin-password
   IPDR_API_KEYS=your-api-key-1,your-api-key-2
   ```

4. **Access Your Application:**
   - Railway provides a URL like: `https://your-app-name.railway.app`
   - Your app will be available at this URL

### 2. Render (Alternative Option)

**Best for:** Free tier, easy setup, good documentation

#### Setup Steps:

1. **Prepare Your Repository:**
   ```bash
   # Ensure these files are in your repo:
   - requirements.txt
   - runtime.txt
   ```

2. **Deploy to Render:**
   - Go to [render.com](https://render.com)
   - Sign up with GitHub
   - Click "New" → "Web Service"
   - Connect your GitHub repository

3. **Configure Build Settings:**
   ```
   Build Command: pip install -r requirements.txt
   Start Command: gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:$PORT src.web.app:app
   ```

4. **Set Environment Variables:**
   ```bash
   SECRET_KEY=your-production-secret-key
   FLASK_ENV=production
   ADMIN_PASSWORD=your-admin-password
   IPDR_API_KEYS=your-api-key-1,your-api-key-2
   ```

### 3. Heroku (Traditional Option)

**Best for:** Established platform, good add-ons, scaling options

#### Setup Steps:

1. **Install Heroku CLI:**
   ```bash
   # Download from: https://devcenter.heroku.com/articles/heroku-cli
   ```

2. **Login and Create App:**
   ```bash
   heroku login
   heroku create your-app-name
   ```

3. **Deploy:**
   ```bash
   git add .
   git commit -m "Deploy to Heroku"
   git push heroku main
   ```

4. **Set Environment Variables:**
   ```bash
   heroku config:set SECRET_KEY=your-production-secret-key
   heroku config:set FLASK_ENV=production
   heroku config:set ADMIN_PASSWORD=your-admin-password
   heroku config:set IPDR_API_KEYS=your-api-key-1,your-api-key-2
   ```

## Environment Variables Configuration

### Required Variables:

```bash
# Security
SECRET_KEY=your-production-secret-key-here
ADMIN_PASSWORD=your-admin-password-here

# API Configuration
IPDR_API_KEYS=your-api-key-1,your-api-key-2,your-api-key-3

# Application Settings
FLASK_ENV=production
HOST=0.0.0.0
PORT=5000

# Data Directories
DATA_DIR=/app/data
OUTPUT_DIR=/app/outputs

# Logging
LOG_LEVEL=INFO
```

### Optional Variables:

```bash
# Rate Limiting
IPDR_RATE_LIMIT_PER_MIN=60

# Admin Access
ADMIN_IP_ALLOW=127.0.0.1,::1

# CORS Settings
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

## Data Management

### Uploading Sample Data:

1. **Via Web Interface:**
   - Access your deployed application
   - Use the "Upload Data" feature in the dashboard
   - Upload your IPDR CSV/JSON files

2. **Via API:**
   ```bash
   curl -X POST \
     -H "X-API-Key: your-api-key" \
     -F "file=@your-data.csv" \
     https://your-app-url.com/api/upload-data
   ```

3. **Generate Test Data:**
   - Use the "Generate Data" feature in the web interface
   - Or call the API endpoint for data generation

## Security Considerations

### Production Security:

1. **Strong Passwords:**
   - Use strong, unique passwords for admin access
   - Generate secure API keys

2. **HTTPS:**
   - All recommended platforms provide HTTPS by default
   - Ensure your custom domain uses SSL

3. **Access Control:**
   - Limit admin access to specific IP addresses
   - Regularly rotate API keys

4. **Data Protection:**
   - Ensure sensitive data is not logged
   - Use environment variables for secrets

## Monitoring and Maintenance

### Health Checks:

Your application includes health check endpoints:
- `GET /api/v1/health` - Basic health check
- `GET /api/v1/datasets` - Dataset status

### Logs:

- **Railway:** View logs in the Railway dashboard
- **Render:** Access logs in the Render dashboard
- **Heroku:** Use `heroku logs --tail`

### Performance Monitoring:

- Monitor response times
- Check memory usage
- Watch for error rates

## Troubleshooting

### Common Issues:

1. **Build Failures:**
   - Check Python version compatibility
   - Verify all dependencies in requirements.txt
   - Ensure proper file structure

2. **Runtime Errors:**
   - Check environment variables
   - Verify data file permissions
   - Review application logs

3. **WebSocket Issues:**
   - Ensure platform supports WebSocket connections
   - Check firewall settings
   - Verify eventlet worker configuration

### Support Resources:

- **Railway:** [docs.railway.app](https://docs.railway.app)
- **Render:** [render.com/docs](https://render.com/docs)
- **Heroku:** [devcenter.heroku.com](https://devcenter.heroku.com)

## Cost Considerations

### Free Tiers:

- **Railway:** $5/month after free tier (500 hours)
- **Render:** Free tier available, $7/month for paid plans
- **Heroku:** No free tier, $7/month minimum

### Scaling Costs:

For 5-6 users, the free tiers should be sufficient. Monitor usage and upgrade if needed.

## Custom Domain Setup

### Railway:
1. Go to your project settings
2. Click "Domains"
3. Add your custom domain
4. Update DNS records

### Render:
1. Go to your service settings
2. Click "Custom Domains"
3. Add your domain
4. Configure DNS

### Heroku:
```bash
heroku domains:add yourdomain.com
# Follow DNS configuration instructions
```

## Backup and Recovery

### Data Backup:
- Export important data via the web interface
- Use API endpoints to download datasets
- Regular backups of configuration files

### Recovery Procedures:
1. Redeploy from GitHub repository
2. Restore environment variables
3. Upload data files
4. Verify application functionality

This deployment guide provides comprehensive instructions for hosting your IPDR Analysis System on various platforms suitable for small teams and testing purposes.
