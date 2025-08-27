#!/usr/bin/env python3
"""
IPDR Analysis Demo Runner
Run this script to see the complete IPDR analysis in action
"""

import os
import sys
import json
from datetime import datetime

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def check_dependencies():
    """Check if all required packages are installed"""
    required_packages = ['pandas', 'numpy', 'networkx', 'matplotlib', 'faker']
    missing = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print("❌ Missing required packages:")
        for pkg in missing:
            print(f"   - {pkg}")
        print(f"\nInstall with: pip install {' '.join(missing)}")
        return False
    
    print("✅ All dependencies found")
    return True

def generate_sample_data():
    """Generate sample IPDR data"""
    print("\n📊 Generating sample IPDR data...")
    
    try:
        from src.utils.synthetic_ipdr_generator import create_comprehensive_dataset
        records, case_studies = create_comprehensive_dataset()
        print(f"✅ Generated {len(records)} sample records")
        return True
    except Exception as e:
        print(f"❌ Error generating data: {e}")
        return False

def run_analysis():
    """Run the main IPDR analysis"""
    print("\n🔍 Running IPDR analysis...")
    
    try:
        # Import here to avoid issues if not all deps are installed
        from src.core.ipdr_analyzer import IPDRAnalyzer
        
        # Initialize analyzer
        analyzer = IPDRAnalyzer()
        
        # Load data
        print("   Loading data...")
        data_file = os.path.join('data', 'raw', 'hackathon_ipdr_main.csv')
        if not analyzer.parse_ipdr_file(data_file):
            print("❌ Could not load data file")
            return False
        
        # Extract relationships
        print("   Extracting relationships...")
        analyzer.extract_relationships()
        
        # Analyze patterns
        print("   Analyzing communication patterns...")
        patterns = analyzer.analyze_communication_patterns()
        
        # Display key metrics
        print(f"\n📈 Analysis Results:")
        print(f"   • Total records analyzed: {patterns['total_communications']:,}")
        print(f"   • Unique A-parties: {patterns['unique_a_parties']}")
        print(f"   • Unique B-parties: {patterns['unique_b_parties']}")
        print(f"   • Network nodes: {analyzer.network_graph.number_of_nodes()}")
        print(f"   • Network edges: {analyzer.network_graph.number_of_edges()}")
        
        if 'avg_duration' in patterns and patterns['avg_duration'] > 0:
            print(f"   • Average duration: {patterns['avg_duration']:.1f} seconds")
        
        # Detect suspicious activities
        print("   Detecting suspicious activities...")
        suspicious = analyzer.detect_suspicious_activities()
        
        print(f"\n🚨 Suspicious Activities Found: {len(suspicious)}")
        for i, activity in enumerate(suspicious, 1):
            severity_emoji = {"low": "🟡", "medium": "🟠", "high": "🔴"}.get(activity['severity'], "⚪")
            print(f"   {i}. {severity_emoji} {activity['type'].replace('_', ' ').title()}")
            print(f"      └─ {activity['description']}")
        
        # Entity search example
        if analyzer.data is not None and len(analyzer.data) > 0:
            sample_entity = analyzer.data['a_party'].iloc[0]
            search_results = analyzer.search_entity(sample_entity)
            
            print(f"\n🔎 Entity Search Example ({sample_entity}):")
            print(f"   • Total communications: {search_results['total_communications']}")
            print(f"   • Communication partners: {len(search_results['communication_partners'])}")
            print(f"   • As initiator: {len(search_results['as_initiator'])}")
            print(f"   • As recipient: {len(search_results['as_recipient'])}")
        
        # Generate outputs
        print("\n💾 Generating output files...")
        try:
            viz_file = os.path.join('outputs', 'visualizations', 'network_analysis.png')
            analyzer.generate_network_visualization(viz_file, max_nodes=50)
            print("   ✅ Network visualization: outputs/visualizations/network_analysis.png")
        except Exception as e:
            print(f"   ⚠️  Could not generate visualization: {e}")
        
        analysis_file = os.path.join('outputs', 'analysis', 'complete_analysis.json')
        analyzer.export_results(analysis_file)
        print("   ✅ Analysis results: outputs/analysis/complete_analysis.json")
        
        return True, analyzer, patterns, suspicious
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()
        return False

def display_detailed_analysis(analyzer, patterns, suspicious):
    """Display detailed analysis results"""
    print("\n" + "="*60)
    print("📊 DETAILED ANALYSIS RESULTS")
    print("="*60)
    
    # Communication patterns
    if 'busiest_hours' in patterns and patterns['busiest_hours']:
        print(f"\n⏰ Time Patterns:")
        if 'peak_hours' in patterns['busiest_hours']:
            peak_hours = patterns['busiest_hours']['peak_hours']
            print(f"   • Peak communication hours: {peak_hours}")
        if 'quiet_hours' in patterns['busiest_hours']:
            quiet_hours = patterns['busiest_hours']['quiet_hours']
            print(f"   • Quietest hours: {quiet_hours}")
    
    # Top communicators
    if 'top_communicators' in patterns:
        top_comm = patterns['top_communicators']
        if 'top_initiators' in top_comm:
            print(f"\n📞 Top 5 Call Initiators:")
            for entity, count in list(top_comm['top_initiators'].items())[:5]:
                print(f"   • {entity}: {count} calls initiated")
        
        if 'top_recipients' in top_comm:
            print(f"\n📱 Top 5 Call Recipients:")
            for entity, count in list(top_comm['top_recipients'].items())[:5]:
                print(f"   • {entity}: {count} calls received")
    
    # Network analysis
    if analyzer.network_graph.number_of_nodes() > 0:
        try:
            import networkx as nx
            
            print(f"\n🕸️  Network Analysis:")
            
            # Degree centrality
            degree_cent = nx.degree_centrality(analyzer.network_graph)
            top_central = sorted(degree_cent.items(), key=lambda x: x[1], reverse=True)[:3]
            
            print(f"   • Most connected entities:")
            for entity, centrality in top_central:
                connections = analyzer.network_graph.degree(entity)
                print(f"     └─ {entity}: {connections} direct connections")
            
            # Connected components
            components = list(nx.connected_components(analyzer.network_graph))
            print(f"   • Network components: {len(components)}")
            if len(components) > 1:
                largest_component = max(components, key=len)
                print(f"   • Largest component: {len(largest_component)} nodes")
                
        except ImportError:
            print("   (NetworkX not available for advanced network metrics)")
    
    # Suspicious activity details
    print(f"\n🚨 Suspicious Activity Details:")
    for i, activity in enumerate(suspicious, 1):
        print(f"\n   {i}. {activity['type'].replace('_', ' ').title()}")
        print(f"      Severity: {activity['severity'].upper()}")
        print(f"      Description: {activity['description']}")
        
        if 'details' in activity and activity['details']:
            print(f"      Sample records:")
            details = activity['details']
            if isinstance(details, list):
                for j, detail in enumerate(details[:3]):  # Show max 3 examples
                    if isinstance(detail, dict):
                        a_party = detail.get('a_party', 'Unknown')
                        b_party = detail.get('b_party', 'Unknown')
                        print(f"        {j+1}. {a_party} ↔ {b_party}")
            elif isinstance(details, dict):
                for entity, count in list(details.items())[:3]:
                    print(f"        • {entity}: {count}")

def interactive_search(analyzer):
    """Interactive entity search"""
    print("\n" + "="*60)
    print("🔍 INTERACTIVE ENTITY SEARCH")
    print("="*60)
    print("Enter phone numbers or IP addresses to search for patterns")
    print("(Type 'quit' to exit, 'sample' for random entity)")
    
    while True:
        try:
            query = input("\nSearch entity: ").strip()
            
            if query.lower() == 'quit':
                break
            elif query.lower() == 'sample':
                if analyzer.data is not None and len(analyzer.data) > 0:
                    import random
                    all_entities = list(analyzer.data['a_party'].unique()) + list(analyzer.data['b_party'].unique())
                    query = random.choice(all_entities)
                    print(f"Searching for sample entity: {query}")
                else:
                    print("No data available for sampling")
                    continue
            elif not query:
                continue
            
            # Search for the entity
            results = analyzer.search_entity(query)
            
            if results['total_communications'] == 0:
                print(f"❌ No communications found for {query}")
                continue
            
            print(f"\n📊 Results for {query}:")
            print(f"   • Total communications: {results['total_communications']}")
            print(f"   • As initiator: {len(results['as_initiator'])}")
            print(f"   • As recipient: {len(results['as_recipient'])}")
            print(f"   • Unique partners: {len(results['communication_partners'])}")
            
            if results['time_range']:
                print(f"   • Activity period: {results['time_range']['first']} to {results['time_range']['last']}")
            
            # Show communication partners
            if len(results['communication_partners']) > 0:
                print(f"\n   Top communication partners:")
                partners = results['communication_partners'][:5]  # Show top 5
                for partner in partners:
                    print(f"     • {partner}")
                
                if len(results['communication_partners']) > 5:
                    print(f"     ... and {len(results['communication_partners']) - 5} more")
            
        except KeyboardInterrupt:
            print("\n\nExiting search...")
            break
        except Exception as e:
            print(f"❌ Search error: {e}")

def main():
    """Main demo function"""
    print("🚀 IPDR Analysis Tool - Demo")
    print("="*40)
    
    # Check dependencies
    if not check_dependencies():
        return
    
    # Generate sample data if needed
    if not os.path.exists(os.path.join('data', 'raw', 'hackathon_ipdr_main.csv')):
        if not generate_sample_data():
            return
    else:
        print("✅ Found existing sample data")
    
    # Run main analysis
    result = run_analysis()
    if isinstance(result, tuple):
        success, analyzer, patterns, suspicious = result
        if not success:
            return
    else:
        return
    
    # Display results
    display_detailed_analysis(analyzer, patterns, suspicious)
    
    # Ask if user wants interactive search
    print("\n" + "="*60)
    try:
        response = input("\nWould you like to run interactive entity search? (y/n): ").strip().lower()
        if response in ['y', 'yes']:
            interactive_search(analyzer)
    except KeyboardInterrupt:
        print("\nExiting...")
    
    # Final summary
    print("\n" + "="*60)
    print("✅ ANALYSIS COMPLETE!")
    print("="*60)
    print("Generated files:")
    
    files_created = []
    for filename in ['hackathon_ipdr_main.csv', 'network_analysis.png', 'complete_analysis.json']:
        if os.path.exists(filename):
            size = os.path.getsize(filename)
            size_str = f"{size/1024:.1f}KB" if size < 1024*1024 else f"{size/(1024*1024):.1f}MB"
            files_created.append(f"   📄 {filename} ({size_str})")
    
    for file_info in files_created:
        print(file_info)
    
    print(f"\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Ready for hackathon presentation! 🎉")

if __name__ == "__main__":
    main()