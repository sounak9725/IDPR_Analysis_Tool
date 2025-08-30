# IPDR Analysis System

A comprehensive digital forensics and telecommunications analysis platform designed to process, analyze, and visualize communication data between parties. The system provides both programmatic API access and an interactive web interface for investigators, law enforcement, and security analysts.

## System Overview

The IPDR (Internet Protocol Detail Record) Analysis System processes telecommunications metadata to identify patterns, relationships, and anomalies in communication networks. It analyzes communication records between Party A (initiator) and Party B (recipient) to provide insights for criminal investigations, fraud detection, network security, and compliance monitoring.

## Core Features

- **Multi-format IPDR parsing** (CSV, JSON, TXT)
- **Network analysis** with relationship mapping and force-directed graphs
- **Suspicious activity detection** using advanced pattern recognition algorithms
- **Interactive entity search** and investigation tools with timeline analysis
- **Advanced visualizations** with interactive charts and network graphs
- **Synthetic data generation** for testing and development
- **Interactive Web Dashboard** with real-time analysis capabilities
- **Enhanced Search & Investigation** tools for comprehensive analysis
- **Pattern Analysis** with anomaly detection and behavioral insights
- **Network Visualization** with interactive D3.js force-directed graphs
- **Real-time Communication** using Flask-SocketIO

## Web Dashboard Features

### Dashboard Overview
- **Real-time Statistics**: Live overview of IPDR data with key metrics
- **Interactive Charts**: Time-based communication patterns using Chart.js
- **Suspicious Activity Monitor**: Real-time detection and display of suspicious patterns
- **Communication Insights**: Top communicators and service type distribution

### Enhanced Investigation Tools
- **Advanced Entity Search**: Search by phone number, service type, or time range
- **Activity Timeline**: Visual timeline of entity communications
- **Communication Partners**: Top contacts and relationship strength analysis
- **Pattern Analysis**: Communication behavior and suspicious indicators
- **Export Capabilities**: Download investigation results in multiple formats
- **Search History**: Track previous searches and investigations

### Network Analysis
- **Interactive Network Graph**: D3.js force-directed graph visualization
- **Node Controls**: Adjustable display parameters (max nodes, layout, node size)
- **Network Statistics**: Degree distribution and connection analysis
- **Top Connected Nodes**: Identify key network hubs and influencers
- **Network Insights**: Automated analysis of network structure and anomalies

### Pattern Analysis
- **Time-based Patterns**: Hourly and daily communication trends
- **Service Distribution**: Analysis of different communication types
- **Duration Patterns**: Call length and communication duration insights
- **Behavioral Analysis**: Entity behavior patterns and anomalies
- **Anomaly Detection**: Automated identification of unusual activities

## Project Structure

```
ipdr_hackathon/
├── src/                          # Source code
│   ├── core/                     # Core analysis components
│   │   ├── __init__.py
│   │   └── ipdr_analyzer.py      # Main analysis engine
│   ├── utils/                    # Utility functions
│   │   ├── __init__.py
│   │   └── synthetic_ipdr_generator.py  # Data generation
│   ├── visualization/            # Visualization components
│   │   └── __init__.py
│   └── web/                      # Web dashboard components
│       ├── __init__.py
│       ├── app.py                # Flask application
│       └── templates/            # HTML templates
│           ├── base.html         # Base template with common elements
│           ├── dashboard.html    # Main dashboard page
│           ├── investigation.html # Enhanced investigation tools
│           ├── network.html      # Network visualization
│           └── patterns.html     # Pattern analysis
├── data/                         # Data files
│   ├── raw/                      # Raw input data
│   ├── processed/                # Processed data
│   └── sample/                   # Sample datasets
├── outputs/                      # Analysis outputs
│   ├── analysis/                 # Analysis results
│   └── visualizations/           # Generated plots
├── tests/                        # Test files
├── docs/                         # Documentation
├── examples/                     # Example scripts
├── demo_runner.py               # Main demo script
├── web_dashboard.py             # Web dashboard launcher
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## Installation

1. **Clone or download the project**
2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Install web dashboard dependencies:**
   ```bash
   pip install flask flask-socketio
   ```

## Quick Start

### Option 1: Web Dashboard (Recommended)
Launch the interactive web dashboard:
```bash
python web_dashboard.py
```

This will:
- Start a web server on http://localhost:5000
- Open the dashboard automatically in your browser
- Provide interactive visualizations and search
- Enable real-time analysis and investigation
- Offer enhanced search and investigation tools
- Display interactive network visualizations
- Show pattern analysis and anomaly detection

### Option 2: Command Line Demo
Run the complete demo:
```bash
python demo_runner.py
```

This will:
- Check dependencies
- Generate sample data (if needed)
- Run comprehensive IPDR analysis
- Detect suspicious activities
- Generate visualizations
- Provide interactive search capabilities

## How to Use the Web Dashboard

### 1. Dashboard Overview
- **Launch**: Run `python web_dashboard.py`
- **Navigate**: Use the navigation bar to switch between different analysis views
- **Real-time Data**: View live statistics and communication patterns

### 2. Enhanced Investigation
- **Search**: Use the search bar to find specific entities
- **Timeline**: View communication activity over time
- **Patterns**: Analyze communication behavior and suspicious indicators
- **Export**: Download investigation results for further analysis

### 3. Network Analysis
- **Interactive Graph**: Explore network relationships with zoom and drag
- **Controls**: Adjust display parameters for optimal visualization
- **Insights**: View automated network analysis and key node identification

### 4. Pattern Analysis
- **Charts**: Interactive charts for time patterns and service distribution
- **Anomalies**: Automated detection of unusual communication patterns
- **Behavioral Insights**: Analysis of entity communication behavior

## Analysis Capabilities

### Core Analysis
- **Communication Pattern Analysis**: Identify peak hours, busy entities, and communication trends
- **Network Relationship Mapping**: Build and analyze communication networks with interactive visualization
- **Suspicious Activity Detection**: Detect unusual patterns like:
  - High-frequency calling
  - Burner phone patterns
  - Criminal network clustering
  - Automated bot behavior
  - Unusual time patterns
  - Service type anomalies

### Advanced Visualization
- **Interactive Network Graphs**: D3.js force-directed network visualizations
- **Real-time Charts**: Chart.js powered interactive charts
- **Communication Heatmaps**: Time-based activity patterns
- **Entity Relationship Charts**: Connection strength analysis
- **Pattern Analysis Charts**: Behavioral and anomaly visualization

### Enhanced Search & Investigation
- **Multi-criteria Search**: Search by phone number, service type, time range, or duration
- **Pattern Matching**: Identify similar communication patterns across entities
- **Timeline Analysis**: Track entity activity over time with visual representation
- **Relationship Mapping**: Visualize entity connections and communication networks
- **Anomaly Detection**: Automated identification of suspicious patterns
- **Export Functionality**: Download investigation results in multiple formats

## Usage Examples

### Basic Analysis
```python
from src.core.ipdr_analyzer import IPDRAnalyzer

analyzer = IPDRAnalyzer()
analyzer.parse_ipdr_file('data/raw/your_data.csv')
analyzer.extract_relationships()
patterns = analyzer.analyze_communication_patterns()
```

### Entity Search
```python
results = analyzer.search_entity('919876543210')
print(f"Total communications: {results['total_communications']}")
```

### Generate Visualizations
```python
analyzer.generate_network_visualization('outputs/visualizations/network.png')
```

### Web Dashboard API
```python
# The web dashboard provides RESTful API endpoints:
# GET /api/overview - Get overview statistics
# GET /api/search?entity=919876543210 - Search for specific entity
# GET /api/suspicious - Get suspicious activities
# GET /api/network - Get network graph data
# GET /api/patterns - Get communication patterns
```

## Key Features for Presentation

### 1. Interactive Web Interface
- **Modern UI**: Bootstrap-based responsive design
- **Real-time Updates**: Live data refresh and analysis
- **Interactive Charts**: Zoom, pan, and hover interactions
- **Mobile Responsive**: Works on all device sizes

### 2. Advanced Analytics
- **Pattern Recognition**: Automated detection of communication patterns
- **Anomaly Detection**: Identification of suspicious activities
- **Network Analysis**: Relationship mapping and clustering
- **Behavioral Analysis**: Entity communication behavior insights

### 3. Investigation Tools
- **Enhanced Search**: Multi-criteria entity search
- **Timeline Analysis**: Visual activity tracking
- **Export Capabilities**: Download results for further analysis
- **Search History**: Track investigation progress

### 4. Visualization Capabilities
- **Network Graphs**: Interactive D3.js force-directed graphs
- **Statistical Charts**: Chart.js powered analytics
- **Real-time Updates**: Live data visualization
- **Customizable Views**: Adjustable display parameters

## Output Files

The tool generates several output files:
- `outputs/analysis/complete_analysis.json` - Detailed analysis results
- `outputs/visualizations/network_analysis.png` - Network visualization
- Various data files in the `data/` directory
- Web dashboard accessible at http://localhost:5000

## Testing

Run tests (when implemented):
```bash
python -m pytest tests/
```

## Data Formats

The tool supports multiple IPDR formats:

### CSV Format
```csv
timestamp,a_party,b_party,duration,service_type
2024-01-15 10:30:15,919876543210,918765432109,120,VOICE
```

### JSON Format
```json
[
  {
    "timestamp": "2024-01-15T10:30:15",
    "a_party": "919876543210",
    "b_party": "918765432109",
    "duration": 120,
    "service_type": "VOICE"
  }
]
```

### Text Format
```
2024-01-15 10:30:15|919876543210|918765432109|120|VOICE
```

## How to Present the Project

### 1. Start with the Web Dashboard
```bash
python web_dashboard.py
```
- Show the interactive interface
- Demonstrate real-time data loading
- Highlight the modern, professional UI

### 2. Demonstrate Key Features
- **Dashboard Overview**: Show statistics and communication patterns
- **Enhanced Search**: Search for specific entities and show results
- **Network Analysis**: Display interactive network visualizations
- **Pattern Analysis**: Show anomaly detection and behavioral insights

### 3. Highlight Technical Achievements
- **Real-time Analysis**: Live data processing and visualization
- **Interactive Visualizations**: D3.js and Chart.js integration
- **Advanced Search**: Multi-criteria investigation tools
- **Professional UI**: Modern, responsive web interface

### 4. Show Data Processing
- **Multi-format Support**: CSV, JSON, TXT parsing
- **Pattern Detection**: Automated suspicious activity identification
- **Network Mapping**: Relationship analysis and clustering
- **Export Capabilities**: Download results for further analysis

## Technical Stack

- **Backend**: Python, Flask, Flask-SocketIO
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Charts**: Chart.js, D3.js
- **UI Framework**: Bootstrap 5
- **Data Processing**: Pandas, NumPy, NetworkX
- **Real-time**: WebSocket communication
- **Data Generation**: Faker library for synthetic data

## Performance Features

- **Real-time Processing**: Live data analysis and visualization
- **Interactive Visualizations**: Responsive charts and graphs
- **Efficient Search**: Optimized entity search algorithms
- **Memory Management**: Efficient data handling for large datasets
- **Responsive UI**: Fast loading and smooth interactions

## Documentation

For comprehensive documentation, see:
- **[System Overview](docs/SYSTEM_OVERVIEW.md)**: High-level system description and capabilities
- **[Technical Architecture](docs/TECHNICAL_ARCHITECTURE.md)**: System architecture and implementation details
- **[Web Interface](docs/WEB_INTERFACE.md)**: Web interface features and functionality
- **[User Guide](docs/USER_GUIDE.md)**: Comprehensive user instructions and best practices
- **[API Documentation](docs/API_DOCUMENTATION.md)**: Complete API endpoint documentation
- **[Comprehensive Documentation](COMPREHENSIVE_README.md)**: Complete system overview and documentation

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is developed for hackathon purposes.

## Support

For issues or questions, please check the documentation in the `docs/` folder or create an issue in the repository.

---
