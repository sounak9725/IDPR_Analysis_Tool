#!/usr/bin/env python3
"""
Advanced Filtering System for IPDR Data
Features:
- Relevance scoring for communication sessions
- Automated noise reduction
- Priority-based filtering
- Custom filter templates
- Batch processing for large datasets
- Smart filtering algorithms
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
import json
import logging
from dataclasses import dataclass
from enum import Enum

class FilterPriority(Enum):
    """Filter priority levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

class FilterType(Enum):
    """Types of filters"""
    TIME_BASED = "time_based"
    FREQUENCY_BASED = "frequency_based"
    PATTERN_BASED = "pattern_based"
    RISK_BASED = "risk_based"
    CUSTOM = "custom"

@dataclass
class FilterCriteria:
    """Filter criteria configuration"""
    name: str
    filter_type: FilterType
    priority: FilterPriority
    criteria: Dict[str, Any]
    weight: float = 1.0
    description: str = ""
    is_active: bool = True

class AdvancedFilteringSystem:
    def __init__(self):
        self.filters = []
        self.filter_templates = self._load_default_templates()
        self.noise_reduction_config = self._load_noise_reduction_config()
        self.relevance_weights = self._load_relevance_weights()
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def _load_default_templates(self) -> Dict[str, FilterCriteria]:
        """Load default filter templates"""
        return {
            'law_enforcement_critical': FilterCriteria(
                name="Law Enforcement Critical",
                filter_type=FilterType.RISK_BASED,
                priority=FilterPriority.CRITICAL,
                criteria={
                    'min_risk_score': 70,
                    'suspicious_patterns': True,
                    'high_frequency': True,
                    'late_night_activity': True
                },
                weight=2.0,
                description="Critical filters for law enforcement investigations"
            ),
            'suspicious_activity': FilterCriteria(
                name="Suspicious Activity",
                filter_type=FilterType.PATTERN_BASED,
                priority=FilterPriority.HIGH,
                criteria={
                    'burner_phone_patterns': True,
                    'unusual_timing': True,
                    'high_volume_communications': True
                },
                weight=1.5,
                description="Detect suspicious communication patterns"
            ),
            'network_analysis': FilterCriteria(
                name="Network Analysis",
                filter_type=FilterType.FREQUENCY_BASED,
                priority=FilterPriority.MEDIUM,
                criteria={
                    'min_connections': 5,
                    'centrality_threshold': 0.3,
                    'cluster_detection': True
                },
                weight=1.0,
                description="Focus on network analysis relevant data"
            ),
            'time_based_analysis': FilterCriteria(
                name="Time-based Analysis",
                filter_type=FilterType.TIME_BASED,
                priority=FilterPriority.MEDIUM,
                criteria={
                    'peak_hours': True,
                    'weekend_activity': True,
                    'holiday_patterns': True
                },
                weight=0.8,
                description="Analyze temporal communication patterns"
            )
        }
    
    def _load_noise_reduction_config(self) -> Dict:
        """Load noise reduction configuration"""
        return {
            'duplicate_threshold': 0.95,  # 95% similarity for duplicates
            'noise_patterns': [
                'test', 'demo', 'sample', 'example',
                '0000000000', '1111111111', '9999999999'
            ],
            'min_duration_threshold': 1,  # Minimum call duration in seconds
            'max_duration_threshold': 3600,  # Maximum call duration in seconds
            'valid_service_types': ['VOICE', 'SMS', 'DATA', 'MMS'],
            'geographic_noise_filters': {
                'max_distance_km': 1000,  # Maximum realistic distance
                'exclude_private_ips': True,
                'exclude_reserved_ips': True
            }
        }
    
    def _load_relevance_weights(self) -> Dict[str, float]:
        """Load relevance scoring weights"""
        return {
            'duration': 0.15,
            'frequency': 0.25,
            'timing': 0.20,
            'geographic': 0.15,
            'service_type': 0.10,
            'risk_score': 0.15
        }
    
    @property
    def active_filters(self) -> List[FilterCriteria]:
        """Get list of active filters"""
        return [f for f in self.filters if f.is_active]
    
    @property
    def active_filters_count(self) -> int:
        """Get count of active filters"""
        return len(self.active_filters)
    
    def add_filter(self, filter_criteria: FilterCriteria) -> None:
        """Add a new filter to the system"""
        self.filters.append(filter_criteria)
        self.logger.info(f"Added filter: {filter_criteria.name}")
    
    def remove_filter(self, filter_name: str) -> bool:
        """Remove a filter by name"""
        for i, filter_obj in enumerate(self.filters):
            if filter_obj.name == filter_name:
                del self.filters[i]
                self.logger.info(f"Removed filter: {filter_name}")
                return True
        return False
    
    def apply_template(self, template_name: str) -> bool:
        """Apply a predefined filter template"""
        if template_name in self.filter_templates:
            template = self.filter_templates[template_name]
            self.add_filter(template)
            return True
        return False
    
    def calculate_relevance_score(self, row: pd.Series, context: Dict = None) -> float:
        """
        Calculate relevance score for a single IPDR record
        
        Args:
            row: Pandas Series containing IPDR data
            context: Additional context for scoring
        
        Returns:
            Relevance score between 0 and 1
        """
        try:
            score = 0.0
            weights = self.relevance_weights
            
            # Duration relevance
            if 'duration' in row and pd.notna(row['duration']):
                duration_score = self._calculate_duration_score(row['duration'])
                score += duration_score * weights['duration']
            
            # Frequency relevance
            if context and 'entity_frequency' in context:
                freq_score = self._calculate_frequency_score(context['entity_frequency'])
                score += freq_score * weights['frequency']
            
            # Timing relevance
            if 'timestamp' in row and pd.notna(row['timestamp']):
                timing_score = self._calculate_timing_score(row['timestamp'])
                score += timing_score * weights['timing']
            
            # Geographic relevance
            if context and 'geographic_context' in context:
                geo_score = self._calculate_geographic_score(context['geographic_context'])
                score += geo_score * weights['geographic']
            
            # Service type relevance
            if 'service_type' in row and pd.notna(row['service_type']):
                service_score = self._calculate_service_score(row['service_type'])
                score += service_score * weights['service_type']
            
            # Risk score relevance
            if context and 'risk_score' in context:
                risk_score = self._calculate_risk_score_relevance(context['risk_score'])
                score += risk_score * weights['risk_score']
            
            return min(max(score, 0.0), 1.0)
            
        except Exception as e:
            self.logger.error(f"Error calculating relevance score: {str(e)}")
            return 0.0
    
    def _calculate_duration_score(self, duration: float) -> float:
        """Calculate relevance score based on call duration"""
        if duration < 1:  # Very short calls
            return 0.3
        elif duration < 30:  # Short calls
            return 0.6
        elif duration < 300:  # Normal calls
            return 1.0
        elif duration < 1800:  # Long calls
            return 0.8
        else:  # Very long calls
            return 0.4
    
    def _calculate_frequency_score(self, frequency: int) -> float:
        """Calculate relevance score based on entity frequency"""
        if frequency == 1:  # Single communication
            return 0.5
        elif frequency <= 5:  # Low frequency
            return 0.7
        elif frequency <= 20:  # Medium frequency
            return 1.0
        elif frequency <= 100:  # High frequency
            return 0.8
        else:  # Very high frequency
            return 0.6
    
    def _calculate_timing_score(self, timestamp: Any) -> float:
        """Calculate relevance score based on timing"""
        try:
            if isinstance(timestamp, str):
                dt = pd.to_datetime(timestamp)
            else:
                dt = timestamp
            
            hour = dt.hour
            weekday = dt.weekday()
            
            # Late night activity (suspicious)
            if 22 <= hour or hour <= 6:
                return 1.0
            
            # Weekend activity
            if weekday >= 5:
                return 0.8
            
            # Business hours
            if 9 <= hour <= 17:
                return 0.6
            
            # Regular hours
            return 0.7
            
        except Exception as e:
            self.logger.warning(f"Error calculating timing score: {str(e)}")
            return 0.5
    
    def _calculate_geographic_score(self, geo_context: Dict) -> float:
        """Calculate relevance score based on geographic context"""
        score = 0.5  # Base score
        
        # Distance-based scoring
        if 'distance_km' in geo_context:
            distance = geo_context['distance_km']
            if distance > 1000:  # Long distance
                score += 0.3
            elif distance > 100:  # Medium distance
                score += 0.2
            else:  # Local
                score += 0.1
        
        # Cross-border communication
        if geo_context.get('cross_border', False):
            score += 0.2
        
        # International communication
        if geo_context.get('international', False):
            score += 0.3
        
        return min(score, 1.0)
    
    def _calculate_service_score(self, service_type: str) -> float:
        """Calculate relevance score based on service type"""
        service_scores = {
            'VOICE': 1.0,    # Most relevant for investigations
            'SMS': 0.9,      # Very relevant
            'MMS': 0.8,      # Relevant
            'DATA': 0.6,     # Less relevant
            'ROAMING': 0.7,  # Relevant for location tracking
            'UNKNOWN': 0.5   # Neutral
        }
        return service_scores.get(service_type.upper(), 0.5)
    
    def _calculate_risk_score_relevance(self, risk_score: float) -> float:
        """Calculate relevance score based on risk score"""
        if risk_score >= 80:
            return 1.0
        elif risk_score >= 60:
            return 0.8
        elif risk_score >= 40:
            return 0.6
        elif risk_score >= 20:
            return 0.4
        else:
            return 0.2
    
    def apply_filters(self, df: pd.DataFrame, context: Dict = None) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Apply all active filters to the dataset
        
        Args:
            df: Input DataFrame
            context: Additional context for filtering
        
        Returns:
            Tuple of (filtered_data, filtered_out_data)
        """
        try:
            if df.empty:
                return df, df
            
            # Calculate relevance scores
            df['relevance_score'] = df.apply(
                lambda row: self.calculate_relevance_score(row, context), axis=1
            )
            
            # Apply noise reduction
            df_clean = self._apply_noise_reduction(df)
            
            # Apply active filters
            filtered_data = df_clean.copy()
            filtered_out = pd.DataFrame()
            
            for filter_obj in self.filters:
                if filter_obj.is_active:
                    filtered_data, removed_data = self._apply_single_filter(
                        filtered_data, filter_obj, context
                    )
                    if not removed_data.empty:
                        filtered_out = pd.concat([filtered_out, removed_data], ignore_index=True)
            
            # Sort by relevance score
            filtered_data = filtered_data.sort_values('relevance_score', ascending=False)
            
            self.logger.info(f"Filtering complete: {len(filtered_data)} records kept, {len(filtered_out)} filtered out")
            
            return filtered_data, filtered_out
            
        except Exception as e:
            self.logger.error(f"Error applying filters: {str(e)}")
            return df, pd.DataFrame()
    
    def _apply_noise_reduction(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply noise reduction algorithms"""
        try:
            df_clean = df.copy()
            config = self.noise_reduction_config
            
            # Remove duplicates
            df_clean = self._remove_duplicates(df_clean, config['duplicate_threshold'])
            
            # Filter by duration
            if 'duration' in df_clean.columns:
                df_clean = df_clean[
                    (df_clean['duration'] >= config['min_duration_threshold']) &
                    (df_clean['duration'] <= config['max_duration_threshold'])
                ]
            
            # Filter by service type
            if 'service_type' in df_clean.columns:
                df_clean = df_clean[
                    df_clean['service_type'].isin(config['valid_service_types'])
                ]
            
            # Remove noise patterns
            df_clean = self._remove_noise_patterns(df_clean, config['noise_patterns'])
            
            # Apply geographic filters
            df_clean = self._apply_geographic_filters(df_clean, config['geographic_noise_filters'])
            
            return df_clean
            
        except Exception as e:
            self.logger.error(f"Error in noise reduction: {str(e)}")
            return df
    
    def _remove_duplicates(self, df: pd.DataFrame, similarity_threshold: float) -> pd.DataFrame:
        """Remove duplicate records based on similarity threshold"""
        try:
            # Simple duplicate removal based on key columns
            key_columns = ['a_party', 'b_party', 'timestamp', 'duration', 'service_type']
            available_columns = [col for col in key_columns if col in df.columns]
            
            if available_columns:
                df_clean = df.drop_duplicates(subset=available_columns, keep='first')
                return df_clean
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error removing duplicates: {str(e)}")
            return df
    
    def _remove_noise_patterns(self, df: pd.DataFrame, noise_patterns: List[str]) -> pd.DataFrame:
        """Remove records matching noise patterns"""
        try:
            df_clean = df.copy()
            
            for pattern in noise_patterns:
                # Check in a_party and b_party columns
                for col in ['a_party', 'b_party']:
                    if col in df_clean.columns:
                        mask = df_clean[col].astype(str).str.contains(pattern, case=False, na=False)
                        df_clean = df_clean[~mask]
            
            return df_clean
            
        except Exception as e:
            self.logger.error(f"Error removing noise patterns: {str(e)}")
            return df
    
    def _apply_geographic_filters(self, df: pd.DataFrame, geo_config: Dict) -> pd.DataFrame:
        """Apply geographic-based noise filters"""
        try:
            df_clean = df.copy()
            
            # This would typically involve IP geolocation analysis
            # For now, we'll implement basic filters
            
            if geo_config.get('exclude_private_ips', False):
                # Filter out private IP addresses
                if 'b_party' in df_clean.columns:
                    # Simple private IP detection
                    private_ip_mask = df_clean['b_party'].astype(str).str.match(
                        r'^(10\.|172\.(1[6-9]|2[0-9]|3[0-1])\.|192\.168\.)'
                    )
                    df_clean = df_clean[~private_ip_mask]
            
            return df_clean
            
        except Exception as e:
            self.logger.error(f"Error applying geographic filters: {str(e)}")
            return df
    
    def _apply_single_filter(self, df: pd.DataFrame, filter_obj: FilterCriteria, context: Dict) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Apply a single filter to the dataset"""
        try:
            df_filtered = df.copy()
            df_removed = pd.DataFrame()
            
            if filter_obj.filter_type == FilterType.RISK_BASED:
                df_filtered, df_removed = self._apply_risk_based_filter(df, filter_obj, context)
            elif filter_obj.filter_type == FilterType.PATTERN_BASED:
                df_filtered, df_removed = self._apply_pattern_based_filter(df, filter_obj, context)
            elif filter_obj.filter_type == FilterType.FREQUENCY_BASED:
                df_filtered, df_removed = self._apply_frequency_based_filter(df, filter_obj, context)
            elif filter_obj.filter_type == FilterType.TIME_BASED:
                df_filtered, df_removed = self._apply_time_based_filter(df, filter_obj, context)
            elif filter_obj.filter_type == FilterType.CUSTOM:
                df_filtered, df_removed = self._apply_custom_filter(df, filter_obj, context)
            
            return df_filtered, df_removed
            
        except Exception as e:
            self.logger.error(f"Error applying filter {filter_obj.name}: {str(e)}")
            return df, pd.DataFrame()
    
    def _apply_risk_based_filter(self, df: pd.DataFrame, filter_obj: FilterCriteria, context: Dict) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Apply risk-based filtering"""
        try:
            criteria = filter_obj.criteria
            df_filtered = df.copy()
            df_removed = pd.DataFrame()
            
            # Filter by risk score
            if 'min_risk_score' in criteria and 'relevance_score' in df.columns:
                min_score = criteria['min_risk_score'] / 100.0  # Convert to 0-1 scale
                mask = df_filtered['relevance_score'] >= min_score
                df_removed = df_filtered[~mask]
                df_filtered = df_filtered[mask]
            
            # Filter by suspicious patterns
            if criteria.get('suspicious_patterns', False):
                # This would involve more sophisticated pattern detection
                # For now, we'll use relevance score as a proxy
                pass
            
            return df_filtered, df_removed
            
        except Exception as e:
            self.logger.error(f"Error in risk-based filtering: {str(e)}")
            return df, pd.DataFrame()
    
    def _apply_pattern_based_filter(self, df: pd.DataFrame, filter_obj: FilterCriteria, context: Dict) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Apply pattern-based filtering"""
        try:
            criteria = filter_obj.criteria
            df_filtered = df.copy()
            df_removed = pd.DataFrame()
            
            # Filter by burner phone patterns
            if criteria.get('burner_phone_patterns', False):
                # Simple burner phone detection
                if 'b_party' in df.columns:
                    # Check for repeated digits
                    def is_burner_pattern(value):
                        if pd.isna(value):
                            return False
                        str_val = str(value)
                        if len(str_val) >= 10:
                            unique_digits = len(set(str_val))
                            return unique_digits <= 3
                        return False
                    
                    mask = df_filtered['b_party'].apply(is_burner_pattern)
                    df_removed = pd.concat([df_removed, df_filtered[mask]], ignore_index=True)
                    df_filtered = df_filtered[~mask]
            
            return df_filtered, df_removed
            
        except Exception as e:
            self.logger.error(f"Error in pattern-based filtering: {str(e)}")
            return df, pd.DataFrame()
    
    def _apply_frequency_based_filter(self, df: pd.DataFrame, filter_obj: FilterCriteria, context: Dict) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Apply frequency-based filtering"""
        try:
            criteria = filter_obj.criteria
            df_filtered = df.copy()
            df_removed = pd.DataFrame()
            
            # Filter by minimum connections
            if 'min_connections' in criteria:
                min_conn = criteria['min_connections']
                if 'a_party' in df.columns:
                    # Count connections per party
                    party_counts = df_filtered['a_party'].value_counts()
                    parties_with_min_conn = party_counts[party_counts >= min_conn].index
                    mask = df_filtered['a_party'].isin(parties_with_min_conn)
                    df_removed = df_filtered[~mask]
                    df_filtered = df_filtered[mask]
            
            return df_filtered, df_removed
            
        except Exception as e:
            self.logger.error(f"Error in frequency-based filtering: {str(e)}")
            return df, pd.DataFrame()
    
    def _apply_time_based_filter(self, df: pd.DataFrame, filter_obj: FilterCriteria, context: Dict) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Apply time-based filtering"""
        try:
            criteria = filter_obj.criteria
            df_filtered = df.copy()
            df_removed = pd.DataFrame()
            
            if 'timestamp' in df.columns:
                # Convert timestamp to datetime if needed
                if df_filtered['timestamp'].dtype == 'object':
                    df_filtered['timestamp'] = pd.to_datetime(df_filtered['timestamp'], errors='coerce')
                
                # Filter by peak hours
                if criteria.get('peak_hours', False):
                    df_filtered['hour'] = df_filtered['timestamp'].dt.hour
                    mask = (df_filtered['hour'] >= 9) & (df_filtered['hour'] <= 17)
                    df_removed = pd.concat([df_removed, df_filtered[~mask]], ignore_index=True)
                    df_filtered = df_filtered[mask]
                    df_filtered = df_filtered.drop('hour', axis=1)
            
            return df_filtered, df_removed
            
        except Exception as e:
            self.logger.error(f"Error in time-based filtering: {str(e)}")
            return df, pd.DataFrame()
    
    def _apply_custom_filter(self, df: pd.DataFrame, filter_obj: FilterCriteria, context: Dict) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Apply custom filter criteria"""
        try:
            criteria = filter_obj.criteria
            df_filtered = df.copy()
            df_removed = pd.DataFrame()
            
            # Apply custom criteria based on the filter configuration
            for column, condition in criteria.items():
                if column in df.columns:
                    if isinstance(condition, dict):
                        # Range condition
                        if 'min' in condition and 'max' in condition:
                            mask = (df_filtered[column] >= condition['min']) & (df_filtered[column] <= condition['max'])
                            df_removed = pd.concat([df_removed, df_filtered[~mask]], ignore_index=True)
                            df_filtered = df_filtered[mask]
                        elif 'values' in condition:
                            # Value list condition
                            mask = df_filtered[column].isin(condition['values'])
                            df_removed = pd.concat([df_removed, df_filtered[~mask]], ignore_index=True)
                            df_filtered = df_filtered[mask]
                    else:
                        # Simple equality condition
                        mask = df_filtered[column] == condition
                        df_removed = pd.concat([df_removed, df_filtered[~mask]], ignore_index=True)
                        df_filtered = df_filtered[mask]
            
            return df_filtered, df_removed
            
        except Exception as e:
            self.logger.error(f"Error in custom filtering: {str(e)}")
            return df, pd.DataFrame()
    
    def generate_filter_report(self, original_df: pd.DataFrame, filtered_df: pd.DataFrame, filtered_out_df: pd.DataFrame) -> Dict:
        """Generate comprehensive report on filtering results"""
        try:
            total_records = len(original_df)
            kept_records = len(filtered_df)
            removed_records = len(filtered_out_df)
            
            # Calculate statistics
            if 'relevance_score' in filtered_df.columns:
                avg_relevance = filtered_df['relevance_score'].mean()
                min_relevance = filtered_df['relevance_score'].min()
                max_relevance = filtered_df['relevance_score'].max()
            else:
                avg_relevance = min_relevance = max_relevance = 0
            
            # Filter effectiveness
            effectiveness = (kept_records / total_records) * 100 if total_records > 0 else 0
            
            # Active filters summary
            active_filters = [f.name for f in self.filters if f.is_active]
            
            report = {
                'summary': {
                    'total_records': total_records,
                    'kept_records': kept_records,
                    'removed_records': removed_records,
                    'effectiveness_percentage': round(effectiveness, 2)
                },
                'relevance_scores': {
                    'average': round(avg_relevance, 3),
                    'minimum': round(min_relevance, 3),
                    'maximum': round(max_relevance, 3)
                },
                'active_filters': active_filters,
                'filter_configuration': [
                    {
                        'name': f.name,
                        'type': f.filter_type.value,
                        'priority': f.priority.value,
                        'weight': f.weight,
                        'description': f.description
                    }
                    for f in self.filters if f.is_active
                ],
                'generated_at': datetime.now().isoformat()
            }
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating filter report: {str(e)}")
            return {'error': str(e)}
    
    def save_filter_configuration(self, filepath: str) -> bool:
        """Save current filter configuration to file"""
        try:
            config = {
                'filters': [
                    {
                        'name': f.name,
                        'filter_type': f.filter_type.value,
                        'priority': f.priority.value,
                        'criteria': f.criteria,
                        'weight': f.weight,
                        'description': f.description,
                        'is_active': f.is_active
                    }
                    for f in self.filters
                ],
                'saved_at': datetime.now().isoformat()
            }
            
            with open(filepath, 'w') as f:
                json.dump(config, f, indent=2)
            
            self.logger.info(f"Filter configuration saved to {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving filter configuration: {str(e)}")
            return False
    
    def load_filter_configuration(self, filepath: str) -> bool:
        """Load filter configuration from file"""
        try:
            with open(filepath, 'r') as f:
                config = json.load(f)
            
            # Clear existing filters
            self.filters.clear()
            
            # Load filters from configuration
            for filter_config in config.get('filters', []):
                filter_criteria = FilterCriteria(
                    name=filter_config['name'],
                    filter_type=FilterType(filter_config['filter_type']),
                    priority=FilterPriority(filter_config['priority']),
                    criteria=filter_config['criteria'],
                    weight=filter_config['weight'],
                    description=filter_config['description'],
                    is_active=filter_config['is_active']
                )
                self.filters.append(filter_criteria)
            
            self.logger.info(f"Filter configuration loaded from {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading filter configuration: {str(e)}")
            return False
