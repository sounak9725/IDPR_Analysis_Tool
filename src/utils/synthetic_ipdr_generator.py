import pandas as pd
import numpy as np
import random
import json
import csv
from datetime import datetime, timedelta
from faker import Faker
import ipaddress

fake = Faker()

class SyntheticIPDRGenerator:
    def __init__(self):
        self.phone_numbers = []
        self.ip_addresses = []
        self.imei_numbers = []
        self.cell_towers = []
        self.suspicious_entities = []
        
    def generate_entities(self, num_phones=200, num_ips=100):
        """Generate realistic phone numbers and IP addresses"""
        
        # Generate Indian mobile numbers (realistic format)
        indian_prefixes = ['91987', '91988', '91989', '91990', '91991', '91992', '91993', '91994', '91995', '91996', '91997', '91998', '91999']
        for _ in range(num_phones):
            prefix = random.choice(indian_prefixes)
            suffix = ''.join([str(random.randint(0, 9)) for _ in range(5)])
            self.phone_numbers.append(prefix + suffix)
        
        # Generate IP addresses (various ranges)
        ip_ranges = [
            '192.168.{}.{}',
            '10.0.{}.{}',
            '172.16.{}.{}',
            '203.{}.{}.{}',  # Public IPs
            '117.{}.{}.{}',  # Indian ISP range
        ]
        
        for _ in range(num_ips):
            ip_template = random.choice(ip_ranges)
            if ip_template.count('{}') == 2:
                ip = ip_template.format(
                    random.randint(1, 254),
                    random.randint(1, 254)
                )
            else:
                ip = ip_template.format(
                    random.randint(1, 254),
                    random.randint(1, 254),
                    random.randint(1, 254)
                )
            self.ip_addresses.append(ip)
        
        # Generate IMEI numbers
        for _ in range(num_phones):
            imei = ''.join([str(random.randint(0, 9)) for _ in range(15)])
            self.imei_numbers.append(imei)
        
        # Generate cell tower information
        for i in range(50):
            tower = {
                'tower_id': f'TOWER_{i+1:03d}',
                'lac': random.randint(1000, 9999),
                'location': fake.city() + ', ' + fake.state(),
                'coordinates': [fake.latitude(), fake.longitude()]
            }
            self.cell_towers.append(tower)
    
    def create_suspicious_patterns(self):
        """Define entities that will exhibit suspicious behavior"""
        
        # Criminal network (highly connected nodes)
        criminal_network = random.sample(self.phone_numbers, 10)
        
        # Burner phone patterns (short-lived, high activity)
        burner_phones = random.sample(self.phone_numbers, 5)
        
        # Drug dealer pattern (many short calls)
        drug_dealers = random.sample(self.phone_numbers, 3)
        
        # Bot network (IP addresses with automated patterns)
        bot_network = random.sample(self.ip_addresses, 8)
        
        self.suspicious_entities = {
            'criminal_network': criminal_network,
            'burner_phones': burner_phones,
            'drug_dealers': drug_dealers,
            'bot_network': bot_network
        }
        
        return self.suspicious_entities
    
    def generate_ipdr_records(self, num_records=10000, days_span=30):
        """Generate realistic IPDR records with suspicious patterns"""
        
        if not self.phone_numbers:
            self.generate_entities()
        
        self.create_suspicious_patterns()
        
        records = []
        base_date = datetime.now() - timedelta(days=days_span)
        
        for i in range(num_records):
            # Determine if this should be a suspicious record
            is_suspicious = random.random() < 0.15  # 15% suspicious records
            
            # Generate timestamp
            if is_suspicious:
                # Suspicious calls more likely at unusual hours
                hour = random.choice([1, 2, 3, 23, 0] * 3 + list(range(24)))
            else:
                # Normal distribution of calls throughout the day
                hour = np.random.choice(24, p=self._get_hourly_distribution())
            
            timestamp = base_date + timedelta(
                days=random.randint(0, days_span-1),
                hours=hour,
                minutes=random.randint(0, 59),
                seconds=random.randint(0, 59)
            )
            
            # Select A-party and B-party
            a_party, b_party, service_type = self._select_parties(is_suspicious)
            
            # Generate call/session details
            duration = self._generate_duration(is_suspicious, service_type)
            data_volume = self._generate_data_volume(service_type, duration)
            
            # Generate location info
            tower = random.choice(self.cell_towers)
            
            record = {
                'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'a_party': a_party,
                'b_party': b_party,
                'duration': duration,
                'service_type': service_type,
                'bytes_up': data_volume['up'],
                'bytes_down': data_volume['down'],
                'cell_tower_id': tower['tower_id'],
                'lac': tower['lac'],
                'location': tower['location'],
                'session_id': f'SID_{i+1:08d}',
                'imei': random.choice(self.imei_numbers) if service_type != 'DATA' else None,
                'protocol': self._get_protocol(service_type),
                'status': random.choice(['COMPLETED', 'FAILED', 'BUSY']) if service_type == 'VOICE' else 'COMPLETED'
            }
            
            records.append(record)
        
        return records
    
    def _get_hourly_distribution(self):
        """Realistic hourly distribution of communications"""
        # Peak hours: 9-11 AM, 2-4 PM, 7-9 PM
        distribution = np.array([
            0.01, 0.01, 0.01, 0.01, 0.01, 0.02,  # 0-5 AM
            0.03, 0.05, 0.08, 0.12, 0.10, 0.08,  # 6-11 AM
            0.06, 0.08, 0.10, 0.09, 0.07, 0.06,  # 12-5 PM
            0.05, 0.08, 0.11, 0.09, 0.06, 0.03   # 6-11 PM
        ])
        return distribution / distribution.sum()
    
    def _select_parties(self, is_suspicious):
        """Select A-party and B-party based on suspicious patterns"""
        
        all_entities = self.phone_numbers + self.ip_addresses
        
        if is_suspicious:
            # Higher chance of involving suspicious entities
            if random.random() < 0.6:
                # Criminal network communications
                if random.random() < 0.4:
                    a_party = random.choice(self.suspicious_entities['criminal_network'])
                    b_party = random.choice(self.suspicious_entities['criminal_network'])
                    service_type = random.choice(['VOICE', 'SMS'])
                
                # Drug dealer pattern
                elif random.random() < 0.3:
                    a_party = random.choice(self.suspicious_entities['drug_dealers'])
                    b_party = random.choice(all_entities)
                    service_type = 'VOICE'
                
                # Burner phone pattern
                elif random.random() < 0.2:
                    a_party = random.choice(self.suspicious_entities['burner_phones'])
                    b_party = random.choice(all_entities)
                    service_type = random.choice(['VOICE', 'SMS'])
                
                # Bot network
                else:
                    a_party = random.choice(self.suspicious_entities['bot_network'])
                    b_party = random.choice(self.ip_addresses)
                    service_type = 'DATA'
            else:
                a_party = random.choice(all_entities)
                b_party = random.choice(all_entities)
                service_type = random.choice(['VOICE', 'SMS', 'DATA'])
        else:
            # Normal communication
            a_party = random.choice(all_entities)
            b_party = random.choice(all_entities)
            service_type = random.choice(['VOICE', 'SMS', 'DATA'])
        
        # Ensure A and B are different
        while b_party == a_party:
            b_party = random.choice(all_entities)
        
        return a_party, b_party, service_type
    
    def _generate_duration(self, is_suspicious, service_type):
        """Generate realistic duration based on service type and suspicion level"""
        
        if service_type == 'SMS':
            return 0  # SMS has no duration
        elif service_type == 'DATA':
            if is_suspicious:
                # Suspicious data sessions might be very short (automated) or very long
                return random.choice([
                    random.randint(1, 10),      # Very short
                    random.randint(3600, 7200)  # Very long
                ])
            else:
                return random.randint(60, 1800)  # Normal browsing
        else:  # VOICE
            if is_suspicious:
                # Drug dealers: many very short calls
                if random.random() < 0.4:
                    return random.randint(3, 15)
                # Criminal network: normal or long calls
                else:
                    return random.randint(30, 1800)
            else:
                # Normal voice call distribution
                return int(np.random.lognormal(4, 1))  # Log-normal distribution
    
    def _generate_data_volume(self, service_type, duration):
        """Generate data volume based on service type and duration"""
        
        if service_type == 'VOICE':
            # Voice calls: ~64 kbps
            rate = 8000  # bytes per second
            up = duration * rate + random.randint(-1000, 1000)
            down = duration * rate + random.randint(-1000, 1000)
        elif service_type == 'SMS':
            up = random.randint(100, 500)
            down = random.randint(100, 500)
        else:  # DATA
            # Variable data rates
            if duration > 0:
                rate = random.randint(50000, 500000)  # 50KB to 500KB per second
                up = duration * rate // 10  # Upload typically lower
                down = duration * rate
            else:
                up = down = 0
        
        return {'up': max(0, up), 'down': max(0, down)}
    
    def _get_protocol(self, service_type):
        """Get protocol based on service type"""
        protocols = {
            'VOICE': random.choice(['SIP', 'H.323', 'RTP']),
            'SMS': 'SMS-MT/MO',
            'DATA': random.choice(['HTTP', 'HTTPS', 'TCP', 'UDP', 'FTP'])
        }
        return protocols.get(service_type, 'UNKNOWN')
    
    def export_to_csv(self, records, filename='synthetic_ipdr.csv'):
        """Export records to CSV format"""
        df = pd.DataFrame(records)
        df.to_csv(filename, index=False)
        print(f"Exported {len(records)} records to {filename}")
    
    def export_to_json(self, records, filename='synthetic_ipdr.json'):
        """Export records to JSON format"""
        with open(filename, 'w') as f:
            json.dump(records, f, indent=2, default=str)
        print(f"Exported {len(records)} records to {filename}")
    
    def export_to_text(self, records, filename='synthetic_ipdr.txt'):
        """Export records to pipe-delimited text format"""
        with open(filename, 'w') as f:
            for record in records:
                line = '|'.join([
                    str(record['timestamp']),
                    str(record['a_party']),
                    str(record['b_party']),
                    str(record['duration']),
                    str(record['service_type']),
                    str(record['bytes_up']),
                    str(record['bytes_down'])
                ])
                f.write(line + '\n')
        print(f"Exported {len(records)} records to {filename}")
    
    def generate_case_study_data(self):
        """Generate specific case study scenarios"""
        
        case_studies = {
            'drug_trafficking_ring': self._generate_drug_case(),
            'terrorism_network': self._generate_terrorism_case(),
            'cybercrime_botnet': self._generate_botnet_case(),
            'fraud_network': self._generate_fraud_case()
        }
        
        return case_studies
    
    def _generate_drug_case(self):
        """Generate a drug trafficking case scenario"""
        # Main dealer with many short calls to different numbers
        dealer = random.choice(self.suspicious_entities['drug_dealers'])
        customers = random.sample(self.phone_numbers, 20)
        
        records = []
        base_time = datetime.now() - timedelta(days=7)
        
        for day in range(7):
            # 10-15 calls per day
            for _ in range(random.randint(10, 15)):
                customer = random.choice(customers)
                timestamp = base_time + timedelta(
                    days=day,
                    hours=random.randint(18, 23),  # Evening calls
                    minutes=random.randint(0, 59)
                )
                
                # Very short call followed by meeting
                records.append({
                    'timestamp': timestamp,
                    'a_party': customer,
                    'b_party': dealer,
                    'duration': random.randint(5, 20),
                    'service_type': 'VOICE',
                    'pattern': 'drug_deal_coordination'
                })
        
        return records
    
    def _generate_terrorism_case(self):
        """Generate a terrorism network case scenario"""
        network = random.sample(self.suspicious_entities['criminal_network'], 6)
        leader = network[0]
        
        records = []
        base_time = datetime.now() - timedelta(days=14)
        
        # Planning phase: increased communications
        for day in range(10):
            for member in network[1:]:
                if random.random() < 0.7:  # 70% chance of daily contact
                    timestamp = base_time + timedelta(
                        days=day,
                        hours=random.choice([22, 23, 0, 1, 2]),  # Late night
                        minutes=random.randint(0, 59)
                    )
                    
                    records.append({
                        'timestamp': timestamp,
                        'a_party': leader,
                        'b_party': member,
                        'duration': random.randint(300, 1800),  # Longer calls
                        'service_type': 'VOICE',
                        'pattern': 'terrorism_coordination'
                    })
        
        return records
    
    def _generate_botnet_case(self):
        """Generate a botnet case scenario"""
        command_server = random.choice(self.suspicious_entities['bot_network'])
        bots = random.sample(self.ip_addresses, 15)
        
        records = []
        base_time = datetime.now() - timedelta(hours=24)
        
        # Regular check-ins every 30 minutes
        for hour in range(24):
            for minute in [0, 30]:
                timestamp = base_time + timedelta(hours=hour, minutes=minute)
                
                for bot in bots:
                    if random.random() < 0.8:  # 80% of bots check in
                        records.append({
                            'timestamp': timestamp,
                            'a_party': bot,
                            'b_party': command_server,
                            'duration': random.randint(1, 5),  # Very short
                            'service_type': 'DATA',
                            'bytes_up': random.randint(100, 500),
                            'bytes_down': random.randint(100, 500),
                            'pattern': 'botnet_checkin'
                        })
        
        return records

# Example usage
def create_comprehensive_dataset():
    """Create a comprehensive synthetic dataset for hackathon"""
    
    generator = SyntheticIPDRGenerator()
    
    # Generate main dataset
    print("Generating main IPDR dataset...")
    records = generator.generate_ipdr_records(num_records=15000, days_span=30)
    
    # Export in multiple formats
    generator.export_to_csv(records, 'hackathon_ipdr_main.csv')
    generator.export_to_json(records, 'hackathon_ipdr_main.json')
    generator.export_to_text(records, 'hackathon_ipdr_main.txt')
    
    # Generate case study data
    print("Generating case study scenarios...")
    case_studies = generator.generate_case_study_data()
    
    for case_name, case_records in case_studies.items():
        if case_records:
            df = pd.DataFrame(case_records)
            df.to_csv(f'case_study_{case_name}.csv', index=False)
    
    # Generate summary statistics
    df = pd.DataFrame(records)
    summary = {
        'total_records': len(records),
        'unique_a_parties': df['a_party'].nunique(),
        'unique_b_parties': df['b_party'].nunique(),
        'service_types': df['service_type'].value_counts().to_dict(),
        'suspicious_entities': generator.suspicious_entities,
        'date_range': {
            'start': df['timestamp'].min(),
            'end': df['timestamp'].max()
        }
    }
    
    with open('dataset_summary.json', 'w') as f:
        json.dump(summary, f, indent=2, default=str)
    
    print(f"\nDataset Generation Complete!")
    print(f"✓ Main dataset: {len(records)} records")
    print(f"✓ Unique entities: {df['a_party'].nunique() + df['b_party'].nunique()}")
    print(f"✓ Case studies: {len(case_studies)}")
    print(f"✓ Suspicious patterns included: Drug trafficking, terrorism, botnets, fraud")
    
    return records, case_studies

if __name__ == "__main__":
    # Install faker if not already installed
    try:
        from faker import Faker
    except ImportError:
        print("Please install faker: pip install faker")
        exit(1)
    
    # Generate comprehensive dataset
    create_comprehensive_dataset()