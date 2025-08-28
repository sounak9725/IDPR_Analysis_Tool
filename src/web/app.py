#!/usr/bin/env python3
"""
IPDR Analysis Web Dashboard
Interactive web interface for IPDR analysis and investigation
"""

import os
import sys
import json
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_socketio import SocketIO, emit
import threading
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('web_dashboard.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from src.core.ipdr_analyzer import IPDRAnalyzer
from src.utils.enhanced_bparty_analyzer import EnhancedBPartyAnalyzer
from src.utils.advanced_filtering import AdvancedFilteringSystem, FilterCriteria, FilterType, FilterPriority
from src.utils.case_management import CaseManagementSystem, Case, EvidenceItem, InvestigationStep, SuspectProfile

class IPDRDashboard:
    def __init__(self):
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'ipdr-hackathon-2024')
        self.app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
        
        # Configure SocketIO with better production settings
        self.socketio = SocketIO(
            self.app, 
            cors_allowed_origins="*",
            logger=True,
            engineio_logger=True,
            ping_timeout=60,
            ping_interval=25
        )
        
        self.analyzer = None
        self.enhanced_analyzer = None
        self.filtering_system = None
        self.case_management = None
        self.data_loaded = False
        self.setup_routes()
        self.setup_error_handlers()
    
    def clean_data_for_json(self, df):
        """Clean DataFrame data for JSON serialization by replacing NaN values"""
        if df is None or df.empty:
            return []
        
        try:
            # Replace NaN values with None (which becomes null in JSON)
            df_clean = df.replace({np.nan: None})
            
            # Convert to records and clean each record
            records = df_clean.to_dict('records')
            cleaned_records = []
            
            for record in records:
                cleaned_record = {}
                for key, value in record.items():
                    if pd.isna(value) or value == np.nan:
                        cleaned_record[key] = None
                    elif isinstance(value, (np.integer, np.floating)):
                        cleaned_record[key] = value.item()
                    elif isinstance(value, np.bool_):
                        cleaned_record[key] = bool(value)
                    elif isinstance(value, pd.Timestamp):
                        cleaned_record[key] = value.isoformat()
                    else:
                        cleaned_record[key] = value
                cleaned_records.append(cleaned_record)
            
            return cleaned_records
        except Exception as e:
            logger.error(f"Error cleaning data for JSON: {str(e)}")
            # Fallback: return empty list if cleaning fails
            return []
        
    def setup_error_handlers(self):
        """Setup error handlers for better user experience"""
        
        @self.app.errorhandler(404)
        def not_found_error(error):
            logger.warning(f"404 error: {request.url}")
            return jsonify({'error': 'Resource not found'}), 404
        
        @self.app.errorhandler(500)
        def internal_error(error):
            logger.error(f"500 error: {str(error)}")
            return jsonify({'error': 'Internal server error'}), 500
        
        @self.app.errorhandler(413)
        def too_large(error):
            logger.warning(f"File too large: {request.url}")
            return jsonify({'error': 'File too large'}), 413
        
    def setup_routes(self):
        """Setup all web routes"""
        
        @self.app.route('/')
        def index():
            """Main dashboard page"""
            return render_template('dashboard.html')
        
        @self.app.route('/health')
        def health_check():
            """Health check endpoint for monitoring"""
            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'data_loaded': self.data_loaded,
                'version': '1.0.0'
            })
        
        @self.app.route('/status')
        def status():
            """Detailed system status"""
            return jsonify({
                'status': 'operational',
                'data_loaded': self.data_loaded,
                'analyzers_initialized': {
                    'core_analyzer': self.analyzer is not None,
                    'enhanced_analyzer': self.enhanced_analyzer is not None,
                    'filtering_system': self.filtering_system is not None,
                    'case_management': self.case_management is not None
                },
                'timestamp': datetime.now().isoformat(),
                'uptime': 'running'
            })
        
        @self.app.route('/enhanced-analysis')
        def enhanced_analysis():
            """Enhanced B-Party Analysis page"""
            return render_template('enhanced_analysis.html')
        
        @self.app.route('/advanced-filtering')
        def advanced_filtering():
            """Advanced Filtering page"""
            return render_template('advanced_filtering.html')
        
        @self.app.route('/case-management')
        def case_management():
            """Case Management page"""
            return render_template('case_management.html')
        
        @self.app.route('/api/load-data')
        def load_data():
            """Load IPDR data"""
            try:
                if not self.data_loaded:
                    self.analyzer = IPDRAnalyzer()
                    self.enhanced_analyzer = EnhancedBPartyAnalyzer()
                    self.filtering_system = AdvancedFilteringSystem()
                    self.case_management = CaseManagementSystem()
                    
                    data_file = os.path.join('data', 'raw', 'hackathon_ipdr_main.csv')
                    
                    if not os.path.exists(data_file):
                        return jsonify({'error': 'Data file not found'}), 404
                    
                    if not self.analyzer.parse_ipdr_file(data_file):
                        return jsonify({'error': 'Failed to parse data file'}), 500
                    
                    self.analyzer.extract_relationships()
                    self.data_loaded = True
                
                return jsonify({
                    'success': True,
                    'message': f'Loaded {len(self.analyzer.data)} records',
                    'records_count': len(self.analyzer.data)
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/overview')
        def get_overview():
            """Get overview statistics"""
            if not self.data_loaded:
                return jsonify({'error': 'Data not loaded'}), 400
            
            try:
                patterns = self.analyzer.analyze_communication_patterns()
                suspicious = self.analyzer.detect_suspicious_activities()
                
                return jsonify({
                    'total_records': patterns['total_communications'],
                    'unique_a_parties': patterns['unique_a_parties'],
                    'unique_b_parties': patterns['unique_b_parties'],
                    'network_nodes': self.analyzer.network_graph.number_of_nodes(),
                    'network_edges': self.analyzer.network_graph.number_of_edges(),
                    'avg_duration': patterns.get('avg_duration', 0),
                    'suspicious_count': len(suspicious),
                    'peak_hours': patterns.get('busiest_hours', {}).get('peak_hours', []),
                    'quiet_hours': patterns.get('busiest_hours', {}).get('quiet_hours', [])
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/search')
        def search_entity():
            """Enhanced entity search"""
            if not self.data_loaded:
                return jsonify({'error': 'Data not loaded'}), 400
            
            query = request.args.get('q', '').strip()
            if not query:
                return jsonify({'error': 'Search query required'}), 400
            
            try:
                results = self.analyzer.search_entity(query)
                
                # Enhanced search results
                enhanced_results = {
                    'entity': query,
                    'total_communications': results['total_communications'],
                    'as_initiator': len(results['as_initiator']),
                    'as_recipient': len(results['as_recipient']),
                    'communication_partners': results['communication_partners'][:10],  # Top 10
                    'time_range': results.get('time_range', {}),
                    'top_partners': [],
                    'recent_activity': [],
                    'suspicious_flags': []
                }
                
                # Get top communication partners with counts
                if self.analyzer.data is not None:
                    entity_data = self.analyzer.data[
                        (self.analyzer.data['a_party'] == query) | 
                        (self.analyzer.data['b_party'] == query)
                    ]
                    
                    # Top partners
                    if entity_data['a_party'].iloc[0] == query:
                        partners = entity_data['b_party'].value_counts().head(5)
                    else:
                        partners = entity_data['a_party'].value_counts().head(5)
                    
                    enhanced_results['top_partners'] = [
                        {'entity': partner, 'count': count} 
                        for partner, count in partners.items()
                    ]
                    
                    # Recent activity
                    recent = entity_data.sort_values('timestamp', ascending=False).head(5)
                    enhanced_results['recent_activity'] = [
                        {
                            'timestamp': str(row['timestamp']),
                            'partner': row['b_party'] if row['a_party'] == query else row['a_party'],
                            'duration': row.get('duration', 0),
                            'service_type': row.get('service_type', 'Unknown')
                        }
                        for _, row in recent.iterrows()
                    ]
                
                return jsonify(enhanced_results)
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/suspicious')
        def get_suspicious_activities():
            """Get suspicious activities"""
            if not self.data_loaded:
                return jsonify({'error': 'Data not loaded'}), 400
            
            try:
                suspicious = self.analyzer.detect_suspicious_activities()
                return jsonify({'suspicious_activities': suspicious})
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/network')
        def get_network_data():
            """Get network graph data for visualization"""
            if not self.data_loaded:
                return jsonify({'error': 'Data not loaded'}), 400
            
            try:
                # Get network nodes and edges
                nodes = []
                edges = []
                
                for node in self.analyzer.network_graph.nodes():
                    degree = self.analyzer.network_graph.degree(node)
                    nodes.append({
                        'id': node,
                        'label': node,
                        'degree': degree,
                        'size': min(degree * 2, 20)  # Scale node size
                    })
                
                for edge in self.analyzer.network_graph.edges():
                    edges.append({
                        'source': edge[0],
                        'target': edge[1]
                    })
                
                return jsonify({
                    'nodes': nodes[:100],  # Limit for performance
                    'edges': edges[:200]   # Limit for performance
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/patterns')
        def get_patterns():
            """Get communication patterns"""
            if not self.data_loaded:
                return jsonify({'error': 'Data not loaded'}), 400
            
            try:
                patterns = self.analyzer.analyze_communication_patterns()
                
                # Format patterns for frontend
                formatted_patterns = {
                    'time_patterns': {
                        'peak_hours': patterns.get('busiest_hours', {}).get('peak_hours', []),
                        'quiet_hours': patterns.get('busiest_hours', {}).get('quiet_hours', [])
                    },
                    'top_communicators': {
                        'initiators': list(patterns.get('top_communicators', {}).get('top_initiators', {}).items())[:10],
                        'recipients': list(patterns.get('top_communicators', {}).get('top_recipients', {}).items())[:10]
                    }
                }
                
                return jsonify(formatted_patterns)
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/investigation')
        def investigation_page():
            """Enhanced investigation page"""
            return render_template('investigation.html')
        
        @self.app.route('/network')
        def network_page():
            """Network visualization page"""
            return render_template('network.html')
        
        @self.app.route('/patterns')
        def patterns_page():
            """Patterns analysis page"""
            return render_template('patterns.html')
        
        # Enhanced Features API Endpoints
        
        @self.app.route('/api/enhanced-analysis')
        def enhanced_analysis_api():
            """Enhanced B-Party Analysis API"""
            if not self.data_loaded:
                return jsonify({'error': 'Data not loaded'}), 400
            
            try:
                # Get sample B-parties from the data
                bparties = self.analyzer.data['b_party'].unique()[:20]  # First 20 unique B-parties
                
                # Analyze B-parties
                analysis_results = self.enhanced_analyzer.batch_analyze_bparties(bparties.tolist())
                
                # Generate report
                report = self.enhanced_analyzer.generate_bparty_report(analysis_results)
                
                return jsonify({
                    'success': True,
                    'analysis_results': analysis_results,
                    'report': report
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/advanced-filtering')
        def advanced_filtering_api():
            """Advanced Filtering API"""
            if not self.data_loaded:
                return jsonify({'error': 'Data not loaded'}), 400
            
            try:
                # Apply default filter templates
                self.filtering_system.apply_template('law_enforcement_critical')
                self.filtering_system.apply_template('suspicious_activity')
                
                # Get filtered results
                logger.info("Running filters on data...")
                filtered_data, filtered_out = self.filtering_system.apply_filters(self.analyzer.data)
                
                logger.info(f"Filtering complete: {len(filtered_data)} records kept, {len(filtered_out)} filtered out")
                
                # Ensure we have valid DataFrames
                if not isinstance(filtered_data, pd.DataFrame):
                    logger.error(f"filtered_data is not a DataFrame: {type(filtered_data)}")
                    filtered_data = pd.DataFrame()
                
                if not isinstance(filtered_out, pd.DataFrame):
                    logger.error(f"filtered_out is not a DataFrame: {type(filtered_out)}")
                    filtered_out = pd.DataFrame()
                
                # Clean data for JSON serialization
                logger.info("Cleaning data for JSON serialization...")
                cleaned_filtered_data = self.clean_data_for_json(filtered_data)
                
                # Limit to 100 records
                cleaned_filtered_data = cleaned_filtered_data[:100]
                
                logger.info(f"Cleaned data: {len(cleaned_filtered_data)} records ready for JSON")
                
                # Get filter statistics
                stats = {
                    'original_count': len(self.analyzer.data),
                    'filtered_count': len(filtered_data),
                    'filtered_out_count': len(filtered_out),
                    'active_filters': len(self.filtering_system.active_filters),
                    'filter_effectiveness': round((len(filtered_data) / len(self.analyzer.data)) * 100, 2)
                }
                
                return jsonify({
                    'success': True,
                    'filtered_data': cleaned_filtered_data,
                    'statistics': stats,
                    'active_filters': [
                        {
                            'name': f.name,
                            'type': f.filter_type.value,
                            'priority': f.priority.value,
                            'criteria': f.criteria
                        }
                        for f in self.filtering_system.active_filters
                    ]
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/case-management')
        def case_management_api():
            """Case Management API"""
            if not self.data_loaded:
                return jsonify({'error': 'Data not loaded'}), 400
            
            try:
                # Get existing cases
                cases = self.case_management.get_all_cases()
                
                # Get system statistics
                stats = self.case_management.get_system_statistics()
                
                return jsonify({
                    'success': True,
                    'cases': cases,
                    'statistics': stats
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/case-management/create', methods=['POST'])
        def create_case_api():
            """Create new case API"""
            if not self.data_loaded:
                return jsonify({'error': 'Data not loaded'}), 400
            
            try:
                data = request.get_json()
                case_name = data.get('name', 'New Investigation Case')
                description = data.get('description', 'Case created via web interface')
                priority = data.get('priority', 'medium')
                
                case_id = self.case_management.create_case_simple(
                    name=case_name,
                    description=description,
                    priority=priority
                )
                
                return jsonify({
                    'success': True,
                    'case_id': case_id,
                    'message': f'Case "{case_name}" created successfully'
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/case-management/<case_id>/add-evidence', methods=['POST'])
        def add_evidence_api(case_id):
            """Add evidence to case API"""
            if not self.data_loaded:
                return jsonify({'error': 'Data not loaded'}), 400
            
            try:
                data = request.get_json()
                evidence_type_str = data.get('type', 'document')
                description = data.get('description', 'Evidence added via web interface')
                collected_by = data.get('source', 'Web Dashboard')
                
                # Convert string to EvidenceType enum
                evidence_type_map = {
                    'document': 'DOCUMENT',
                    'image': 'SCREENSHOT',
                    'video': 'VIDEO_RECORDING',
                    'audio': 'AUDIO_RECORDING',
                    'ipdr_record': 'IPDR_RECORD',
                    'network_analysis': 'NETWORK_ANALYSIS',
                    'pattern_analysis': 'PATTERN_ANALYSIS',
                    'geolocation_data': 'GEOLOCATION_DATA',
                    'carrier_info': 'CARRIER_INFO',
                    'exported_report': 'EXPORTED_REPORT',
                    'other': 'OTHER'
                }
                
                evidence_type_enum = evidence_type_map.get(evidence_type_str.lower(), 'OTHER')
                
                # Import EvidenceType enum
                from src.utils.case_management import EvidenceType
                evidence_type = getattr(EvidenceType, evidence_type_enum)
                
                evidence_id = self.case_management.add_evidence(
                    case_id=case_id,
                    evidence_type=evidence_type,
                    title=f"Evidence: {evidence_type_str}",
                    description=description,
                    collected_by=collected_by
                )
                
                return jsonify({
                    'success': True,
                    'evidence_id': evidence_id,
                    'message': 'Evidence added successfully'
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500

def create_app():
    """Create and configure the Flask app"""
    dashboard = IPDRDashboard()
    return dashboard.app, dashboard.socketio

if __name__ == '__main__':
    app, socketio = create_app()
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
