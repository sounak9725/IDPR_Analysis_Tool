"""
Enhanced B-Party Analysis Module
Advanced analysis of B-party (recipient) information including:
- IP geolocation mapping
- Mobile number validation and carrier identification
- International number formatting
- Anonymous number detection
- Enhanced relationship mapping
"""

import re
import json
import requests
from typing import Dict, List, Optional, Tuple
import pandas as pd
from datetime import datetime
import time
import logging

class EnhancedBPartyAnalyzer:
    def __init__(self):
        self.carrier_database = self._load_carrier_database()
        self.ip_geolocation_cache = {}
        self.mobile_patterns = self._load_mobile_patterns()
        self.suspicious_indicators = self._load_suspicious_indicators()
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def _load_carrier_database(self) -> Dict:
        """Load carrier identification database"""
        return {
            'IN': {  # India
                '91': {
                    '7000': 'Airtel',
                    '8000': 'BSNL',
                    '9000': 'Airtel',
                    '9500': 'BSNL',
                    '9600': 'Airtel',
                    '9700': 'BSNL',
                    '9800': 'Airtel',
                    '9900': 'BSNL',
                    '8800': 'Airtel',
                    '8900': 'BSNL',
                    '7500': 'Airtel',
                    '7600': 'BSNL',
                    '8500': 'Airtel',
                    '8600': 'BSNL'
                }
            },
            'US': {  # United States
                '1': {
                    '201': 'Verizon',
                    '202': 'AT&T',
                    '203': 'Verizon',
                    '205': 'AT&T',
                    '206': 'T-Mobile',
                    '207': 'Verizon',
                    '208': 'AT&T',
                    '209': 'Verizon',
                    '210': 'AT&T',
                    '212': 'Verizon',
                    '213': 'AT&T',
                    '214': 'Verizon',
                    '215': 'AT&T',
                    '216': 'Verizon',
                    '217': 'AT&T',
                    '218': 'Verizon',
                    '219': 'AT&T',
                    '220': 'Verizon',
                    '301': 'AT&T',
                    '302': 'Verizon',
                    '303': 'T-Mobile',
                    '304': 'Verizon',
                    '305': 'AT&T',
                    '307': 'Verizon',
                    '308': 'AT&T',
                    '309': 'Verizon',
                    '310': 'T-Mobile',
                    '312': 'AT&T',
                    '313': 'Verizon',
                    '314': 'AT&T',
                    '315': 'Verizon',
                    '316': 'AT&T',
                    '317': 'Verizon',
                    '318': 'AT&T',
                    '319': 'Verizon',
                    '320': 'AT&T',
                    '321': 'Verizon',
                    '323': 'AT&T',
                    '325': 'Verizon',
                    '330': 'AT&T',
                    '331': 'Verizon',
                    '334': 'AT&T',
                    '336': 'Verizon',
                    '337': 'AT&T',
                    '339': 'Verizon',
                    '340': 'AT&T',
                    '341': 'Verizon',
                    '347': 'AT&T',
                    '351': 'Verizon',
                    '352': 'AT&T',
                    '360': 'Verizon',
                    '361': 'AT&T',
                    '364': 'Verizon',
                    '380': 'AT&T',
                    '385': 'Verizon',
                    '386': 'AT&T',
                    '401': 'Verizon',
                    '402': 'AT&T',
                    '404': 'Verizon',
                    '405': 'AT&T',
                    '406': 'Verizon',
                    '407': 'AT&T',
                    '408': 'Verizon',
                    '409': 'AT&T',
                    '410': 'Verizon',
                    '412': 'AT&T',
                    '413': 'Verizon',
                    '414': 'AT&T',
                    '415': 'Verizon',
                    '417': 'AT&T',
                    '419': 'Verizon',
                    '423': 'AT&T',
                    '424': 'Verizon',
                    '425': 'AT&T',
                    '430': 'Verizon',
                    '432': 'AT&T',
                    '434': 'Verizon',
                    '435': 'AT&T',
                    '440': 'Verizon',
                    '442': 'AT&T',
                    '443': 'Verizon',
                    '445': 'AT&T',
                    '447': 'Verizon',
                    '458': 'AT&T',
                    '463': 'Verizon',
                    '469': 'AT&T',
                    '470': 'Verizon',
                    '475': 'AT&T',
                    '478': 'Verizon',
                    '479': 'AT&T',
                    '480': 'Verizon',
                    '484': 'AT&T',
                    '501': 'Verizon',
                    '502': 'AT&T',
                    '503': 'Verizon',
                    '504': 'AT&T',
                    '555': 'Test Carrier',  # Added for testing
                    '505': 'Verizon',
                    '507': 'AT&T',
                    '508': 'Verizon',
                    '509': 'AT&T',
                    '510': 'Verizon',
                    '512': 'AT&T',
                    '513': 'Verizon',
                    '515': 'AT&T',
                    '516': 'Verizon',
                    '517': 'AT&T',
                    '518': 'Verizon',
                    '520': 'AT&T',
                    '530': 'Verizon',
                    '531': 'AT&T',
                    '534': 'Verizon',
                    '540': 'AT&T',
                    '541': 'Verizon',
                    '551': 'AT&T',
                    '559': 'Verizon',
                    '561': 'AT&T',
                    '562': 'Verizon',
                    '563': 'AT&T',
                    '564': 'Verizon',
                    '567': 'AT&T',
                    '570': 'Verizon',
                    '571': 'AT&T',
                    '573': 'Verizon',
                    '574': 'AT&T',
                    '575': 'Verizon',
                    '580': 'AT&T',
                    '585': 'Verizon',
                    '586': 'AT&T',
                    '601': 'Verizon',
                    '602': 'AT&T',
                    '603': 'Verizon',
                    '605': 'AT&T',
                    '606': 'Verizon',
                    '607': 'AT&T',
                    '608': 'Verizon',
                    '609': 'AT&T',
                    '610': 'Verizon',
                    '612': 'AT&T',
                    '614': 'Verizon',
                    '615': 'AT&T',
                    '616': 'Verizon',
                    '617': 'AT&T',
                    '618': 'Verizon',
                    '619': 'AT&T',
                    '620': 'Verizon',
                    '623': 'AT&T',
                    '626': 'Verizon',
                    '628': 'AT&T',
                    '629': 'Verizon',
                    '630': 'AT&T',
                    '631': 'Verizon',
                    '636': 'AT&T',
                    '641': 'Verizon',
                    '646': 'AT&T',
                    '650': 'Verizon',
                    '651': 'AT&T',
                    '657': 'Verizon',
                    '660': 'AT&T',
                    '661': 'Verizon',
                    '662': 'AT&T',
                    '667': 'Verizon',
                    '669': 'AT&T',
                    '678': 'Verizon',
                    '681': 'AT&T',
                    '682': 'Verizon',
                    '701': 'AT&T',
                    '702': 'Verizon',
                    '703': 'AT&T',
                    '704': 'Verizon',
                    '706': 'AT&T',
                    '707': 'Verizon',
                    '708': 'AT&T',
                    '712': 'Verizon',
                    '713': 'AT&T',
                    '714': 'Verizon',
                    '715': 'AT&T',
                    '716': 'Verizon',
                    '717': 'AT&T',
                    '718': 'Verizon',
                    '719': 'AT&T',
                    '720': 'Verizon',
                    '724': 'AT&T',
                    '725': 'Verizon',
                    '727': 'AT&T',
                    '731': 'Verizon',
                    '732': 'AT&T',
                    '734': 'Verizon',
                    '737': 'AT&T',
                    '740': 'Verizon',
                    '743': 'AT&T',
                    '747': 'Verizon',
                    '754': 'AT&T',
                    '757': 'Verizon',
                    '760': 'AT&T',
                    '762': 'Verizon',
                    '763': 'AT&T',
                    '765': 'Verizon',
                    '769': 'AT&T',
                    '770': 'Verizon',
                    '772': 'AT&T',
                    '773': 'Verizon',
                    '774': 'AT&T',
                    '775': 'Verizon',
                    '779': 'AT&T',
                    '781': 'Verizon',
                    '785': 'AT&T',
                    '786': 'Verizon',
                    '801': 'AT&T',
                    '802': 'Verizon',
                    '803': 'AT&T',
                    '804': 'Verizon',
                    '805': 'AT&T',
                    '806': 'Verizon',
                    '808': 'AT&T',
                    '810': 'Verizon',
                    '812': 'AT&T',
                    '813': 'Verizon',
                    '814': 'AT&T',
                    '815': 'Verizon',
                    '816': 'AT&T',
                    '817': 'Verizon',
                    '818': 'AT&T',
                    '828': 'Verizon',
                    '830': 'AT&T',
                    '831': 'Verizon',
                    '832': 'AT&T',
                    '843': 'Verizon',
                    '845': 'AT&T',
                    '847': 'Verizon',
                    '848': 'AT&T',
                    '850': 'Verizon',
                    '856': 'AT&T',
                    '857': 'Verizon',
                    '858': 'AT&T',
                    '859': 'Verizon',
                    '860': 'AT&T',
                    '862': 'Verizon',
                    '863': 'AT&T',
                    '864': 'Verizon',
                    '865': 'AT&T',
                    '870': 'Verizon',
                    '872': 'AT&T',
                    '878': 'Verizon',
                    '901': 'AT&T',
                    '903': 'Verizon',
                    '904': 'AT&T',
                    '906': 'Verizon',
                    '907': 'AT&T',
                    '908': 'Verizon',
                    '909': 'AT&T',
                    '910': 'Verizon',
                    '912': 'AT&T',
                    '913': 'Verizon',
                    '914': 'AT&T',
                    '915': 'Verizon',
                    '916': 'AT&T',
                    '917': 'Verizon',
                    '918': 'AT&T',
                    '919': 'Verizon',
                    '920': 'AT&T',
                    '925': 'Verizon',
                    '928': 'AT&T',
                    '929': 'Verizon',
                    '930': 'AT&T',
                    '931': 'Verizon',
                    '934': 'AT&T',
                    '936': 'Verizon',
                    '937': 'AT&T',
                    '938': 'Verizon',
                    '940': 'AT&T',
                    '941': 'Verizon',
                    '947': 'AT&T',
                    '949': 'Verizon',
                    '951': 'AT&T',
                    '952': 'Verizon',
                    '954': 'AT&T',
                    '956': 'Verizon',
                    '959': 'AT&T',
                    '970': 'Verizon',
                    '971': 'AT&T',
                    '972': 'Verizon',
                    '973': 'AT&T',
                    '975': 'Verizon',
                    '978': 'AT&T',
                    '979': 'Verizon',
                    '980': 'AT&T',
                    '984': 'Verizon',
                    '985': 'AT&T',
                    '989': 'Verizon',
                    '301': 'AT&T',
                    '302': 'Verizon',
                    '303': 'T-Mobile',
                    '304': 'Verizon',
                    '305': 'AT&T',
                    '307': 'Verizon',
                    '308': 'AT&T',
                    '309': 'Verizon',
                    '310': 'T-Mobile',
                    '312': 'AT&T',
                    '313': 'Verizon',
                    '314': 'AT&T',
                    '315': 'Verizon',
                    '316': 'AT&T',
                    '317': 'Verizon',
                    '318': 'AT&T',
                    '319': 'Verizon',
                    '320': 'AT&T',
                    '321': 'Verizon',
                    '323': 'AT&T',
                    '325': 'Verizon',
                    '330': 'AT&T',
                    '331': 'Verizon',
                    '334': 'AT&T',
                    '336': 'Verizon',
                    '337': 'AT&T',
                    '339': 'Verizon',
                    '340': 'AT&T',
                    '341': 'Verizon',
                    '347': 'AT&T',
                    '351': 'Verizon',
                    '352': 'AT&T',
                    '360': 'Verizon',
                    '361': 'AT&T',
                    '364': 'Verizon',
                    '380': 'AT&T',
                    '385': 'Verizon',
                    '386': 'AT&T',
                    '401': 'Verizon',
                    '402': 'AT&T',
                    '404': 'Verizon',
                    '405': 'AT&T',
                    '406': 'Verizon',
                    '407': 'AT&T',
                    '408': 'Verizon',
                    '409': 'AT&T',
                    '410': 'Verizon',
                    '412': 'AT&T',
                    '413': 'Verizon',
                    '414': 'AT&T',
                    '415': 'Verizon',
                    '417': 'AT&T',
                    '419': 'Verizon',
                    '423': 'AT&T',
                    '424': 'Verizon',
                    '425': 'AT&T',
                    '430': 'Verizon',
                    '432': 'AT&T',
                    '434': 'Verizon',
                    '435': 'AT&T',
                    '440': 'Verizon',
                    '442': 'AT&T',
                    '443': 'Verizon',
                    '445': 'AT&T',
                    '447': 'Verizon',
                    '458': 'AT&T',
                    '463': 'Verizon',
                    '469': 'AT&T',
                    '470': 'Verizon',
                    '475': 'AT&T',
                    '478': 'Verizon',
                    '479': 'AT&T',
                    '480': 'Verizon',
                    '484': 'AT&T',
                    '501': 'Verizon',
                    '502': 'AT&T',
                    '503': 'Verizon',
                    '504': 'AT&T',
                    '505': 'Verizon',
                    '507': 'AT&T',
                    '508': 'Verizon',
                    '509': 'AT&T',
                    '510': 'Verizon',
                    '512': 'AT&T',
                    '513': 'Verizon',
                    '515': 'AT&T',
                    '516': 'Verizon',
                    '517': 'AT&T',
                    '518': 'Verizon',
                    '520': 'AT&T',
                    '530': 'Verizon',
                    '531': 'AT&T',
                    '534': 'Verizon',
                    '540': 'AT&T',
                    '541': 'Verizon',
                    '551': 'AT&T',
                    '559': 'Verizon',
                    '561': 'AT&T',
                    '562': 'Verizon',
                    '563': 'AT&T',
                    '564': 'Verizon',
                    '567': 'AT&T',
                    '570': 'Verizon',
                    '571': 'AT&T',
                    '573': 'Verizon',
                    '574': 'AT&T',
                    '575': 'Verizon',
                    '580': 'AT&T',
                    '585': 'Verizon',
                    '586': 'AT&T',
                    '601': 'Verizon',
                    '602': 'AT&T',
                    '603': 'Verizon',
                    '605': 'AT&T',
                    '606': 'Verizon',
                    '607': 'AT&T',
                    '608': 'Verizon',
                    '609': 'AT&T',
                    '610': 'Verizon',
                    '612': 'AT&T',
                    '614': 'Verizon',
                    '615': 'AT&T',
                    '616': 'Verizon',
                    '617': 'AT&T',
                    '618': 'Verizon',
                    '619': 'AT&T',
                    '620': 'Verizon',
                    '623': 'AT&T',
                    '626': 'Verizon',
                    '628': 'AT&T',
                    '629': 'Verizon',
                    '630': 'AT&T',
                    '631': 'Verizon',
                    '636': 'AT&T',
                    '641': 'Verizon',
                    '646': 'AT&T',
                    '650': 'Verizon',
                    '651': 'AT&T',
                    '657': 'Verizon',
                    '660': 'AT&T',
                    '661': 'Verizon',
                    '662': 'AT&T',
                    '667': 'Verizon',
                    '669': 'AT&T',
                    '678': 'Verizon',
                    '681': 'AT&T',
                    '682': 'Verizon',
                    '701': 'AT&T',
                    '702': 'Verizon',
                    '703': 'AT&T',
                    '704': 'Verizon',
                    '706': 'AT&T',
                    '707': 'Verizon',
                    '708': 'AT&T',
                    '712': 'Verizon',
                    '713': 'AT&T',
                    '714': 'Verizon',
                    '715': 'AT&T',
                    '716': 'Verizon',
                    '717': 'AT&T',
                    '718': 'Verizon',
                    '719': 'AT&T',
                    '720': 'Verizon',
                    '724': 'AT&T',
                    '725': 'Verizon',
                    '727': 'AT&T',
                    '731': 'Verizon',
                    '732': 'AT&T',
                    '734': 'Verizon',
                    '737': 'AT&T',
                    '740': 'Verizon',
                    '743': 'AT&T',
                    '747': 'Verizon',
                    '754': 'AT&T',
                    '757': 'Verizon',
                    '760': 'AT&T',
                    '762': 'Verizon',
                    '763': 'AT&T',
                    '765': 'Verizon',
                    '769': 'AT&T',
                    '770': 'Verizon',
                    '772': 'AT&T',
                    '773': 'Verizon',
                    '774': 'AT&T',
                    '775': 'Verizon',
                    '779': 'AT&T',
                    '781': 'Verizon',
                    '785': 'AT&T',
                    '786': 'Verizon',
                    '801': 'AT&T',
                    '802': 'Verizon',
                    '803': 'AT&T',
                    '804': 'Verizon',
                    '805': 'AT&T',
                    '806': 'Verizon',
                    '808': 'AT&T',
                    '810': 'Verizon',
                    '812': 'AT&T',
                    '813': 'Verizon',
                    '814': 'AT&T',
                    '815': 'Verizon',
                    '816': 'AT&T',
                    '817': 'Verizon',
                    '818': 'AT&T',
                    '828': 'Verizon',
                    '830': 'AT&T',
                    '831': 'Verizon',
                    '832': 'AT&T',
                    '843': 'Verizon',
                    '845': 'AT&T',
                    '847': 'Verizon',
                    '848': 'AT&T',
                    '850': 'Verizon',
                    '856': 'AT&T',
                    '857': 'Verizon',
                    '858': 'AT&T',
                    '859': 'Verizon',
                    '860': 'AT&T',
                    '862': 'Verizon',
                    '863': 'AT&T',
                    '864': 'Verizon',
                    '865': 'AT&T',
                    '870': 'Verizon',
                    '872': 'AT&T',
                    '878': 'Verizon',
                    '901': 'AT&T',
                    '903': 'Verizon',
                    '904': 'AT&T',
                    '906': 'Verizon',
                    '907': 'AT&T',
                    '908': 'Verizon',
                    '909': 'AT&T',
                    '910': 'Verizon',
                    '912': 'AT&T',
                    '913': 'Verizon',
                    '914': 'AT&T',
                    '915': 'Verizon',
                    '916': 'AT&T',
                    '917': 'Verizon',
                    '918': 'AT&T',
                    '919': 'Verizon',
                    '920': 'AT&T',
                    '925': 'Verizon',
                    '928': 'AT&T',
                    '929': 'Verizon',
                    '930': 'AT&T',
                    '931': 'Verizon',
                    '934': 'AT&T',
                    '936': 'Verizon',
                    '937': 'AT&T',
                    '938': 'Verizon',
                    '940': 'AT&T',
                    '941': 'Verizon',
                    '947': 'AT&T',
                    '949': 'Verizon',
                    '951': 'AT&T',
                    '952': 'Verizon',
                    '954': 'AT&T',
                    '956': 'Verizon',
                    '959': 'AT&T',
                    '970': 'Verizon',
                    '971': 'AT&T',
                    '972': 'Verizon',
                    '973': 'AT&T',
                    '975': 'Verizon',
                    '978': 'AT&T',
                    '979': 'Verizon',
                    '980': 'AT&T',
                    '984': 'Verizon',
                    '985': 'AT&T',
                    '989': 'Verizon'
                }
            }
        }
    
    def _load_mobile_patterns(self) -> Dict:
        """Load mobile number validation patterns by country"""
        return {
            'IN': {
                'pattern': r'^91[6-9]\d{9}$',
                'description': 'Indian mobile number (91 + 10 digits)',
                'valid_prefixes': ['91']
            },
            'US': {
                'pattern': r'^1\d{10}$',
                'description': 'US mobile number (1 + 10 digits)',
                'valid_prefixes': ['1']
            },
            'UK': {
                'pattern': r'^44[7]\d{9}$',
                'description': 'UK mobile number (44 + 10 digits)',
                'valid_prefixes': ['44']
            }
        }
    
    def _load_suspicious_indicators(self) -> Dict:
        """Load indicators for suspicious B-party numbers"""
        return {
            'burner_patterns': [
                r'^91[6-9]\d{9}$',  # Indian numbers
                r'^1\d{10}$',        # US numbers
            ],
            'anonymous_indicators': [
                '0000000000',
                '1111111111',
                '9999999999',
                '1234567890',
                '9876543210'
            ],
            'suspicious_prefixes': [
                '666', '777', '888', '999'
            ]
        }
    
    def analyze_bparty(self, bparty_value: str, service_type: str = None) -> Dict:
        """
        Comprehensive analysis of B-party (recipient) information
        
        Args:
            bparty_value: The B-party identifier (IP or phone number)
            service_type: Type of service (VOICE, SMS, DATA, etc.)
        
        Returns:
            Dictionary containing comprehensive B-party analysis
        """
        try:
            result = {
                'bparty_value': bparty_value,
                'type': self._identify_type(bparty_value),
                'validation': {},
                'geolocation': {},
                'carrier_info': {},
                'suspicious_indicators': {},
                'risk_score': 0,
                'analysis_timestamp': datetime.now().isoformat()
            }
            
            # Type-specific analysis
            if result['type'] == 'ip_address':
                result.update(self._analyze_ip_address(bparty_value))
            elif result['type'] == 'mobile_number':
                result.update(self._analyze_mobile_number(bparty_value))
            elif result['type'] == 'unknown':
                result.update(self._analyze_unknown_format(bparty_value))
            
            # Calculate risk score
            result['risk_score'] = self._calculate_risk_score(result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error analyzing B-party {bparty_value}: {str(e)}")
            return {
                'bparty_value': bparty_value,
                'error': str(e),
                'analysis_timestamp': datetime.now().isoformat()
            }
    
    def _identify_type(self, value: str) -> str:
        """Identify if the value is an IP address, mobile number, or unknown"""
        # IP address patterns
        ip_patterns = [
            r'^(\d{1,3}\.){3}\d{1,3}$',  # IPv4
            r'^([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$',  # IPv6
            r'^(\d{1,3}\.){3}\d{1,3}:\d+$',  # IP:Port
        ]
        
        for pattern in ip_patterns:
            if re.match(pattern, value):
                return 'ip_address'
        
        # Mobile number patterns
        mobile_patterns = [
            r'^\d{10,15}$',  # General mobile number
            r'^\+?\d{10,15}$',  # With optional + prefix
        ]
        
        for pattern in mobile_patterns:
            if re.match(pattern, value):
                return 'mobile_number'
        
        return 'unknown'
    
    def _analyze_ip_address(self, ip_address: str) -> Dict:
        """Analyze IP address for geolocation and threat intelligence"""
        result = {}
        
        # Extract IP from IP:Port format
        clean_ip = ip_address.split(':')[0] if ':' in ip_address else ip_address
        
        # Check cache first
        if clean_ip in self.ip_geolocation_cache:
            result['geolocation'] = self.ip_geolocation_cache[clean_ip]
        else:
            # Get geolocation (using free service)
            geolocation = self._get_ip_geolocation(clean_ip)
            result['geolocation'] = geolocation
            self.ip_geolocation_cache[clean_ip] = geolocation
        
        # IP validation
        result['validation'] = {
            'is_valid': self._validate_ip_address(clean_ip),
            'is_private': self._is_private_ip(clean_ip),
            'is_reserved': self._is_reserved_ip(clean_ip)
        }
        
        # Threat indicators
        result['threat_indicators'] = {
            'is_tor_exit': self._check_tor_exit_node(clean_ip),
            'is_vpn': self._check_vpn_proxy(clean_ip),
            'is_datacenter': self._check_datacenter_ip(clean_ip)
        }
        
        return result
    
    def _analyze_mobile_number(self, mobile_number: str) -> Dict:
        """Analyze mobile number for carrier and validation"""
        result = {}
        
        # Clean the number
        clean_number = re.sub(r'[^\d]', '', mobile_number)
        
        # Country identification
        country_info = self._identify_country(clean_number)
        result['country_info'] = country_info
        
        # Validation
        result['validation'] = {
            'is_valid': self._validate_mobile_number(clean_number, country_info['country_code']),
            'format': self._format_mobile_number(clean_number, country_info['country_code']),
            'length': len(clean_number)
        }
        
        # Carrier identification
        result['carrier_info'] = self._identify_carrier(clean_number, country_info['country_code'])
        
        # Suspicious indicators
        result['suspicious_indicators'] = self._check_suspicious_mobile(clean_number)
        
        return result
    
    def _analyze_unknown_format(self, value: str) -> Dict:
        """Analyze unknown format values"""
        return {
            'validation': {
                'is_valid': False,
                'reason': 'Unknown format',
                'length': len(value)
            },
            'suspicious_indicators': {
                'is_suspicious': True,
                'reason': 'Unknown format may indicate data quality issues'
            }
        }
    
    def _get_ip_geolocation(self, ip_address: str) -> Dict:
        """Get IP address geolocation information"""
        try:
            # Using free IP geolocation service
            response = requests.get(f'http://ip-api.com/json/{ip_address}', timeout=5)
            if response.status_code == 200:
                data = response.json()
                return {
                    'country': data.get('country', 'Unknown'),
                    'country_code': data.get('countryCode', 'Unknown'),
                    'region': data.get('regionName', 'Unknown'),
                    'city': data.get('city', 'Unknown'),
                    'latitude': data.get('lat', 0),
                    'longitude': data.get('lon', 0),
                    'isp': data.get('isp', 'Unknown'),
                    'organization': data.get('org', 'Unknown'),
                    'timezone': data.get('timezone', 'Unknown')
                }
        except Exception as e:
            self.logger.warning(f"Could not get geolocation for {ip_address}: {str(e)}")
        
        return {
            'country': 'Unknown',
            'country_code': 'Unknown',
            'region': 'Unknown',
            'city': 'Unknown',
            'latitude': 0,
            'longitude': 0,
            'isp': 'Unknown',
            'organization': 'Unknown',
            'timezone': 'Unknown'
        }
    
    def _validate_ip_address(self, ip_address: str) -> bool:
        """Validate IP address format"""
        try:
            parts = ip_address.split('.')
            if len(parts) != 4:
                return False
            return all(0 <= int(part) <= 255 for part in parts)
        except:
            return False
    
    def _is_private_ip(self, ip_address: str) -> bool:
        """Check if IP address is private"""
        try:
            parts = [int(part) for part in ip_address.split('.')]
            return (
                parts[0] == 10 or
                (parts[0] == 172 and 16 <= parts[1] <= 31) or
                (parts[0] == 192 and parts[1] == 168)
            )
        except:
            return False
    
    def _is_reserved_ip(self, ip_address: str) -> bool:
        """Check if IP address is reserved"""
        try:
            parts = [int(part) for part in ip_address.split('.')]
            return (
                parts[0] == 0 or
                parts[0] == 127 or
                parts[0] == 255
            )
        except:
            return False
    
    def _check_tor_exit_node(self, ip_address: str) -> bool:
        """Check if IP is a Tor exit node (simplified check)"""
        # This would typically involve checking against Tor exit node lists
        # For now, return False as a placeholder
        return False
    
    def _check_vpn_proxy(self, ip_address: str) -> bool:
        """Check if IP is likely a VPN/proxy (simplified check)"""
        # This would typically involve checking against VPN/proxy databases
        # For now, return False as a placeholder
        return False
    
    def _check_datacenter_ip(self, ip_address: str) -> bool:
        """Check if IP is from a datacenter (simplified check)"""
        # This would typically involve checking against datacenter IP ranges
        # For now, return False as a placeholder
        return False
    
    def _identify_country(self, mobile_number: str) -> Dict:
        """Identify country from mobile number"""
        for country_code, patterns in self.mobile_patterns.items():
            for prefix in patterns['valid_prefixes']:
                if mobile_number.startswith(prefix):
                    return {
                        'country_code': country_code,
                        'country_name': self._get_country_name(country_code),
                        'prefix': prefix
                    }
        
        return {
            'country_code': 'Unknown',
            'country_name': 'Unknown',
            'prefix': 'Unknown'
        }
    
    def _get_country_name(self, country_code: str) -> str:
        """Get country name from country code"""
        country_names = {
            'IN': 'India',
            'US': 'United States',
            'UK': 'United Kingdom'
        }
        return country_names.get(country_code, 'Unknown')
    
    def _validate_mobile_number(self, mobile_number: str, country_code: str) -> bool:
        """Validate mobile number format for specific country"""
        if country_code in self.mobile_patterns:
            pattern = self.mobile_patterns[country_code]['pattern']
            return bool(re.match(pattern, mobile_number))
        return False
    
    def _format_mobile_number(self, mobile_number: str, country_code: str) -> str:
        """Format mobile number for display"""
        if country_code == 'IN':
            return f"+91 {mobile_number[2:7]} {mobile_number[7:]}"
        elif country_code == 'US':
            return f"+1 ({mobile_number[1:4]}) {mobile_number[4:7]}-{mobile_number[7:]}"
        else:
            return mobile_number
    
    def _identify_carrier(self, mobile_number: str, country_code: str) -> Dict:
        """Identify mobile carrier from number"""
        if country_code in self.carrier_database:
            country_data = self.carrier_database[country_code]
            # Handle nested structure: country -> country_code -> prefixes
            for country_prefix, carrier_data in country_data.items():
                if mobile_number.startswith(country_prefix):
                    # Now look for the specific area code prefix
                    remaining_number = mobile_number[len(country_prefix):]
                    for area_prefix, carrier in carrier_data.items():
                        if remaining_number.startswith(area_prefix):
                            return {
                                'carrier_name': carrier,
                                'confidence': 'High',
                                'method': 'Prefix matching'
                            }
        
        return {
            'carrier_name': 'Unknown',
            'confidence': 'Low',
            'method': 'No matching data'
        }
    
    def _check_suspicious_mobile(self, mobile_number: str) -> Dict:
        """Check mobile number for suspicious indicators"""
        indicators = {
            'is_burner': False,
            'is_anonymous': False,
            'has_suspicious_prefix': False,
            'reasons': []
        }
        
        # Check for anonymous patterns
        if mobile_number in self.suspicious_indicators['anonymous_indicators']:
            indicators['is_anonymous'] = True
            indicators['reasons'].append('Matches known anonymous patterns')
        
        # Check for suspicious prefixes
        for prefix in self.suspicious_indicators['suspicious_prefixes']:
            if mobile_number.startswith(prefix):
                indicators['has_suspicious_prefix'] = True
                indicators['reasons'].append(f'Suspicious prefix: {prefix}')
        
        # Check for burner patterns (recently activated numbers)
        # This would typically involve checking against carrier databases
        # For now, we'll use a simple heuristic
        if len(set(mobile_number)) <= 3:  # Too many repeated digits
            indicators['is_burner'] = True
            indicators['reasons'].append('Too many repeated digits')
        
        return indicators
    
    def _calculate_risk_score(self, analysis_result: Dict) -> int:
        """Calculate risk score for B-party (0-100, higher = more risky)"""
        score = 0
        
        # IP address risk factors
        if analysis_result.get('type') == 'ip_address':
            if analysis_result.get('validation', {}).get('is_private', False):
                score += 10
            if analysis_result.get('threat_indicators', {}).get('is_tor_exit', False):
                score += 30
            if analysis_result.get('threat_indicators', {}).get('is_vpn', False):
                score += 20
        
        # Mobile number risk factors
        elif analysis_result.get('type') == 'mobile_number':
            suspicious = analysis_result.get('suspicious_indicators', {})
            if suspicious.get('is_burner', False):
                score += 25
            if suspicious.get('is_anonymous', False):
                score += 35
            if suspicious.get('has_suspicious_prefix', False):
                score += 15
        
        # Unknown format risk
        elif analysis_result.get('type') == 'unknown':
            score += 40
        
        # Validation failures
        if not analysis_result.get('validation', {}).get('is_valid', True):
            score += 20
        
        return min(score, 100)
    
    def batch_analyze_bparties(self, bparty_list: List[str], service_types: List[str] = None) -> List[Dict]:
        """Analyze multiple B-parties in batch"""
        results = []
        
        if service_types is None:
            service_types = [None] * len(bparty_list)
        
        for i, bparty in enumerate(bparty_list):
            service_type = service_types[i] if i < len(service_types) else None
            result = self.analyze_bparty(bparty, service_type)
            results.append(result)
            
            # Rate limiting for external API calls
            if result.get('type') == 'ip_address':
                time.sleep(0.1)  # 100ms delay between IP lookups
        
        return results
    
    def generate_bparty_report(self, analysis_results: List[Dict]) -> Dict:
        """Generate comprehensive report from B-party analysis"""
        total_count = len(analysis_results)
        ip_count = sum(1 for r in analysis_results if r.get('type') == 'ip_address')
        mobile_count = sum(1 for r in analysis_results if r.get('type') == 'mobile_number')
        unknown_count = sum(1 for r in analysis_results if r.get('type') == 'unknown')
        
        high_risk = sum(1 for r in analysis_results if r.get('risk_score', 0) >= 70)
        medium_risk = sum(1 for r in analysis_results if 30 <= r.get('risk_score', 0) < 70)
        low_risk = sum(1 for r in analysis_results if r.get('risk_score', 0) < 30)
        
        return {
            'summary': {
                'total_bparties': total_count,
                'ip_addresses': ip_count,
                'mobile_numbers': mobile_count,
                'unknown_formats': unknown_count
            },
            'risk_distribution': {
                'high_risk': high_risk,
                'medium_risk': medium_risk,
                'low_risk': low_risk
            },
            'top_risky_bparties': sorted(
                [r for r in analysis_results if r.get('risk_score', 0) >= 50],
                key=lambda x: x.get('risk_score', 0),
                reverse=True
            )[:10],
            'geolocation_summary': self._generate_geolocation_summary(analysis_results),
            'carrier_summary': self._generate_carrier_summary(analysis_results),
            'generated_at': datetime.now().isoformat()
        }
    
    def _generate_geolocation_summary(self, analysis_results: List[Dict]) -> Dict:
        """Generate geolocation summary from analysis results"""
        countries = {}
        cities = {}
        
        for result in analysis_results:
            if result.get('type') == 'ip_address':
                geo = result.get('geolocation', {})
                country = geo.get('country', 'Unknown')
                city = geo.get('city', 'Unknown')
                
                countries[country] = countries.get(country, 0) + 1
                cities[city] = cities.get(city, 0) + 1
        
        return {
            'countries': dict(sorted(countries.items(), key=lambda x: x[1], reverse=True)[:10]),
            'cities': dict(sorted(cities.items(), key=lambda x: x[1], reverse=True)[:10])
        }
    
    def _generate_carrier_summary(self, analysis_results: List[Dict]) -> Dict:
        """Generate carrier summary from analysis results"""
        carriers = {}
        
        for result in analysis_results:
            if result.get('type') == 'mobile_number':
                carrier_info = result.get('carrier_info', {})
                if isinstance(carrier_info, dict):
                    carrier = carrier_info.get('carrier_name', 'Unknown')
                else:
                    carrier = str(carrier_info) if carrier_info else 'Unknown'
                carriers[carrier] = carriers.get(carrier, 0) + 1
        
        return dict(sorted(carriers.items(), key=lambda x: x[1], reverse=True)[:10])
