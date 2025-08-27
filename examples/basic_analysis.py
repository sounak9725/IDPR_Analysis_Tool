#!/usr/bin/env python3
"""
Basic IPDR Analysis Example
Demonstrates how to use the IPDR analysis tool for basic operations
"""

import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.core.ipdr_analyzer import IPDRAnalyzer

def main():
    """Run basic IPDR analysis"""
    print("🔍 Basic IPDR Analysis Example")
    print("=" * 40)
    
    # Initialize analyzer
    analyzer = IPDRAnalyzer()
    
    # Load data
    data_file = os.path.join('..', 'data', 'raw', 'hackathon_ipdr_main.csv')
    if not os.path.exists(data_file):
        print(f"❌ Data file not found: {data_file}")
        print("Please run demo_runner.py first to generate sample data")
        return
    
    print(f"📁 Loading data from: {data_file}")
    if not analyzer.parse_ipdr_file(data_file):
        print("❌ Failed to parse data file")
        return
    
    # Extract relationships
    print("🔗 Extracting relationships...")
    analyzer.extract_relationships()
    
    # Analyze patterns
    print("📊 Analyzing communication patterns...")
    patterns = analyzer.analyze_communication_patterns()
    
    # Display results
    print(f"\n📈 Analysis Results:")
    print(f"   • Total communications: {patterns['total_communications']:,}")
    print(f"   • Unique A-parties: {patterns['unique_a_parties']}")
    print(f"   • Unique B-parties: {patterns['unique_b_parties']}")
    print(f"   • Network nodes: {analyzer.network_graph.number_of_nodes()}")
    print(f"   • Network edges: {analyzer.network_graph.number_of_edges()}")
    
    # Search for a sample entity
    if analyzer.data is not None and len(analyzer.data) > 0:
        sample_entity = analyzer.data['a_party'].iloc[0]
        print(f"\n🔎 Sample entity search: {sample_entity}")
        
        results = analyzer.search_entity(sample_entity)
        print(f"   • Total communications: {results['total_communications']}")
        print(f"   • Communication partners: {len(results['communication_partners'])}")
    
    print("\n✅ Basic analysis complete!")

if __name__ == "__main__":
    main()
