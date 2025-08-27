# IPDR Analysis Tool

A comprehensive toolkit for analyzing Internet Protocol Detail Records (IPDR) with advanced pattern detection and network visualization capabilities.

## 🚀 Features

- **Multi-format IPDR parsing** (CSV, JSON, TXT)
- **Network analysis** with relationship mapping
- **Suspicious activity detection** using pattern recognition
- **Interactive entity search** and investigation tools
- **Advanced visualizations** with network graphs
- **Synthetic data generation** for testing and development

## 📁 Project Structure

```
ipdr_hackathon/
├── src/                          # Source code
│   ├── core/                     # Core analysis components
│   │   ├── __init__.py
│   │   └── ipdr_analyzer.py      # Main analysis engine
│   ├── utils/                    # Utility functions
│   │   ├── __init__.py
│   │   └── synthetic_ipdr_generator.py  # Data generation
│   └── visualization/            # Visualization components
│       └── __init__.py
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
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## 🛠️ Installation

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
4. **For web dashboard (optional but recommended):**
   ```bash
   pip install flask flask-socketio
   ```

## 🎯 Quick Start

### Option 1: Command Line Demo
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

### Option 2: Web Dashboard (Recommended)
Launch the interactive web dashboard:
```bash
python web_dashboard.py
```

This will:
- Start a web server on http://localhost:5000
- Open the dashboard automatically in your browser
- Provide interactive visualizations and search
- Enable real-time analysis and investigation

## 📊 Analysis Capabilities

### Core Analysis
- **Communication Pattern Analysis**: Identify peak hours, busy entities, and communication trends
- **Network Relationship Mapping**: Build and analyze communication networks
- **Suspicious Activity Detection**: Detect unusual patterns like:
  - High-frequency calling
  - Burner phone patterns
  - Criminal network clustering
  - Automated bot behavior

### Visualization
- **Network Graphs**: Interactive network visualizations
- **Communication Heatmaps**: Time-based activity patterns
- **Entity Relationship Charts**: Connection strength analysis

### Search & Investigation
- **Entity Search**: Find all communications for specific entities
- **Pattern Matching**: Identify similar communication patterns
- **Timeline Analysis**: Track entity activity over time

## 🔧 Usage Examples

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

## 📈 Output Files

The tool generates several output files:
- `outputs/analysis/complete_analysis.json` - Detailed analysis results
- `outputs/visualizations/network_analysis.png` - Network visualization
- Various data files in the `data/` directory

## 🧪 Testing

Run tests (when implemented):
```bash
python -m pytest tests/
```

## 📝 Data Formats

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

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is developed for hackathon purposes.

## 🆘 Support

For issues or questions, please check the documentation in the `docs/` folder or create an issue in the repository.

---

**Ready for hackathon presentation! 🎉**
