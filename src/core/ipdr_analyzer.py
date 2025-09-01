import pandas as pd
import networkx as nx
import json
import csv
import re
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import warnings
warnings.filterwarnings('ignore')

class IPDRAnalyzer:
    def __init__(self):
        self.data = None
        self.network_graph = nx.Graph()
        self.communication_patterns = {}
        self.suspicious_activities = []
        
    def parse_ipdr_file(self, file_path, file_format='auto'):
        """
        Parse IPDR files in multiple formats
        """
        try:
            if file_format == 'auto':
                file_format = self._detect_format(file_path)
            
            if file_format == 'csv':
                self.data = pd.read_csv(file_path)
            elif file_format == 'json':
                with open(file_path, 'r') as f:
                    json_data = json.load(f)
                self.data = pd.json_normalize(json_data)
            elif file_format == 'txt':
                self.data = self._parse_text_file(file_path)
            
            self._normalize_columns()
            print(f"Successfully parsed {len(self.data)} records")
            return True
            
        except Exception as e:
            print(f"Error parsing file: {e}")
            return False
    
    def _detect_format(self, file_path):
        """Auto-detect file format"""
        if file_path.endswith('.csv'):
            return 'csv'
        elif file_path.endswith('.json'):
            return 'json'
        elif file_path.endswith('.txt'):
            return 'txt'
        else:
            return 'csv'  # default
    
    def _parse_text_file(self, file_path):
        """Parse text-based IPDR files"""
        records = []
        with open(file_path, 'r') as f:
            for line in f:
                parts = line.strip().split('|')
                if len(parts) >= 5:
                    records.append({
                        'timestamp': parts[0],
                        'a_party': parts[1],
                        'b_party': parts[2],
                        'duration': int(parts[3]) if parts[3].isdigit() else 0,
                        'service_type': parts[4]
                    })
        return pd.DataFrame(records)
    
    def _normalize_columns(self):
        """Normalize column names across different formats"""
        column_mapping = {
            'calling_number': 'a_party',
            'called_number': 'b_party',
            'caller': 'a_party',
            'callee': 'b_party',
            'source_ip': 'a_party',
            'dest_ip': 'b_party',
            'call_duration': 'duration',
            'session_duration': 'duration',
            'call_time': 'timestamp',
            'start_time': 'timestamp'
        }
        
        for old_name, new_name in column_mapping.items():
            if old_name in self.data.columns:
                self.data.rename(columns={old_name: new_name}, inplace=True)

        # timestamp is datetime
        if 'timestamp' in self.data.columns:
            self.data['timestamp'] = pd.to_datetime(self.data['timestamp'])
    
    def extract_relationships(self):
        """Extract A-party to B-party relationships"""
        if self.data is None:
            print("No data loaded. Please parse IPDR file first.")
            return
        
        # building network graph
        for _, row in self.data.iterrows():
            a_party = str(row['a_party'])
            b_party = str(row['b_party'])
            
            # adding edge with communication metadata
            if self.network_graph.has_edge(a_party, b_party):
                # Update existing edge
                self.network_graph[a_party][b_party]['weight'] += 1
                self.network_graph[a_party][b_party]['total_duration'] += row.get('duration', 0)
            else:
                # creating new edge
                self.network_graph.add_edge(a_party, b_party, 
                                          weight=1, 
                                          total_duration=row.get('duration', 0),
                                          first_contact=row.get('timestamp'))
        
        print(f"Network graph created with {self.network_graph.number_of_nodes()} nodes and {self.network_graph.number_of_edges()} edges")
    
    def analyze_communication_patterns(self):
        """Analyze communication patterns for insights"""
        if self.data is None:
            return
        
        patterns = {
            'total_communications': len(self.data),
            'unique_a_parties': self.data['a_party'].nunique(),
            'unique_b_parties': self.data['b_party'].nunique(),
            'avg_duration': self.data.get('duration', pd.Series([0])).mean(),
            'busiest_hours': self._analyze_time_patterns(),
            'top_communicators': self._get_top_communicators(),
            'communication_frequency': self._analyze_frequency()
        }
        
        self.communication_patterns = patterns
        return patterns
    
    def _analyze_time_patterns(self):
        """Analyze temporal communication patterns"""
        if 'timestamp' not in self.data.columns:
            return {}
        
        self.data['hour'] = self.data['timestamp'].dt.hour
        hourly_counts = self.data['hour'].value_counts().sort_index()
        
        return {
            'hourly_distribution': hourly_counts.to_dict(),
            'peak_hours': hourly_counts.nlargest(3).index.tolist(),
            'quiet_hours': hourly_counts.nsmallest(3).index.tolist()
        }
    
    def _get_top_communicators(self):
        """Get most active communicators"""
        a_party_counts = self.data['a_party'].value_counts()
        b_party_counts = self.data['b_party'].value_counts()
        
        return {
            'top_initiators': a_party_counts.head(10).to_dict(),
            'top_recipients': b_party_counts.head(10).to_dict()
        }
    
    def _analyze_frequency(self):
        """Analyze communication frequency patterns"""
        frequency_analysis = {}
        
        # group by A-party and B-party combinations
        pair_counts = self.data.groupby(['a_party', 'b_party']).size().reset_index(name='count')
        
        frequency_analysis['high_frequency_pairs'] = pair_counts[pair_counts['count'] > 10]
        frequency_analysis['avg_communications_per_pair'] = pair_counts['count'].mean()
        
        return frequency_analysis
    
    def detect_suspicious_activities(self):
        """Detect suspicious communication patterns"""
        suspicious = []
        
        if self.data is None:
            return suspicious
        
        if 'timestamp' in self.data.columns:
            late_night_calls = self.data[
                (self.data['timestamp'].dt.hour >= 23) | 
                (self.data['timestamp'].dt.hour <= 5)
            ]
            
            if len(late_night_calls) > 0:
                suspicious.append({
                    'type': 'unusual_timing',
                    'description': f'{len(late_night_calls)} communications during unusual hours (11PM-5AM)',
                    'severity': 'medium',
                    'details': late_night_calls[['a_party', 'b_party', 'timestamp']].head(10).to_dict('records')
                })
        
        if 'duration' in self.data.columns:
            short_calls = self.data[self.data['duration'] <= 5]  
            
            if len(short_calls) > len(self.data) * 0.1:  
                suspicious.append({
                    'type': 'short_duration_pattern',
                    'description': f'{len(short_calls)} very short communications (≤5 seconds)',
                    'severity': 'high',
                    'details': short_calls[['a_party', 'b_party', 'duration']].head(10).to_dict('records')
                })
        
        pair_counts = self.data.groupby(['a_party', 'b_party']).size().reset_index(name='count')
        high_freq_pairs = pair_counts[pair_counts['count'] > 50] 
        
        if len(high_freq_pairs) > 0:
            suspicious.append({
                'type': 'high_frequency_communication',
                'description': f'{len(high_freq_pairs)} pairs with unusually high communication frequency',
                'severity': 'medium',
                'details': high_freq_pairs.head(10).to_dict('records')
            })
        
        node_degrees = dict(self.network_graph.degree())
        high_degree_nodes = {node: degree for node, degree in node_degrees.items() if degree > 20}
        
        if high_degree_nodes:
            suspicious.append({
                'type': 'high_connectivity_nodes',
                'description': f'{len(high_degree_nodes)} entities with unusually high connectivity',
                'severity': 'high',
                'details': high_degree_nodes
            })
        
        self.suspicious_activities = suspicious
        return suspicious
    
    def search_entity(self, entity_id, entity_type='both'):
        """Search for specific entity (phone number or IP)"""
        if self.data is None:
            return {}
        
        results = {
            'entity_id': entity_id,
            'as_initiator': [],
            'as_recipient': [],
            'total_communications': 0,
            'communication_partners': set(),
            'time_range': None
        }
        
        if entity_type in ['both', 'initiator']:
            as_initiator = self.data[self.data['a_party'] == entity_id]
            results['as_initiator'] = as_initiator.to_dict('records')
            results['communication_partners'].update(as_initiator['b_party'].tolist())
        
        if entity_type in ['both', 'recipient']:
            as_recipient = self.data[self.data['b_party'] == entity_id]
            results['as_recipient'] = as_recipient.to_dict('records')
            results['communication_partners'].update(as_recipient['a_party'].tolist())
        
        # calculate totals
        results['total_communications'] = len(results['as_initiator']) + len(results['as_recipient'])
        results['communication_partners'] = list(results['communication_partners'])
        
        # time range
        all_records = results['as_initiator'] + results['as_recipient']
        if all_records and 'timestamp' in self.data.columns:
            timestamps = [record.get('timestamp') for record in all_records if record.get('timestamp')]
            if timestamps:
                results['time_range'] = {
                    'first': min(timestamps),
                    'last': max(timestamps)
                }
        
        return results
    
    def generate_network_visualization(self, output_file='network_graph.png', max_nodes=100):
        """Generate network visualization"""
        try:
            import matplotlib.pyplot as plt
            
            # limit nodes for visualization
            if self.network_graph.number_of_nodes() > max_nodes:
                # Get top nodes by degree
                top_nodes = sorted(self.network_graph.degree(), key=lambda x: x[1], reverse=True)[:max_nodes]
                subgraph_nodes = [node for node, _ in top_nodes]
                G = self.network_graph.subgraph(subgraph_nodes)
            else:
                G = self.network_graph
            
            plt.figure(figsize=(12, 8))
            pos = nx.spring_layout(G, k=1, iterations=50)
            
            # draw network
            nx.draw(G, pos, 
                   node_color='lightblue',
                   node_size=50,
                   edge_color='gray',
                   alpha=0.7,
                   with_labels=False)
            
            plt.title("Communication Network Graph")
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            plt.close()
            
            print(f"Network visualization saved to {output_file}")
            
        except ImportError:
            print("Matplotlib not available. Install with: pip install matplotlib")
    
    def export_results(self, output_file='ipdr_analysis_results.json'):
        """Export analysis results"""
        results = {
            'analysis_timestamp': datetime.now().isoformat(),
            'summary': {
                'total_records': len(self.data) if self.data is not None else 0,
                'network_nodes': self.network_graph.number_of_nodes(),
                'network_edges': self.network_graph.number_of_edges()
            },
            'communication_patterns': self.communication_patterns,
            'suspicious_activities': self.suspicious_activities
        }
        
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"Results exported to {output_file}")

# Example usage and testing
def generate_sample_ipdr_data(filename='sample_ipdr.csv', num_records=1000):
    """Generate sample IPDR data for testing"""
    import random
    from datetime import datetime, timedelta
    
    # Sample phone numbers and IPs
    phone_numbers = [f"91{random.randint(7000000000, 9999999999)}" for _ in range(50)]
    ip_addresses = [f"192.168.{random.randint(1,255)}.{random.randint(1,255)}" for _ in range(20)]
    
    records = []
    base_time = datetime.now() - timedelta(days=30)
    
    for i in range(num_records):
        # Create realistic patterns
        timestamp = base_time + timedelta(
            days=random.randint(0, 29),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )
        
        a_party = random.choice(phone_numbers + ip_addresses)
        b_party = random.choice(phone_numbers + ip_addresses)
        
        # Ensure A and B are different
        while b_party == a_party:
            b_party = random.choice(phone_numbers + ip_addresses)
        
        # Add some suspicious patterns
        if random.random() < 0.05:  # 5% suspicious calls
            duration = random.randint(1, 5)  # Very short calls
            timestamp = timestamp.replace(hour=random.choice([1, 2, 3, 23]))  # Unusual hours
        else:
            duration = random.randint(10, 3600)  # Normal duration
        
        records.append({
            'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'a_party': a_party,
            'b_party': b_party,
            'duration': duration,
            'service_type': random.choice(['VOICE', 'SMS', 'DATA'])
        })
    
    df = pd.DataFrame(records)
    df.to_csv(filename, index=False)
    print(f"Sample IPDR data with {num_records} records saved to {filename}")

# Main execution example
if __name__ == "__main__":
    # Generate sample data
    generate_sample_ipdr_data('sample_ipdr.csv', 1000)
    
    # Initialize analyzer
    analyzer = IPDRAnalyzer()
    
    # Parse IPDR file
    analyzer.parse_ipdr_file('sample_ipdr.csv')
    
    # Extract relationships
    analyzer.extract_relationships()
    
    # Analyze patterns
    patterns = analyzer.analyze_communication_patterns()
    print("\nCommunication Patterns:")
    print(f"Total communications: {patterns['total_communications']}")
    print(f"Unique A-parties: {patterns['unique_a_parties']}")
    print(f"Unique B-parties: {patterns['unique_b_parties']}")
    
    # Detect suspicious activities
    suspicious = analyzer.detect_suspicious_activities()
    print(f"\nFound {len(suspicious)} suspicious activity patterns:")
    for activity in suspicious:
        print(f"- {activity['type']}: {activity['description']} (Severity: {activity['severity']})")
    
    # Search for specific entity
    if patterns['unique_a_parties'] > 0:
        # Get a sample entity to search
        sample_entity = analyzer.data['a_party'].iloc[0]
        search_results = analyzer.search_entity(sample_entity)
        print(f"\nSearch results for {sample_entity}:")
        print(f"Total communications: {search_results['total_communications']}")
        print(f"Communication partners: {len(search_results['communication_partners'])}")
    
    # Export results
    analyzer.export_results('analysis_results.json')