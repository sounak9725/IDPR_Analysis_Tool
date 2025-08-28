#!/usr/bin/env python3
"""
Enhanced Features Demo Script
Demonstrates the new high-priority enhancements:
1. Enhanced B-Party Analysis
2. Advanced Filtering System
3. Case Management System
"""

import os
import sys
import pandas as pd
from datetime import datetime, timedelta

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.utils.enhanced_bparty_analyzer import EnhancedBPartyAnalyzer
from src.utils.advanced_filtering import AdvancedFilteringSystem, FilterCriteria, FilterType, FilterPriority
from src.utils.case_management import CaseManagementSystem, CaseStatus, PriorityLevel, EvidenceType
from src.core.ipdr_analyzer import IPDRAnalyzer

def print_header(title):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(f"🚀 {title}")
    print("="*60)

def print_section(title):
    """Print a formatted section header"""
    print(f"\n📋 {title}")
    print("-" * 40)

def demo_enhanced_bparty_analysis():
    """Demonstrate Enhanced B-Party Analysis"""
    print_section("Enhanced B-Party Analysis")
    
    # Initialize the analyzer
    bparty_analyzer = EnhancedBPartyAnalyzer()
    
    # Test data - mix of IP addresses and mobile numbers
    test_bparties = [
        "192.168.1.1",           # Private IP
        "8.8.8.8",               # Public IP (Google DNS)
        "919876543210",          # Indian mobile number
        "15551234567",           # US mobile number
        "10.0.0.1",              # Private IP
        "172.16.0.1",            # Private IP
        "9999999999",            # Suspicious pattern
        "1234567890",            # Suspicious pattern
        "1.1.1.1",               # Public IP (Cloudflare)
        "9876543210"             # Suspicious pattern
    ]
    
    print("🔍 Analyzing B-party data...")
    
    # Analyze each B-party
    analysis_results = []
    for bparty in test_bparties:
        result = bparty_analyzer.analyze_bparty(bparty)
        analysis_results.append(result)
        print(f"  📱 {bparty}: {result['type']} (Risk: {result['risk_score']})")
    
    # Generate comprehensive report
    print("\n📊 Generating B-party analysis report...")
    report = bparty_analyzer.generate_bparty_report(analysis_results)
    
    print(f"  📈 Total B-parties analyzed: {report['summary']['total_bparties']}")
    print(f"  🌐 IP Addresses: {report['summary']['ip_addresses']}")
    print(f"  📱 Mobile Numbers: {report['summary']['mobile_numbers']}")
    print(f"  ❓ Unknown Formats: {report['summary']['unknown_formats']}")
    print(f"  ⚠️  High Risk: {report['risk_distribution']['high_risk']}")
    print(f"  🔴 Medium Risk: {report['risk_distribution']['medium_risk']}")
    print(f"  🟢 Low Risk: {report['risk_distribution']['low_risk']}")
    
    # Show top risky B-parties
    if report['top_risky_bparties']:
        print("\n🚨 Top Risky B-Parties:")
        for i, risky in enumerate(report['top_risky_bparties'][:5], 1):
            print(f"  {i}. {risky['bparty_value']} - Risk: {risky['risk_score']} ({risky['type']})")
    
    return bparty_analyzer

def demo_advanced_filtering():
    """Demonstrate Advanced Filtering System"""
    print_section("Advanced Filtering System")
    
    # Initialize the filtering system
    filtering_system = AdvancedFilteringSystem()
    
    # Load sample IPDR data
    print("📊 Loading sample IPDR data...")
    try:
        # Try to load existing data
        data_file = os.path.join('data', 'raw', 'hackathon_ipdr_main.csv')
        if os.path.exists(data_file):
            df = pd.read_csv(data_file)
            print(f"  ✅ Loaded {len(df)} records from existing data")
        else:
            # Generate sample data if none exists
            print("  🔄 No existing data found, generating sample data...")
            from src.utils.synthetic_ipdr_generator import create_comprehensive_dataset
            df = create_comprehensive_dataset(1000)  # Generate 1000 records
            print(f"  ✅ Generated {len(df)} sample records")
    except Exception as e:
        print(f"  ❌ Error loading data: {e}")
        return None
    
    # Apply predefined templates
    print("\n🔧 Applying filter templates...")
    
    # Apply law enforcement critical filter
    filtering_system.apply_template('law_enforcement_critical')
    print("  ✅ Applied Law Enforcement Critical filter")
    
    # Apply suspicious activity filter
    filtering_system.apply_template('suspicious_activity')
    print("  ✅ Applied Suspicious Activity filter")
    
    # Apply network analysis filter
    filtering_system.apply_template('network_analysis')
    print("  ✅ Applied Network Analysis filter")
    
    # Create custom filter
    print("\n⚙️  Creating custom filter...")
    custom_filter = FilterCriteria(
        name="Custom Duration Filter",
        filter_type=FilterType.CUSTOM,
        priority=FilterPriority.MEDIUM,
        criteria={
            'duration': {'min': 30, 'max': 300},  # 30 seconds to 5 minutes
            'service_type': ['VOICE', 'SMS']
        },
        weight=1.2,
        description="Filter for calls between 30 seconds and 5 minutes"
    )
    filtering_system.add_filter(custom_filter)
    print("  ✅ Added custom duration filter")
    
    # Apply filters
    print("\n🚀 Applying all filters...")
    
    # Create context for relevance scoring
    context = {
        'entity_frequency': 10,  # Example frequency
        'geographic_context': {
            'distance_km': 150,
            'cross_border': False,
            'international': False
        },
        'risk_score': 65
    }
    
    # Apply filters
    filtered_data, filtered_out = filtering_system.apply_filters(df, context)
    
    print(f"  📊 Original records: {len(df)}")
    print(f"  ✅ Kept records: {len(filtered_data)}")
    print(f"  ❌ Filtered out: {len(filtered_out)}")
    print(f"  📈 Filter effectiveness: {round((len(filtered_data) / len(df)) * 100, 2)}%")
    
    # Show relevance scores
    if 'relevance_score' in filtered_data.columns:
        print(f"  🎯 Average relevance score: {filtered_data['relevance_score'].mean():.3f}")
        print(f"  🎯 Min relevance score: {filtered_data['relevance_score'].min():.3f}")
        print(f"  🎯 Max relevance score: {filtered_data['relevance_score'].max():.3f}")
    
    # Generate filter report
    print("\n📋 Generating filter report...")
    filter_report = filtering_system.generate_filter_report(df, filtered_data, filtered_out)
    
    print(f"  🔧 Active filters: {len(filter_report['active_filters'])}")
    for filter_info in filter_report['filter_configuration']:
        print(f"    - {filter_info['name']} ({filter_info['type']}) - Priority: {filter_info['priority']}")
    
    return filtering_system, filtered_data

def demo_case_management():
    """Demonstrate Case Management System"""
    print_section("Case Management System")
    
    # Initialize the case management system
    case_system = CaseManagementSystem()
    
    # Create a new case
    print("📋 Creating new investigation case...")
    case_id = case_system.create_case(
        case_number="IPDR-2024-001",
        title="Suspicious Communication Network Investigation",
        description="Investigation into suspicious communication patterns detected in IPDR logs",
        created_by="Detective Smith",
        priority=PriorityLevel.HIGH,
        assigned_to="Detective Smith",
        tags=["suspicious_activity", "network_analysis", "high_priority"]
    )
    print(f"  ✅ Created case: {case_id}")
    
    # Add investigation steps
    print("\n📝 Adding investigation steps...")
    
    step1_id = case_system.add_investigation_step(
        case_id=case_id,
        title="Initial Data Analysis",
        description="Analyze IPDR logs for suspicious patterns",
        assigned_to="Detective Smith",
        notes="Focus on high-frequency communications and unusual timing patterns"
    )
    print(f"  ✅ Added step 1: Initial Data Analysis")
    
    step2_id = case_system.add_investigation_step(
        case_id=case_id,
        title="B-Party Analysis",
        description="Analyze B-party information for risk indicators",
        assigned_to="Detective Smith",
        notes="Use enhanced B-party analyzer to identify suspicious recipients"
    )
    print(f"  ✅ Added step 2: B-Party Analysis")
    
    step3_id = case_system.add_investigation_step(
        case_id=case_id,
        title="Network Mapping",
        description="Map communication network and identify key nodes",
        assigned_to="Detective Smith",
        notes="Create network visualization and identify central entities"
    )
    print(f"  ✅ Added step 3: Network Mapping")
    
    # Add evidence
    print("\n🔍 Adding evidence...")
    
    evidence1_id = case_system.add_evidence(
        case_id=case_id,
        evidence_type=EvidenceType.IPDR_RECORD,
        title="IPDR Log Analysis Results",
        description="Results of suspicious activity detection in IPDR logs",
        collected_by="Detective Smith",
        metadata={
            'total_records': 1000,
            'suspicious_records': 45,
            'analysis_timestamp': datetime.now().isoformat()
        }
    )
    print(f"  ✅ Added evidence: IPDR Log Analysis Results")
    
    evidence2_id = case_system.add_evidence(
        case_id=case_id,
        evidence_type=EvidenceType.NETWORK_ANALYSIS,
        title="Network Visualization",
        description="Interactive network graph showing communication relationships",
        collected_by="Detective Smith",
        file_path="outputs/visualizations/network_analysis.png"
    )
    print(f"  ✅ Added evidence: Network Visualization")
    
    # Add suspects
    print("\n👤 Adding suspects...")
    
    suspect1_id = case_system.add_suspect(
        case_id=case_id,
        identifier="919876543210",
        identifier_type="mobile",
        name="Unknown Subject 1",
        risk_score=85.0
    )
    print(f"  ✅ Added suspect: 919876543210 (Risk: 85.0)")
    
    suspect2_id = case_system.add_suspect(
        case_id=case_id,
        identifier="192.168.1.100",
        identifier_type="ip",
        name="Unknown Subject 2",
        risk_score=72.0
    )
    print(f"  ✅ Added suspect: 192.168.1.100 (Risk: 72.0)")
    
    # Update investigation step status
    print("\n🔄 Updating investigation progress...")
    
    case_system.update_investigation_step(
        step_id=step1_id,
        status="completed",
        updated_by="Detective Smith",
        notes="Completed initial analysis. Found 45 suspicious records.",
        evidence_collected=[evidence1_id]
    )
    print(f"  ✅ Updated step 1: Completed")
    
    case_system.update_investigation_step(
        step_id=step2_id,
        status="in_progress",
        updated_by="Detective Smith",
        notes="Started B-party analysis. Using enhanced analyzer.",
        evidence_collected=[]
    )
    print(f"  ✅ Updated step 2: In Progress")
    
    # Update case status
    case_system.update_case_status(
        case_id=case_id,
        new_status=CaseStatus.IN_PROGRESS,
        updated_by="Detective Smith",
        notes="Investigation is now in progress with initial analysis complete"
    )
    print(f"  ✅ Updated case status: In Progress")
    
    # Get case summary
    print("\n📊 Getting case summary...")
    case_summary = case_system.get_case_summary(case_id)
    
    print(f"  📋 Case: {case_summary['case_info']['title']}")
    print(f"  📊 Total evidence: {case_summary['statistics']['total_evidence']}")
    print(f"  📝 Total steps: {case_summary['statistics']['total_steps']}")
    print(f"  ✅ Completed steps: {case_summary['statistics']['completed_steps']}")
    print(f"  📈 Completion: {case_summary['statistics']['completion_percentage']}%")
    print(f"  👤 Total suspects: {case_summary['statistics']['total_suspects']}")
    print(f"  🚨 High risk suspects: {case_summary['statistics']['high_risk_suspects']}")
    
    # Generate case report
    print("\n📄 Generating case report...")
    case_report = case_system.generate_case_report(case_id, "comprehensive")
    
    print(f"  📄 Report generated: {case_report['report_metadata']['report_type']}")
    print(f"  ⏰ Generated at: {case_report['report_metadata']['generated_at']}")
    
    # Export case data
    print("\n💾 Exporting case data...")
    success, result = case_system.export_case_data(case_id, "json")
    if success:
        print(f"  ✅ Case data exported to: {result}")
    else:
        print(f"  ❌ Export failed: {result}")
    
    # Get system statistics
    print("\n📈 Getting system statistics...")
    system_stats = case_system.get_system_statistics()
    
    print(f"  📋 Total cases: {system_stats['case_statistics']['total_cases']}")
    print(f"  🔓 Open cases: {system_stats['case_statistics']['open_cases']}")
    print(f"  🔄 In progress cases: {system_stats['case_statistics']['in_progress_cases']}")
    print(f"  🔒 Closed cases: {system_stats['case_statistics']['closed_cases']}")
    print(f"  🔍 Total evidence: {system_stats['evidence_statistics']['total_evidence']}")
    print(f"  👤 Total suspects: {system_stats['investigation_statistics']['total_suspects']}")
    
    return case_system, case_id

def demo_integration():
    """Demonstrate integration of all enhanced features"""
    print_section("Feature Integration Demo")
    
    print("🔄 Integrating enhanced features with existing IPDR analyzer...")
    
    # Initialize IPDR analyzer
    analyzer = IPDRAnalyzer()
    
    # Load sample data
    data_file = os.path.join('data', 'raw', 'hackathon_ipdr_main.csv')
    if os.path.exists(data_file):
        print("  📊 Loading existing IPDR data...")
        analyzer.parse_ipdr_file(data_file)
        print(f"  ✅ Loaded {len(analyzer.data)} records")
        
        # Extract relationships
        analyzer.extract_relationships()
        print("  🔗 Extracted communication relationships")
        
        # Get unique B-parties for analysis
        unique_bparties = analyzer.data['b_party'].unique()[:20]  # First 20 for demo
        
        # Enhanced B-party analysis
        print("\n🔍 Performing enhanced B-party analysis...")
        bparty_analyzer = EnhancedBPartyAnalyzer()
        
        bparty_results = []
        for bparty in unique_bparties:
            result = bparty_analyzer.analyze_bparty(str(bparty))
            bparty_results.append(result)
        
        # Create case for high-risk findings
        print("\n📋 Creating case for high-risk findings...")
        case_system = CaseManagementSystem()
        
        high_risk_case_id = case_system.create_case(
            case_number="IPDR-2024-002",
            title="High-Risk B-Party Investigation",
            description="Investigation into high-risk B-parties identified through enhanced analysis",
            created_by="System Analyst",
            priority=PriorityLevel.CRITICAL,
            tags=["high_risk", "bparty_analysis", "automated"]
        )
        
        # Add high-risk B-parties as suspects
        high_risk_count = 0
        for result in bparty_results:
            if result.get('risk_score', 0) >= 70:
                case_system.add_suspect(
                    case_id=high_risk_case_id,
                    identifier=result['bparty_value'],
                    identifier_type=result['type'],
                    risk_score=result['risk_score']
                )
                high_risk_count += 1
        
        print(f"  ✅ Created case with {high_risk_count} high-risk suspects")
        
        # Apply advanced filtering
        print("\n🔧 Applying advanced filtering to IPDR data...")
        filtering_system = AdvancedFilteringSystem()
        filtering_system.apply_template('law_enforcement_critical')
        
        # Convert analyzer data to DataFrame for filtering
        df = analyzer.data.copy()
        filtered_data, filtered_out = filtering_system.apply_filters(df)
        
        print(f"  📊 Filtered data: {len(filtered_data)} records kept out of {len(df)}")
        
        # Add filtered results as evidence
        if len(filtered_data) > 0:
            case_system.add_evidence(
                case_id=high_risk_case_id,
                evidence_type=EvidenceType.PATTERN_ANALYSIS,
                title="Filtered IPDR Records",
                description=f"IPDR records filtered using advanced filtering system. Kept {len(filtered_data)} relevant records.",
                collected_by="System Analyst",
                metadata={
                    'original_records': len(df),
                    'filtered_records': len(filtered_data),
                    'filter_effectiveness': round((len(filtered_data) / len(df)) * 100, 2)
                }
            )
            print("  ✅ Added filtered results as evidence")
        
        print("\n🎉 Integration demo completed successfully!")
        print("   All enhanced features are working together seamlessly!")
        
    else:
        print("  ❌ No IPDR data found. Please run the main demo first.")

def main():
    """Main demo function"""
    print_header("Enhanced IPDR Analysis Features Demo")
    print("This demo showcases the new high-priority enhancements:")
    print("1. 🎯 Enhanced B-Party Analysis")
    print("2. 🔧 Advanced Filtering System") 
    print("3. 📋 Case Management System")
    print("4. 🔄 Feature Integration")
    
    try:
        # Demo 1: Enhanced B-Party Analysis
        bparty_analyzer = demo_enhanced_bparty_analysis()
        
        # Demo 2: Advanced Filtering System
        filtering_system, filtered_data = demo_advanced_filtering()
        
        # Demo 3: Case Management System
        case_system, case_id = demo_case_management()
        
        # Demo 4: Feature Integration
        demo_integration()
        
        print_header("🎉 Demo Completed Successfully!")
        print("All enhanced features are working correctly!")
        print("\n🚀 Key Benefits Achieved:")
        print("  ✅ Enhanced B-party identification with IP geolocation and carrier info")
        print("  ✅ Advanced filtering with relevance scoring and noise reduction")
        print("  ✅ Comprehensive case management with evidence tracking")
        print("  ✅ Seamless integration with existing IPDR analysis")
        print("  ✅ Law enforcement investigation workflow support")
        print("  ✅ Audit trail and compliance features")
        
        print("\n📁 Generated Files:")
        print("  - Enhanced B-party analysis results")
        print("  - Filtered IPDR datasets")
        print("  - Case management data in data/cases/")
        print("  - Audit trails and evidence records")
        
        print("\n🔧 Next Steps:")
        print("  - Use web dashboard to explore enhanced features")
        print("  - Create real investigation cases")
        print("  - Apply advanced filtering to your data")
        print("  - Generate comprehensive reports")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎯 All enhancements are ready for law enforcement investigations!")
    else:
        print("\n❌ Demo encountered issues. Please check the error messages above.")
