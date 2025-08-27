#!/usr/bin/env python3
"""
IPDR Analysis Web Dashboard
Interactive web interface for IPDR analysis and investigation
"""

import os
import sys
import json
import pandas as pd
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_socketio import SocketIO, emit
import threading
import time

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from src.core.ipdr_analyzer import IPDRAnalyzer

class IPDRDashboard:
    def __init__(self):
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'ipdr-hackathon-2024'
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        self.analyzer = None
        self.data_loaded = False
        self.setup_routes()
        
    def setup_routes(self):
        """Setup all web routes"""
        
        @self.app.route('/')
        def index():
            """Main dashboard page"""
            return render_template('dashboard.html')
        
        @self.app.route('/api/load-data')
        def load_data():
            """Load IPDR data"""
            try:
                if not self.data_loaded:
                    self.analyzer = IPDRAnalyzer()
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

def create_app():
    """Create and configure the Flask app"""
    dashboard = IPDRDashboard()
    return dashboard.app, dashboard.socketio

if __name__ == '__main__':
    app, socketio = create_app()
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
