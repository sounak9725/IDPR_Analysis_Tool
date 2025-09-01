"""
Case Management System for IPDR Investigations
Features:
- Case creation and tracking
- Evidence chain management
- Investigation timeline
- Suspect relationship mapping
- Report generation
- Audit trail logging
- Legal compliance tracking
"""

import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import pandas as pd
import logging
import os
from pathlib import Path

class CaseStatus(Enum):
    """Case status enumeration"""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    UNDER_REVIEW = "under_review"
    CLOSED = "closed"
    ARCHIVED = "archived"

class EvidenceType(Enum):
    """Evidence type enumeration"""
    IPDR_RECORD = "ipdr_record"
    COMMUNICATION_LOG = "communication_log"
    NETWORK_ANALYSIS = "network_analysis"
    PATTERN_ANALYSIS = "pattern_analysis"
    GEOLOCATION_DATA = "geolocation_data"
    CARRIER_INFO = "carrier_info"
    EXPORTED_REPORT = "exported_report"
    SCREENSHOT = "screenshot"
    AUDIO_RECORDING = "audio_recording"
    VIDEO_RECORDING = "video_recording"
    DOCUMENT = "document"
    OTHER = "other"

class PriorityLevel(Enum):
    """Priority level enumeration"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

@dataclass
class EvidenceItem:
    """Evidence item data structure"""
    id: str
    case_id: str
    evidence_type: EvidenceType
    title: str
    description: str
    file_path: Optional[str] = None
    metadata: Dict[str, Any] = None
    collected_by: str = ""
    collected_at: datetime = None
    chain_of_custody: List[Dict[str, Any]] = None
    hash_value: Optional[str] = None
    is_verified: bool = False
    
    def __post_init__(self):
        if self.collected_at is None:
            self.collected_at = datetime.now()
        if self.metadata is None:
            self.metadata = {}
        if self.chain_of_custody is None:
            self.chain_of_custody = []

@dataclass
class InvestigationStep:
    """Investigation step data structure"""
    id: str
    case_id: str
    step_number: int
    title: str
    description: str
    status: str = "pending"  # pending, in_progress, completed, failed
    assigned_to: str = ""
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    notes: str = ""
    evidence_collected: List[str] = None  # List of evidence IDs
    next_steps: List[str] = None  # List of next step IDs
    
    def __post_init__(self):
        if self.evidence_collected is None:
            self.evidence_collected = []
        if self.next_steps is None:
            self.next_steps = []

@dataclass
class SuspectProfile:
    """Suspect profile data structure"""
    id: str
    case_id: str
    identifier: str  # Phone number, IP address, etc.
    identifier_type: str  # mobile, ip, email, etc.
    name: Optional[str] = None
    aliases: List[str] = None
    risk_score: float = 0.0
    first_seen: Optional[datetime] = None
    last_seen: Optional[datetime] = None
    total_communications: int = 0
    suspicious_indicators: List[str] = None
    relationships: List[Dict[str, Any]] = None
    notes: str = ""
    
    def __post_init__(self):
        if self.aliases is None:
            self.aliases = []
        if self.suspicious_indicators is None:
            self.suspicious_indicators = []
        if self.relationships is None:
            self.relationships = []

@dataclass
class Case:
    """Case data structure"""
    id: str
    case_number: str
    title: str
    description: str
    status: CaseStatus
    priority: PriorityLevel
    created_by: str
    created_at: datetime
    assigned_to: str = ""
    updated_at: datetime = None
    closed_at: Optional[datetime] = None
    tags: List[str] = None
    notes: str = ""
    legal_hold: bool = False
    retention_policy: str = "standard"
    
    def __post_init__(self):
        if self.updated_at is None:
            self.updated_at = self.created_at
        if self.tags is None:
            self.tags = []

class CaseManagementSystem:
    def __init__(self, data_directory: str = "data/cases"):
        self.data_directory = Path(data_directory)
        self.data_directory.mkdir(parents=True, exist_ok=True)
        
        # Initialize storage files
        self.cases_file = self.data_directory / "cases.json"
        self.evidence_file = self.data_directory / "evidence.json"
        self.steps_file = self.data_directory / "investigation_steps.json"
        self.suspects_file = self.data_directory / "suspects.json"
        self.audit_file = self.data_directory / "audit_trail.json"
        
        # Load existing data
        self.cases = self._load_data(self.cases_file, {})
        self.evidence = self._load_data(self.evidence_file, {})
        self.investigation_steps = self._load_data(self.steps_file, {})
        self.suspects = self._load_data(self.suspects_file, {})
        self.audit_trail = self._load_data(self.audit_file, [])
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        self.logger.info(f"Case Management System initialized at {self.data_directory}")
    
    def _load_data(self, file_path: Path, default_value: Any) -> Any:
        """Load data from JSON file"""
        try:
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # Create file with default value
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(default_value, f, indent=2)
                return default_value
        except Exception as e:
            self.logger.error(f"Error loading {file_path}: {str(e)}")
            return default_value
    
    def _save_data(self, file_path: Path, data: Any) -> bool:
        """Save data to JSON file"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str)
            return True
        except Exception as e:
            self.logger.error(f"Error saving {file_path}: {str(e)}")
            return False
    
    def _log_audit_event(self, event_type: str, description: str, user: str, case_id: str = None, details: Dict = None):
        """Log audit event"""
        audit_entry = {
            'id': str(uuid.uuid4()),
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'description': description,
            'user': user,
            'case_id': case_id,
            'details': details or {},
            'ip_address': '127.0.0.1'  # Would be actual IP in production
        }
        
        self.audit_trail.append(audit_entry)
        self._save_data(self.audit_file, self.audit_trail)
    
    def create_case(self, case_number: str, title: str, description: str, created_by: str, 
                   priority: PriorityLevel = PriorityLevel.MEDIUM, assigned_to: str = "", 
                   tags: List[str] = None) -> str:
        """Create a new investigation case"""
        try:
            case_id = str(uuid.uuid4())
            
            case = Case(
                id=case_id,
                case_number=case_number,
                title=title,
                description=description,
                status=CaseStatus.OPEN,
                priority=priority,
                created_by=created_by,
                created_at=datetime.now(),
                assigned_to=assigned_to,
                tags=tags or []
            )
            
            self.cases[case_id] = asdict(case)
            self._save_data(self.cases_file, self.cases)
            
            # Log audit event
            self._log_audit_event(
                'case_created',
                f"Case {case_number} created: {title}",
                created_by,
                case_id,
                {'case_number': case_number, 'priority': priority.value}
            )
            
            self.logger.info(f"Created case {case_number} with ID {case_id}")
            return case_id
            
        except Exception as e:
            self.logger.error(f"Error creating case: {str(e)}")
            raise
    
    def update_case_status(self, case_id: str, new_status: CaseStatus, updated_by: str, notes: str = "") -> bool:
        """Update case status"""
        try:
            if case_id not in self.cases:
                raise ValueError(f"Case {case_id} not found")
            
            old_status = self.cases[case_id]['status']
            self.cases[case_id]['status'] = new_status.value
            self.cases[case_id]['updated_at'] = datetime.now().isoformat()
            
            if new_status == CaseStatus.CLOSED:
                self.cases[case_id]['closed_at'] = datetime.now().isoformat()
            
            if notes:
                self.cases[case_id]['notes'] += f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {notes}"
            
            self._save_data(self.cases_file, self.cases)
            
            # Log audit event
            self._log_audit_event(
                'case_status_updated',
                f"Case status changed from {old_status} to {new_status.value}",
                updated_by,
                case_id,
                {'old_status': old_status, 'new_status': new_status.value, 'notes': notes}
            )
            
            self.logger.info(f"Updated case {case_id} status to {new_status.value}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating case status: {str(e)}")
            return False
    
    def add_evidence(self, case_id: str, evidence_type: EvidenceType, title: str, description: str,
                    collected_by: str, file_path: Optional[str] = None, metadata: Dict[str, Any] = None) -> str:
        """Add evidence to a case"""
        try:
            if case_id not in self.cases:
                raise ValueError(f"Case {case_id} not found")
            
            evidence_id = str(uuid.uuid4())
            
            evidence = EvidenceItem(
                id=evidence_id,
                case_id=case_id,
                evidence_type=evidence_type,
                title=title,
                description=description,
                file_path=file_path,
                metadata=metadata or {},
                collected_by=collected_by
            )
            
            self.evidence[evidence_id] = asdict(evidence)
            self._save_data(self.evidence_file, self.evidence)
            
            # Log audit event
            self._log_audit_event(
                'evidence_added',
                f"Evidence added: {title}",
                collected_by,
                case_id,
                {'evidence_id': evidence_id, 'evidence_type': evidence_type.value}
            )
            
            self.logger.info(f"Added evidence {evidence_id} to case {case_id}")
            return evidence_id
            
        except Exception as e:
            self.logger.error(f"Error adding evidence: {str(e)}")
            raise
    
    def update_evidence_chain_of_custody(self, evidence_id: str, action: str, user: str, 
                                       location: str = "", notes: str = "") -> bool:
        """Update evidence chain of custody"""
        try:
            if evidence_id not in self.evidence:
                raise ValueError(f"Evidence {evidence_id} not found")
            
            custody_entry = {
                'timestamp': datetime.now().isoformat(),
                'action': action,
                'user': user,
                'location': location,
                'notes': notes
            }
            
            self.evidence[evidence_id]['chain_of_custody'].append(custody_entry)
            self._save_data(self.evidence_file, self.evidence)
            
            # Log audit event
            self._log_audit_event(
                'evidence_custody_updated',
                f"Evidence chain of custody updated: {action}",
                user,
                self.evidence[evidence_id]['case_id'],
                {'evidence_id': evidence_id, 'action': action, 'location': location}
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating evidence chain of custody: {str(e)}")
            return False
    
    def add_investigation_step(self, case_id: str, title: str, description: str, 
                             assigned_to: str = "", notes: str = "") -> str:
        """Add investigation step to a case"""
        try:
            if case_id not in self.cases:
                raise ValueError(f"Case {case_id} not found")
            
            step_id = str(uuid.uuid4())
            
            # Get next step number
            existing_steps = [s for s in self.investigation_steps.values() if s['case_id'] == case_id]
            step_number = len(existing_steps) + 1
            
            step = InvestigationStep(
                id=step_id,
                case_id=case_id,
                step_number=step_number,
                title=title,
                description=description,
                assigned_to=assigned_to,
                notes=notes
            )
            
            self.investigation_steps[step_id] = asdict(step)
            self._save_data(self.steps_file, self.investigation_steps)
            
            # Log audit event
            self._log_audit_event(
                'investigation_step_added',
                f"Investigation step added: {title}",
                assigned_to or "system",
                case_id,
                {'step_id': step_id, 'step_number': step_number}
            )
            
            self.logger.info(f"Added investigation step {step_id} to case {case_id}")
            return step_id
            
        except Exception as e:
            self.logger.error(f"Error adding investigation step: {str(e)}")
            raise
    
    def update_investigation_step(self, step_id: str, status: str, updated_by: str, 
                                notes: str = "", evidence_collected: List[str] = None) -> bool:
        """Update investigation step status and details"""
        try:
            if step_id not in self.investigation_steps:
                raise ValueError(f"Step {step_id} not found")
            
            step = self.investigation_steps[step_id]
            
            if status == "in_progress" and not step['started_at']:
                step['started_at'] = datetime.now().isoformat()
            elif status == "completed" and not step['completed_at']:
                step['completed_at'] = datetime.now().isoformat()
            
            step['status'] = status
            step['notes'] += f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {notes}"
            
            if evidence_collected:
                step['evidence_collected'].extend(evidence_collected)
            
            self._save_data(self.steps_file, self.investigation_steps)
            
            # Log audit event
            self._log_audit_event(
                'investigation_step_updated',
                f"Investigation step updated: {step['title']} - {status}",
                updated_by,
                step['case_id'],
                {'step_id': step_id, 'status': status, 'evidence_collected': evidence_collected}
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating investigation step: {str(e)}")
            return False
    
    def add_suspect(self, case_id: str, identifier: str, identifier_type: str, 
                   name: Optional[str] = None, risk_score: float = 0.0) -> str:
        """Add suspect to a case"""
        try:
            if case_id not in self.cases:
                raise ValueError(f"Case {case_id} not found")
            
            suspect_id = str(uuid.uuid4())
            
            suspect = SuspectProfile(
                id=suspect_id,
                case_id=case_id,
                identifier=identifier,
                identifier_type=identifier_type,
                name=name,
                risk_score=risk_score
            )
            
            self.suspects[suspect_id] = asdict(suspect)
            self._save_data(self.suspects_file, self.suspects)
            
            # Log audit event
            self._log_audit_event(
                'suspect_added',
                f"Suspect added: {identifier}",
                "system",
                case_id,
                {'suspect_id': suspect_id, 'identifier': identifier, 'risk_score': risk_score}
            )
            
            self.logger.info(f"Added suspect {suspect_id} to case {case_id}")
            return suspect_id
            
        except Exception as e:
            self.logger.error(f"Error adding suspect: {str(e)}")
            raise
    
    def update_suspect_risk_score(self, suspect_id: str, new_risk_score: float, 
                                updated_by: str, reason: str = "") -> bool:
        """Update suspect risk score"""
        try:
            if suspect_id not in self.suspects:
                raise ValueError(f"Suspect {suspect_id} not found")
            
            old_risk_score = self.suspects[suspect_id]['risk_score']
            self.suspects[suspect_id]['risk_score'] = new_risk_score
            self.suspects[suspect_id]['notes'] += f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Risk score updated from {old_risk_score} to {new_risk_score}. Reason: {reason}"
            
            self._save_data(self.suspects_file, self.suspects)
            
            # Log audit event
            self._log_audit_event(
                'suspect_risk_updated',
                f"Suspect risk score updated: {old_risk_score} -> {new_risk_score}",
                updated_by,
                self.suspects[suspect_id]['case_id'],
                {'suspect_id': suspect_id, 'old_risk': old_risk_score, 'new_risk': new_risk_score, 'reason': reason}
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating suspect risk score: {str(e)}")
            return False
    
    def get_case_summary(self, case_id: str) -> Dict[str, Any]:
        """Get comprehensive case summary"""
        try:
            if case_id not in self.cases:
                raise ValueError(f"Case {case_id} not found")
            
            case = self.cases[case_id]
            
            # Get case evidence
            case_evidence = [e for e in self.evidence.values() if e['case_id'] == case_id]
            
            # Get investigation steps
            case_steps = [s for s in self.investigation_steps.values() if s['case_id'] == case_id]
            
            # Get suspects
            case_suspects = [s for s in self.suspects.values() if s['case_id'] == case_id]
            
            # Calculate statistics
            total_evidence = len(case_evidence)
            completed_steps = len([s for s in case_steps if s['status'] == 'completed'])
            total_steps = len(case_steps)
            high_risk_suspects = len([s for s in case_suspects if s['risk_score'] >= 70])
            
            summary = {
                'case_info': case,
                'statistics': {
                    'total_evidence': total_evidence,
                    'total_steps': total_steps,
                    'completed_steps': completed_steps,
                    'completion_percentage': round((completed_steps / total_steps * 100) if total_steps > 0 else 0, 2),
                    'total_suspects': len(case_suspects),
                    'high_risk_suspects': high_risk_suspects
                },
                'evidence_summary': [
                    {
                        'id': e['id'],
                        'type': e['evidence_type'],
                        'title': e['title'],
                        'collected_at': e['collected_at'],
                        'collected_by': e['collected_by']
                    }
                    for e in case_evidence
                ],
                'investigation_progress': [
                    {
                        'step_number': s['step_number'],
                        'title': s['title'],
                        'status': s['status'],
                        'assigned_to': s['assigned_to'],
                        'started_at': s['started_at'],
                        'completed_at': s['completed_at']
                    }
                    for s in sorted(case_steps, key=lambda x: x['step_number'])
                ],
                'suspects_summary': [
                    {
                        'id': s['id'],
                        'identifier': s['identifier'],
                        'identifier_type': s['identifier_type'],
                        'name': s['name'],
                        'risk_score': s['risk_score'],
                        'total_communications': s['total_communications']
                    }
                    for s in case_suspects
                ]
            }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error getting case summary: {str(e)}")
            return {'error': str(e)}
    
    def generate_case_report(self, case_id: str, report_type: str = "comprehensive") -> Dict[str, Any]:
        """Generate case report for export"""
        try:
            case_summary = self.get_case_summary(case_id)
            if 'error' in case_summary:
                return case_summary
            
            case = case_summary['case_info']
            
            report = {
                'report_metadata': {
                    'report_type': report_type,
                    'generated_at': datetime.now().isoformat(),
                    'generated_by': 'Case Management System',
                    'case_id': case_id,
                    'case_number': case['case_number']
                },
                'case_overview': {
                    'title': case['title'],
                    'description': case['description'],
                    'status': self._format_status(case['status']),
                    'priority': self._format_priority(case['priority']),
                    'created_at': case['created_at'],
                    'assigned_to': case['assigned_to'],
                    'tags': case['tags']
                },
                'investigation_summary': case_summary['statistics'],
                'evidence_inventory': case_summary['evidence_summary'],
                'investigation_timeline': case_summary['investigation_progress'],
                'suspects_analysis': case_summary['suspects_summary'],
                'legal_compliance': {
                    'legal_hold': case['legal_hold'],
                    'retention_policy': case['retention_policy'],
                    'audit_trail_available': True,
                    'chain_of_custody_maintained': True
                }
            }
            
            if report_type == "executive":
                # Simplified version for executives
                report = {
                    'report_metadata': report['report_metadata'],
                    'case_overview': report['case_overview'],
                    'key_findings': {
                        'total_evidence': case_summary['statistics']['total_evidence'],
                        'high_risk_suspects': case_summary['statistics']['high_risk_suspects'],
                        'completion_percentage': case_summary['statistics']['completion_percentage']
                    }
                }
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating case report: {str(e)}")
            return {'error': str(e)}
    
    def search_cases(self, query: str = "", status: CaseStatus = None, 
                    priority: PriorityLevel = None, assigned_to: str = "", 
                    tags: List[str] = None) -> List[Dict[str, Any]]:
        """Search cases based on criteria"""
        try:
            results = []
            
            for case_id, case in self.cases.items():
                # Text search
                if query:
                    searchable_text = f"{case['title']} {case['description']} {case['case_number']}".lower()
                    if query.lower() not in searchable_text:
                        continue
                
                # Status filter
                if status:
                    case_status = self._format_status(case['status'])
                    if case_status != status.value:
                        continue
                
                # Priority filter
                if priority:
                    case_priority = self._format_priority(case['priority'])
                    if case_priority != priority.value:
                        continue
                
                # Assigned to filter
                if assigned_to and case['assigned_to'] != assigned_to:
                    continue
                
                # Tags filter
                if tags:
                    if not any(tag in case['tags'] for tag in tags):
                        continue
                
                results.append({
                    'case_id': case_id,
                    'case_number': case['case_number'],
                    'title': case['title'],
                    'status': self._format_status(case['status']),
                    'priority': self._format_priority(case['priority']),
                    'created_at': case['created_at'],
                    'assigned_to': case['assigned_to'],
                    'tags': case['tags']
                })
            
            # Sort by creation date (newest first)
            results.sort(key=lambda x: x['created_at'], reverse=True)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error searching cases: {str(e)}")
            return []
    
    def get_audit_trail(self, case_id: str = None, start_date: datetime = None, 
                        end_date: datetime = None, event_type: str = None) -> List[Dict[str, Any]]:
        """Get audit trail with optional filtering"""
        try:
            filtered_audit = self.audit_trail.copy()
            
            # Filter by case ID
            if case_id:
                filtered_audit = [entry for entry in filtered_audit if entry['case_id'] == case_id]
            
            # Filter by date range
            if start_date:
                filtered_audit = [
                    entry for entry in filtered_audit 
                    if datetime.fromisoformat(entry['timestamp']) >= start_date
                ]
            
            if end_date:
                filtered_audit = [
                    entry for entry in filtered_audit 
                    if datetime.fromisoformat(entry['timestamp']) <= end_date
                ]
            
            # Filter by event type
            if event_type:
                filtered_audit = [entry for entry in filtered_audit if entry['event_type'] == event_type]
            
            # Sort by timestamp (newest first)
            filtered_audit.sort(key=lambda x: x['timestamp'], reverse=True)
            
            return filtered_audit
            
        except Exception as e:
            self.logger.error(f"Error getting audit trail: {str(e)}")
            return []
    
    def export_case_data(self, case_id: str, export_format: str = "json") -> Tuple[bool, str]:
        """Export case data in specified format"""
        try:
            case_summary = self.get_case_summary(case_id)
            if 'error' in case_summary:
                return False, case_summary['error']
            
            export_dir = self.data_directory / "exports"
            export_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"case_{case_id}_{timestamp}"
            
            if export_format.lower() == "json":
                file_path = export_dir / f"{filename}.json"
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(case_summary, f, indent=2, default=str)
            
            elif export_format.lower() == "csv":
                # Export key data to CSV
                file_path = export_dir / f"{filename}.csv"
                
                # Evidence CSV
                evidence_df = pd.DataFrame(case_summary['evidence_summary'])
                if not evidence_df.empty:
                    evidence_df.to_csv(file_path, index=False)
                
                # Suspects CSV
                suspects_file = export_dir / f"{filename}_suspects.csv"
                suspects_df = pd.DataFrame(case_summary['suspects_summary'])
                if not suspects_df.empty:
                    suspects_df.to_csv(suspects_file, index=False)
            
            else:
                return False, f"Unsupported export format: {export_format}"
            
            # Log export event
            self._log_audit_event(
                'case_exported',
                f"Case data exported in {export_format} format",
                "system",
                case_id,
                {'export_format': export_format, 'file_path': str(file_path)}
            )
            
            return True, str(file_path)
            
        except Exception as e:
            self.logger.error(f"Error exporting case data: {str(e)}")
            return False, str(e)
    
    def get_system_statistics(self) -> Dict[str, Any]:
        """Get system-wide statistics"""
        try:
            total_cases = len(self.cases)
            
            # Handle both enum values and string representations
            open_cases = 0
            in_progress_cases = 0
            closed_cases = 0
            
            for case in self.cases.values():
                status = self._format_status(case['status'])
                if status == 'open':
                    open_cases += 1
                elif status == 'in_progress':
                    in_progress_cases += 1
                elif status == 'closed':
                    closed_cases += 1
            
            total_evidence = len(self.evidence)
            total_suspects = len(self.suspects)
            total_steps = len(self.investigation_steps)
            
            # Priority distribution - handle both enum values and string representations
            priority_distribution = {}
            for case in self.cases.values():
                priority = case['priority']
                if isinstance(priority, str):
                    # Extract clean priority value from string representation
                    if 'PriorityLevel.' in priority:
                        clean_priority = priority.split('.')[-1].lower()
                    else:
                        clean_priority = priority.lower()
                else:
                    clean_priority = priority.lower()
                
                priority_distribution[clean_priority] = priority_distribution.get(clean_priority, 0) + 1
            
            # Recent activity (last 30 days)
            thirty_days_ago = datetime.now() - timedelta(days=30)
            recent_audit_entries = [
                entry for entry in self.audit_trail
                if datetime.fromisoformat(entry['timestamp']) >= thirty_days_ago
            ]
            
            stats = {
                'case_statistics': {
                    'total_cases': total_cases,
                    'open_cases': open_cases,
                    'in_progress_cases': in_progress_cases,
                    'closed_cases': closed_cases,
                    'priority_distribution': priority_distribution
                },
                'evidence_statistics': {
                    'total_evidence': total_evidence,
                    'evidence_per_case': round(total_evidence / total_cases, 2) if total_cases > 0 else 0
                },
                'investigation_statistics': {
                    'total_suspects': total_suspects,
                    'total_steps': total_steps,
                    'steps_per_case': round(total_steps / total_cases, 2) if total_cases > 0 else 0
                },
                'activity_statistics': {
                    'recent_audit_entries': len(recent_audit_entries),
                    'total_audit_entries': len(self.audit_trail)
                },
                'generated_at': datetime.now().isoformat()
            }
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error getting system statistics: {str(e)}")
            return {'error': str(e)}
    
    def get_all_cases(self) -> List[Dict[str, Any]]:
        """Get all cases with additional metadata for web display"""
        try:
            cases_list = []
            
            for case_id, case in self.cases.items():
                # Get case evidence count
                evidence_count = len([e for e in self.evidence.values() if e['case_id'] == case_id])
                
                # Get case steps count
                steps_count = len([s for s in self.investigation_steps.values() if s['case_id'] == case_id])
                
                # Get case suspects count
                suspects_count = len([s for s in self.suspects.values() if s['case_id'] == case_id])
                
                case_data = {
                    'id': case_id,
                    'case_number': case['case_number'],
                    'name': case['title'],  # Map title to name for web interface
                    'title': case['title'],
                    'description': case['description'],
                    'status': self._format_status(case['status']),
                    'priority': self._format_priority(case['priority']),
                    'created_by': case['created_by'],
                    'created_at': case['created_at'],
                    'assigned_to': case['assigned_to'],
                    'tags': case['tags'],
                    'evidence_count': evidence_count,
                    'steps_count': steps_count,
                    'suspects_count': suspects_count
                }
                
                cases_list.append(case_data)
            
            # Sort by creation date (newest first)
            # Handle mixed timestamp formats (strings and datetime objects)
            def safe_sort_key(case):
                created_at = case['created_at']
                if isinstance(created_at, str):
                    try:
                        return datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    except:
                        return datetime.min
                elif isinstance(created_at, datetime):
                    return created_at
                else:
                    return datetime.min
            
            cases_list.sort(key=safe_sort_key, reverse=True)
            
            return cases_list
            
        except Exception as e:
            self.logger.error(f"Error getting all cases: {str(e)}")
            return []
    
    def _format_status(self, status) -> str:
        """Format status value for web display"""
        if isinstance(status, str):
            if 'CaseStatus.' in status:
                return status.split('.')[-1].lower()
            elif 'OPEN' in status:
                return 'open'
            elif 'IN_PROGRESS' in status:
                return 'in_progress'
            elif 'CLOSED' in status:
                return 'closed'
            else:
                return status.lower()
        else:
            return str(status).lower()
    
    def _format_priority(self, priority) -> str:
        """Format priority value for web display"""
        if isinstance(priority, str):
            if 'PriorityLevel.' in priority:
                return priority.split('.')[-1].lower()
            else:
                return priority.lower()
        else:
            return str(priority).lower()
    
    def create_case_simple(self, name: str, description: str, priority: str = "medium", 
                          created_by: str = "Web Dashboard", assigned_to: str = "") -> str:
        """Simplified case creation method for web interface"""
        try:
            # Generate case number
            case_number = f"CASE-{datetime.now().strftime('%Y%m%d')}-{len(self.cases) + 1:03d}"
            
            # Convert priority string to PriorityLevel enum
            priority_map = {
                'low': PriorityLevel.LOW,
                'medium': PriorityLevel.MEDIUM,
                'high': PriorityLevel.HIGH,
                'critical': PriorityLevel.CRITICAL
            }
            priority_level = priority_map.get(priority.lower(), PriorityLevel.MEDIUM)
            
            # Use the existing create_case method
            case_id = self.create_case(
                case_number=case_number,
                title=name,
                description=description,
                created_by=created_by,
                priority=priority_level,
                assigned_to=assigned_to
            )
            
            return case_id
            
        except Exception as e:
            self.logger.error(f"Error in simplified case creation: {str(e)}")
            raise
