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
from werkzeug.utils import secure_filename
from flask import Blueprint, Response

# logging part coding
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('web_dashboard.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

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
        
        # configuring the SocketIO with better production settings for the dashboard
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
        self.current_dataset_path = None
        self.setup_routes()
        self.setup_error_handlers()
        self.api_v1 = Blueprint('api_v1', __name__, url_prefix='/api/v1')
        self.setup_api_v1()
        # implementing the job store
        self.jobs = {}
        # resolving the base directories deterministically (project root = two levels up from this file)
        self.base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        self.config_dir = os.path.join(self.base_dir, 'config')
        self.exports_dir = os.path.join(self.base_dir, 'outputs', 'exports')
        os.makedirs(self.config_dir, exist_ok=True)
        # loading or generating the admin password (file or env).
        self.admin_password, self.admin_password_auto = self._load_or_generate_admin_password()
        try:
            self.jobs = self._load_jobs_from_file()
        except Exception:
            self.jobs = {}
        os.makedirs(self.exports_dir, exist_ok=True)
    
    def clean_data_for_json(self, df):
        """Clean DataFrame data for JSON serialization by replacing NaN values"""
        if df is None or df.empty:
            return []
        
        try:
            # replacing the NaN values with none in the json file
            df_clean = df.replace({np.nan: None})
            
            # converting to records and cleaning each record
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
            # fallback: returning an empty list if cleaning fails
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
                    self.current_dataset_path = data_file
                
                return jsonify({
                    'success': True,
                    'message': f'Loaded {len(self.analyzer.data)} records',
                    'records_count': len(self.analyzer.data),
                    'dataset_path': self.current_dataset_path
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/upload-data', methods=['POST'])
        def upload_data():
            """Upload a user dataset (CSV/JSON/TXT). Does not auto-activate."""
            try:
                if 'file' not in request.files:
                    return jsonify({'error': 'No file part in request'}), 400
                file = request.files['file']
                if file.filename == '':
                    return jsonify({'error': 'No selected file'}), 400

                filename = secure_filename(file.filename)
                raw_dir = os.path.join('data', 'raw')
                os.makedirs(raw_dir, exist_ok=True)
                save_path = os.path.join(raw_dir, f"uploaded_{int(time.time())}_{filename}")
                file.save(save_path)

                return jsonify({
                    'success': True,
                    'message': f'Uploaded {filename}. Activate it from the dataset selector to use.',
                    'path': save_path
                })
            except Exception as e:
                logger.exception('Upload failed')
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/generate-data', methods=['POST'])
        def generate_data():
            """Generate a synthetic dataset. Does not auto-activate."""
            try:
                payload = request.get_json(silent=True) or {}
                num_records = int(payload.get('num_records', 10000))
                days_span = int(payload.get('days_span', 30))

                # lazy import to avoid cost if unused
                from src.utils.synthetic_ipdr_generator import SyntheticIPDRGenerator

                generator = SyntheticIPDRGenerator()
                records = generator.generate_ipdr_records(num_records=num_records, days_span=days_span)

                raw_dir = os.path.join('data', 'raw')
                os.makedirs(raw_dir, exist_ok=True)
                filename = f"generated_{int(time.time())}.csv"
                save_path = os.path.join(raw_dir, filename)

                # saving the CSV file
                import pandas as pd
                pd.DataFrame(records).to_csv(save_path, index=False)

                return jsonify({
                    'success': True,
                    'message': f'Generated dataset saved as {filename}. Activate it from the selector.',
                    'path': save_path
                })
            except Exception as e:
                logger.exception('Generation failed')
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/datasets')
        def list_datasets():
            """List available datasets in data/raw with basic metadata."""
            try:
                raw_dir = os.path.join('data', 'raw')
                os.makedirs(raw_dir, exist_ok=True)
                files = []
                for name in os.listdir(raw_dir):
                    if name.lower().endswith(('.csv', '.json', '.txt')):
                        path = os.path.join(raw_dir, name)
                        stat = os.stat(path)
                        files.append({
                            'name': name,
                            'path': path,
                            'size': stat.st_size,
                            'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
                        })
                files.sort(key=lambda f: f['modified'], reverse=True)
                return jsonify({
                    'success': True,
                    'current': self.current_dataset_path,
                    'datasets': files
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/activate-dataset', methods=['POST'])
        def activate_dataset():
            """Activate a chosen dataset by path, loading it into memory and rebuilding the graph."""
            try:
                payload = request.get_json() or {}
                dataset_path = payload.get('path')
                if not dataset_path or not os.path.exists(dataset_path):
                    return jsonify({'error': 'Dataset path not found'}), 400

                # initializing the analyzers if needed
                if self.analyzer is None:
                    self.analyzer = IPDRAnalyzer()
                    self.enhanced_analyzer = EnhancedBPartyAnalyzer()
                    self.filtering_system = AdvancedFilteringSystem()
                    self.case_management = CaseManagementSystem()

                if not self.analyzer.parse_ipdr_file(dataset_path):
                    return jsonify({'error': 'Failed to parse selected dataset'}), 400
                self.analyzer.network_graph.clear()
                self.analyzer.extract_relationships()
                self.data_loaded = True
                self.current_dataset_path = dataset_path

                return jsonify({
                    'success': True,
                    'message': f'Activated dataset with {len(self.analyzer.data)} records',
                    'dataset_path': self.current_dataset_path
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
                
                # enhanced search results
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
                
                # getting the top communication partners with counts
                if self.analyzer.data is not None:
                    entity_data = self.analyzer.data[
                        (self.analyzer.data['a_party'] == query) | 
                        (self.analyzer.data['b_party'] == query)
                    ]
                    
                    # check if entity_data is not empty before processing
                    if not entity_data.empty:
                        # top partners
                        if entity_data['a_party'].iloc[0] == query:
                            partners = entity_data['b_party'].value_counts().head(5)
                        else:
                            partners = entity_data['a_party'].value_counts().head(5)
                        
                        enhanced_results['top_partners'] = [
                            {'entity': partner, 'count': count} 
                            for partner, count in partners.items()
                        ]
                        
                        # recent activity
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
                    else:
                        # handle case when no data is found for the entity
                        enhanced_results['top_partners'] = []
                        enhanced_results['recent_activity'] = []
                
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
                # building the full node list with degrees
                all_nodes = []
                for node in self.analyzer.network_graph.nodes():
                    degree = self.analyzer.network_graph.degree(node)
                    all_nodes.append({
                        'id': node,
                        'label': node,
                        'degree': degree,
                        'size': min(degree * 2, 20)
                    })

                node_limit = 100
                limited_nodes = all_nodes[:node_limit]
                node_ids = set(n['id'] for n in limited_nodes)

                filtered_edges = []
                for source, target in self.analyzer.network_graph.edges():
                    if source in node_ids and target in node_ids:
                        filtered_edges.append({'source': source, 'target': target})

                edge_limit = 200

                return jsonify({
                    'nodes': limited_nodes,
                    'edges': filtered_edges[:edge_limit]
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
                
                # formatting the patterns for the frontend
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

        @self.app.route('/contributors')
        def contributors_page():
            """Simple page listing developer contributors"""
            contributors = [
                {
                    'name': 'Divya Bhaskar',
                    'year': '2nd/3rd',
                    'department': 'VIT Bhopal/ Btech Computer Science (cyber security)',
                    'city_state': 'Bhopal/MP',
                    'gender': 'Male',
                    'email': 'divya.24bcy10061@vitbhopal.ac.in',
                    'mobile': '8628896159'
                },
                {
                    'name': 'Sounak Bera',
                    'year': '2nd/3rd',
                    'department': 'VIT Bhopal/ Btech Computer Science (cyber security)',
                    'city_state': 'Bhopal/MP',
                    'gender': 'Male',
                    'email': 'sounak.24bcy10012@vitbhopal.ac.in',
                    'mobile': '8240308506'
                },
                {
                    'name': 'Ashqua Islam',
                    'year': '2nd/3rd',
                    'department': 'VIT Bhopal/ Btech Computer Science (cyber security)',
                    'city_state': 'Bhopal/MP',
                    'gender': 'Female',
                    'email': 'ashqua.24bcy10345@vitbhopal.ac.in',
                    'mobile': '6360007954'
                },
                {
                    'name': 'Sakshya Patel',
                    'year': '2nd/3rd',
                    'department': 'VIT Bhopal/ Btech Computer Science (cyber security)',
                    'city_state': 'Bhopal/MP',
                    'gender': 'Male',
                    'email': 'sakshya.24bcy10027@vitbhopal.ac.in',
                    'mobile': '9696053006'
                },
                {
                    'name': 'Aditya Nayak',
                    'year': '2nd/3rd',
                    'department': 'VIT Bhopal/ Btech Computer Science (cyber security)',
                    'city_state': 'Bhopal/MP',
                    'gender': 'Male',
                    'email': 'aditya.24bcy10283@vitbhopal.ac.in',
                    'mobile': '9301359332'
                },
            ]
            return render_template('contributors.html', contributors=contributors)

        # simple admin UI for API keys local only, no auth gate here beyond UI presence maybe later I can enchance the stuffs
        @self.app.route('/admin/keys')
        def admin_keys_page():
            try:
                keys = list(self._load_api_keys_from_file())
            except Exception:
                keys = []
            html = """
<!DOCTYPE html><html><head><meta charset='utf-8'><title>API Keys Admin</title>
<link href='https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css' rel='stylesheet'>
<style>body{padding:20px;background:#1a1a1a;color:#fff} .card{background:#2d2d2d}</style>
</head><body>
<div class='container'>
  <h3 class='mb-3'>API Keys Administration</h3>
  <div class='card mb-3'><div class='card-body'>
    <div id='status' class='alert d-none mb-3'></div>
    <div class='row g-2 align-items-center'>
      <div class='col-md-5'>
        <div class='input-group'>
          <input id='newKey' class='form-control' placeholder='Enter new API key'>
          <button class='btn btn-success' onclick='createKey()'>Create</button>
        </div>
      </div>
      <div class='col-md-3'>
        <input id='adminPw' type='password' class='form-control' placeholder='Admin password'>
      </div>
      <div class='col-md-2'>
        <input id='apiKey' type='password' class='form-control' placeholder='API Key'>
      </div>
      <div class='col-md-2'>
        <div class='d-grid'>
          <div class='btn-group'>
            <button class='btn btn-primary' onclick='savePw()'>Save</button>
            <button class='btn btn-outline-light' onclick='clearPw()'>Clear</button>
          </div>
        </div>
      </div>
    </div>
    <small class='text-muted'>Password is kept in this browser only (localStorage).</small>
  </div></div>
  <div class='card'><div class='card-body'>
    <h6>Existing Keys</h6>
    <ul id='keys' class='list-group'>
    </ul>
  </div></div>
</div>
<script>
async function tryFetchAutoPassword(){
  try{
    // Try to get the API key from localStorage or use a default one
    const apiKey = localStorage.getItem('api_key') || 'UIDN*&*@(KKD';
    const r = await fetch('/api/v1/admin/password', {
      headers: {
        'X-API-Key': apiKey
      }
    });
    if(r.ok){
      const j = await r.json();
      if(j && j.success && j.data && j.data.password){
        localStorage.setItem('admin_pw', j.data.password);
        document.getElementById('adminPw').value = j.data.password;
      }
    }
  }catch(e){}
}
function getHeaders(){
  const pw = localStorage.getItem('admin_pw') || document.getElementById('adminPw').value;
  const apiKey = localStorage.getItem('api_key') || 'UIDN*&*@(KKD';
  const h = {
    'X-API-Key': apiKey
  };
  if(pw) h['X-Admin-Password'] = pw;
  return h;
}
function savePw(){
  const pw = document.getElementById('adminPw').value;
  const apiKey = document.getElementById('apiKey').value;
  if(pw) localStorage.setItem('admin_pw', pw);
  if(apiKey) localStorage.setItem('api_key', apiKey);
  loadKeys();
}
function clearPw(){
  localStorage.removeItem('admin_pw');
  localStorage.removeItem('api_key');
  document.getElementById('adminPw').value='';
  document.getElementById('apiKey').value='';
  setStatus('Credentials cleared from this browser', 'info');
}
function setStatus(message, type){
  const el=document.getElementById('status');
  el.className='alert alert-'+(type||'info');
  el.textContent=message;
  el.classList.remove('d-none');
}
async function loadKeys(){
  const r = await fetch('/api/v1/admin/keys', { headers: getHeaders() });
  let j = { success:false, data:[] };
  try{ j = await r.json(); }catch(e){}
  if(!r.ok || j.success===false){
    setStatus('Auth required or invalid password. Set the correct password and try again.', 'danger');
  } else {
    setStatus('Loaded keys successfully', 'success');
  }
  const ul = document.getElementById('keys');
  ul.innerHTML = '';
  (j.data||[]).forEach(k=>{
    const li = document.createElement('li');
    li.className='list-group-item d-flex justify-content-between align-items-center';
    li.textContent=k;
    const btn=document.createElement('button');
    btn.className='btn btn-sm btn-danger';
    btn.textContent='Delete';
    btn.onclick=async()=>{await fetch('/api/v1/admin/keys/'+encodeURIComponent(k),{method:'DELETE', headers: getHeaders()}); loadKeys();}
    li.appendChild(btn); ul.appendChild(li);
  });
}
async function createKey(){
  const v=document.getElementById('newKey').value.trim();
  if(!v) return; await fetch('/api/v1/admin/keys',{method:'POST',headers:Object.assign({'Content-Type':'application/json'}, getHeaders()),body:JSON.stringify({key:v})});
  document.getElementById('newKey').value=''; loadKeys();
}
// Initialize stored values
document.getElementById('apiKey').value = localStorage.getItem('api_key') || 'UIDN*&*@(KKD';
document.getElementById('adminPw').value = localStorage.getItem('admin_pw') || '';

loadKeys();
tryFetchAutoPassword();
</script>
</body></html>
"""
            return Response(html, mimetype='text/html')
        
        # Enhanced Features API Endpoints
        
        @self.app.route('/api/enhanced-analysis')
        def enhanced_analysis_api():
            """Enhanced B-Party Analysis API"""
            if not self.data_loaded:
                return jsonify({'error': 'Data not loaded'}), 400
            
            try:
                # getting sample B-parties from the data
                bparties = self.analyzer.data['b_party'].unique()[:20]  # First 20 unique B-parties
                
                # analyzing B-parties
                analysis_results = self.enhanced_analyzer.batch_analyze_bparties(bparties.tolist())
                
                # generating the report
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
                # applying default filter templates
                self.filtering_system.apply_template('law_enforcement_critical')
                self.filtering_system.apply_template('suspicious_activity')
                
                # get filtered results with the enpoints
                logger.info("Running filters on data...")
                filtered_data, filtered_out = self.filtering_system.apply_filters(self.analyzer.data)
                
                logger.info(f"Filtering complete: {len(filtered_data)} records kept, {len(filtered_out)} filtered out")
                
                # ensure we have valid DataFrames
                if not isinstance(filtered_data, pd.DataFrame):
                    logger.error(f"filtered_data is not a DataFrame: {type(filtered_data)}")
                    filtered_data = pd.DataFrame()
                
                if not isinstance(filtered_out, pd.DataFrame):
                    logger.error(f"filtered_out is not a DataFrame: {type(filtered_out)}")
                    filtered_out = pd.DataFrame()
                
                # cleaning data for JSON serialization
                logger.info("Cleaning data for JSON serialization...")
                cleaned_filtered_data = self.clean_data_for_json(filtered_data)
                
                # limiting to 100 records
                cleaned_filtered_data = cleaned_filtered_data[:100]
                
                logger.info(f"Cleaned data: {len(cleaned_filtered_data)} records ready for JSON")
                
                # getting the filter statistics
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
                # getting the existing cases
                cases = self.case_management.get_all_cases()
                
                # getting the system statistics
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
                
                # convert string to EvidenceType enum ok
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
                
                # importing the EvidenceType enum
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

    def setup_api_v1(self):
        """Public API v1 - read-only initial endpoints"""
        api = self.api_v1
        self._api_keys_env = set([k.strip() for k in os.environ.get('IPDR_API_KEYS', '').split(',') if k.strip()])
        self._api_keys_file = set(self._load_api_keys_from_file())
        self._api_keys = set.union(self._api_keys_env, self._api_keys_file)
        self._rate_limit_state = {}

        # CORS and API key auth for the API
        @api.before_request
        def api_auth_and_cors():
            # CORS preflight for the API    
            if request.method == 'OPTIONS':
                resp = self._cors_response(jsonify({'success': True}))
                return resp

            # Skip authentication for health check endpoints
            if request.endpoint in ['api_v1.api_health', 'api_v1.api_v1_health']:
                return None

            #  API key only if keys are configured
            # refreshing keys from file each request (lightweight)
            self._api_keys_file = set(self._load_api_keys_from_file())
            self._api_keys = set.union(self._api_keys_env, self._api_keys_file)

            if self._api_keys:
                key = request.headers.get('X-API-Key') or None
                if not key:
                    # supporting the Bearer token
                    auth = request.headers.get('Authorization', '')
                    if auth.lower().startswith('bearer '):
                        key = auth.split(' ', 1)[1].strip()

                if not key or key not in self._api_keys:
                    resp = jsonify({'success': False, 'error': {'code': 'unauthorized', 'message': 'Invalid or missing API key'}})
                    resp.status_code = 401
                    return self._cors_response(resp)

                # simple in-memory rate limiting: 60 req/min per key
                from time import time as now
                bucket = self._rate_limit_state.get(key)
                window = 60
                limit = int(os.environ.get('IPDR_RATE_LIMIT_PER_MIN', '60'))
                t = int(now())
                slot = t - (t % window)
                if not bucket or bucket.get('slot') != slot:
                    bucket = {'slot': slot, 'count': 0}
                bucket['count'] += 1
                self._rate_limit_state[key] = bucket
                remaining = max(0, limit - bucket['count'])
                if bucket['count'] > limit:
                    resp = jsonify({'success': False, 'error': {'code': 'rate_limited', 'message': 'Rate limit exceeded'}})
                    resp.status_code = 429
                    resp.headers['Retry-After'] = str(window)
                    return self._cors_response(resp)

        @api.after_request
        def api_cors_headers(response):
            return self._cors_response(response)

        
        # helper: add CORS headers for the API
        
        

        @api.route('/health')
        def api_health():
            return jsonify({'success': True, 'data': {
                'status': 'ok',
                'data_loaded': self.data_loaded,
                'dataset_path': self.current_dataset_path
            }})

        @api.route('/v1/health')
        def api_v1_health():
            """Health check endpoint for Railway deployment - no authentication required"""
            return jsonify({'success': True, 'data': {
                'status': 'ok',
                'data_loaded': self.data_loaded,
                'dataset_path': self.current_dataset_path,
                'timestamp': datetime.now().isoformat()
            }})

        @api.route('/datasets')
        def api_datasets():
            raw_dir = os.path.join('data', 'raw')
            os.makedirs(raw_dir, exist_ok=True)
            files = []
            for name in os.listdir(raw_dir):
                if name.lower().endswith(('.csv', '.json', '.txt')):
                    path = os.path.join(raw_dir, name)
                    stat = os.stat(path)
                    files.append({
                        'name': name,
                        'path': path,
                        'size': stat.st_size,
                        'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        'active': path == self.current_dataset_path
                    })
            files.sort(key=lambda f: f['modified'], reverse=True)
            return jsonify({'success': True, 'data': files})

        @api.route('/records')
        def api_records():
            if not self.data_loaded or self.analyzer is None or self.analyzer.data is None:
                return jsonify({'success': True, 'data': [], 'total': 0})

            df = self.analyzer.data

            # Filters
            a_party = request.args.get('a_party')
            b_party = request.args.get('b_party')
            service_type = request.args.get('service_type')
            a_parties = request.args.get('a_parties')  # comma-separated
            b_parties = request.args.get('b_parties')
            contains = request.args.get('contains')  # regex on a_party or b_party
            ts_from = request.args.get('from')
            ts_to = request.args.get('to')
            min_dur = request.args.get('min_duration', type=int)
            max_dur = request.args.get('max_duration', type=int)

            if a_party:
                df = df[df['a_party'] == a_party]
            if b_party:
                df = df[df['b_party'] == b_party]
            if service_type:
                if 'service_type' in df.columns:
                    df = df[df['service_type'] == service_type]
            if a_parties:
                vals = [v.strip() for v in a_parties.split(',') if v.strip()]
                if vals:
                    df = df[df['a_party'].isin(vals)]
            if b_parties:
                vals = [v.strip() for v in b_parties.split(',') if v.strip()]
                if vals:
                    df = df[df['b_party'].isin(vals)]
            if contains:
                try:
                    df = df[df['a_party'].astype(str).str.contains(contains, regex=True, na=False) |
                            df['b_party'].astype(str).str.contains(contains, regex=True, na=False)]
                except Exception:
                    pass
            if ts_from and 'timestamp' in df.columns:
                try:
                    df = df[df['timestamp'] >= pd.to_datetime(ts_from)]
                except Exception:
                    pass
            if ts_to and 'timestamp' in df.columns:
                try:
                    df = df[df['timestamp'] <= pd.to_datetime(ts_to)]
                except Exception:
                    pass
            if min_dur is not None and 'duration' in df.columns:
                df = df[df['duration'] >= min_dur]
            if max_dur is not None and 'duration' in df.columns:
                df = df[df['duration'] <= max_dur]

            sort = request.args.get('sort')  # e.g., timestamp:desc
            if sort:
                try:
                    col, direction = (sort.split(':') + ['asc'])[:2]
                    if col in df.columns:
                        df = df.sort_values(col, ascending=(direction != 'desc'))
                except Exception:
                    pass

            page = max(1, request.args.get('page', default=1, type=int))
            limit = min(500, request.args.get('limit', default=50, type=int))
            total = int(len(df))
            start = (page - 1) * limit
            end = start + limit
            page_df = df.iloc[start:end].copy()

            records = self.clean_data_for_json(page_df)
            resp = jsonify({'success': True, 'data': records, 'page': page, 'limit': limit, 'total': total})
            resp.headers['X-Total-Count'] = str(total)
            return resp

        @api.route('/records/export')
        def api_records_export():
            if not self.data_loaded or self.analyzer is None or self.analyzer.data is None:
                return jsonify({'success': False, 'error': {'code': 'no_data', 'message': 'No active dataset'}}), 400

            # Reuse filtering logic by calling the same code path
            df = self.analyzer.data

            def apply_filters(df):
                a_party = request.args.get('a_party')
                b_party = request.args.get('b_party')
                service_type = request.args.get('service_type')
                ts_from = request.args.get('from')
                ts_to = request.args.get('to')
                min_dur = request.args.get('min_duration', type=int)
                max_dur = request.args.get('max_duration', type=int)
                if a_party:
                    df = df[df['a_party'] == a_party]
                if b_party:
                    df = df[df['b_party'] == b_party]
                if service_type and 'service_type' in df.columns:
                    df = df[df['service_type'] == service_type]
                if ts_from and 'timestamp' in df.columns:
                    try: df = df[df['timestamp'] >= pd.to_datetime(ts_from)]
                    except Exception: pass
                if ts_to and 'timestamp' in df.columns:
                    try: df = df[df['timestamp'] <= pd.to_datetime(ts_to)]
                    except Exception: pass
                if min_dur is not None and 'duration' in df.columns:
                    df = df[df['duration'] >= min_dur]
                if max_dur is not None and 'duration' in df.columns:
                    df = df[df['duration'] <= max_dur]
                return df

            df = apply_filters(df)

            def generate_csv():
                # Header
                cols = list(df.columns)
                yield ','.join(str(c) for c in cols) + '\n'
                # Stream rows
                for _, row in df.iterrows():
                    values = []
                    for c in cols:
                        v = row.get(c)
                        if isinstance(v, (datetime, pd.Timestamp)):
                            v = str(v)
                        values.append(str(v).replace('\n', ' ').replace('\r', ' '))
                    yield ','.join(values) + '\n'

            headers = {
                'Content-Disposition': 'attachment; filename="ipdr_export.csv"',
                'Content-Type': 'text/csv'
            }
            return Response(generate_csv(), headers=headers)

        @api.route('/jobs/records/export', methods=['POST'])
        def api_job_records_export():
            if not self.data_loaded or self.analyzer is None or self.analyzer.data is None:
                return jsonify({'success': False, 'error': {'code': 'no_data', 'message': 'No active dataset'}}), 400
            import uuid
            job_id = str(uuid.uuid4())
            filters = request.get_json(silent=True) or {}
            self.jobs[job_id] = {'id': job_id, 'type': 'export', 'status': 'queued', 'created': datetime.now().isoformat(), 'progress': 0}

            def run_job():
                try:
                    self.jobs[job_id]['status'] = 'running'
                    # Apply same filters
                    df = self.analyzer.data
                    a_party = filters.get('a_party')
                    b_party = filters.get('b_party')
                    service_type = filters.get('service_type')
                    ts_from = filters.get('from')
                    ts_to = filters.get('to')
                    min_dur = filters.get('min_duration')
                    max_dur = filters.get('max_duration')
                    if a_party: df = df[df['a_party'] == a_party]
                    if b_party: df = df[df['b_party'] == b_party]
                    if service_type and 'service_type' in df.columns: df = df[df['service_type'] == service_type]
                    if ts_from and 'timestamp' in df.columns:
                        try: df = df[df['timestamp'] >= pd.to_datetime(ts_from)]
                        except Exception: pass
                    if ts_to and 'timestamp' in df.columns:
                        try: df = df[df['timestamp'] <= pd.to_datetime(ts_to)]
                        except Exception: pass
                    if min_dur is not None and 'duration' in df.columns: df = df[df['duration'] >= int(min_dur)]
                    if max_dur is not None and 'duration' in df.columns: df = df[df['duration'] <= int(max_dur)]

                    out_dir = os.path.join('outputs', 'exports')
                    os.makedirs(out_dir, exist_ok=True)
                    out_path = os.path.join(out_dir, f'export_{job_id}.csv')
                    total = len(df)
                    chunk = max(1, total // 10)
                    # Stream write with progress
                    df.to_csv(out_path, index=False)
                    self.jobs[job_id]['progress'] = 100
                    self.jobs[job_id]['status'] = 'completed'
                    self.jobs[job_id]['result_path'] = out_path
                    self._persist_jobs()
                except Exception as e:
                    self.jobs[job_id]['status'] = 'failed'
                    self.jobs[job_id]['error'] = str(e)
                    self._persist_jobs()

            threading.Thread(target=run_job, daemon=True).start()
            return jsonify({'success': True, 'data': {'job_id': job_id}}), 202

        @api.route('/jobs/<job_id>')
        def api_job_status(job_id):
            job = self.jobs.get(job_id)
            if not job:
                return jsonify({'success': False, 'error': {'code': 'not_found', 'message': 'Job not found'}}), 404
            return jsonify({'success': True, 'data': job})

        @api.route('/jobs/<job_id>/download')
        def api_job_download(job_id):
            job = self.jobs.get(job_id)
            if not job or job.get('status') != 'completed' or not job.get('result_path'):
                return jsonify({'success': False, 'error': {'code': 'not_ready', 'message': 'Job not completed'}}), 400
            path = job['result_path']
            if not os.path.exists(path):
                return jsonify({'success': False, 'error': {'code': 'not_found', 'message': 'File missing'}}), 404
            def stream():
                with open(path, 'rb') as f:
                    while True:
                        chunk = f.read(8192)
                        if not chunk: break
                        yield chunk
            headers = {'Content-Disposition': f'attachment; filename="{os.path.basename(path)}"'}
            return Response(stream(), headers=headers, mimetype='text/csv')

        @api.route('/network/summary')
        def api_network_summary():
            if not self.data_loaded:
                return jsonify({'success': True, 'data': {'nodes': 0, 'edges': 0}})
            return jsonify({'success': True, 'data': {
                'nodes': self.analyzer.network_graph.number_of_nodes(),
                'edges': self.analyzer.network_graph.number_of_edges()
            }})

        @api.route('/network/graph')
        def api_network_graph():
            if not self.data_loaded:
                return jsonify({'success': True, 'data': {'nodes': [], 'edges': []}})

            # Reuse logic but without truncation control via query
            node_limit = request.args.get('nodes', default=100, type=int)
            edge_limit = request.args.get('edges', default=200, type=int)

            all_nodes = []
            for node in self.analyzer.network_graph.nodes():
                degree = self.analyzer.network_graph.degree(node)
                all_nodes.append({'id': node, 'label': node, 'degree': degree, 'size': min(degree * 2, 20)})

            limited_nodes = all_nodes[:node_limit]
            node_ids = set(n['id'] for n in limited_nodes)
            filtered_edges = []
            for s, t in self.analyzer.network_graph.edges():
                if s in node_ids and t in node_ids:
                    filtered_edges.append({'source': s, 'target': t})

            return jsonify({'success': True, 'data': {
                'nodes': limited_nodes,
                'edges': filtered_edges[:edge_limit]
            }})

        @api.route('/network/ego')
        def api_network_ego():
            if not self.data_loaded:
                return jsonify({'success': False, 'error': {'code': 'no_data', 'message': 'No active dataset'}}), 400
            entity = request.args.get('entity')
            hops = request.args.get('hops', default=1, type=int)
            if not entity:
                return jsonify({'success': False, 'error': {'code': 'bad_request', 'message': 'entity required'}}), 400
            G = self.analyzer.network_graph
            if entity not in G:
                return jsonify({'success': True, 'data': {'nodes': [], 'edges': []}})
            # Collect nodes within N hops
            nodes = {entity}
            frontier = {entity}
            for _ in range(max(1, hops)):
                next_frontier = set()
                for n in frontier:
                    next_frontier.update(G.neighbors(n))
                nodes.update(next_frontier)
                frontier = next_frontier
            sub = G.subgraph(list(nodes))
            nodes_out = []
            for n in sub.nodes():
                d = sub.degree(n)
                nodes_out.append({'id': n, 'label': n, 'degree': d, 'size': min(d * 2, 20)})
            edges_out = [{'source': s, 'target': t} for s, t in sub.edges()]
            return jsonify({'success': True, 'data': {'nodes': nodes_out, 'edges': edges_out}})

        @api.route('/patterns')
        def api_patterns():
            if not self.data_loaded:
                return jsonify({'success': True, 'data': {}})
            patterns = self.analyzer.analyze_communication_patterns() or {}
            formatted = {
                'time_patterns': {
                    'peak_hours': patterns.get('busiest_hours', {}).get('peak_hours', []),
                    'quiet_hours': patterns.get('busiest_hours', {}).get('quiet_hours', [])
                },
                'top_communicators': {
                    'initiators': list(patterns.get('top_communicators', {}).get('top_initiators', {}).items())[:10],
                    'recipients': list(patterns.get('top_communicators', {}).get('top_recipients', {}).items())[:10]
                }
            }
            return jsonify({'success': True, 'data': formatted})

        @api.route('/docs/openapi.json')
        def api_docs_json():
            doc = {
                'openapi': '3.0.0',
                'info': {'title': 'IPDR API', 'version': '1.0.0', 'description': 'Programmatic access to IPDR analysis'},
                'servers': [{'url': '/'}],
                'paths': {
                    '/api/v1/health': {'get': {'summary': 'Health'}},
                    '/api/v1/datasets': {'get': {'summary': 'List datasets'}},
                    '/api/v1/records': {
                        'get': {
                            'summary': 'List records with filters',
                            'parameters': [
                                {'name':'limit','in':'query','schema':{'type':'integer','default':50}},
                                {'name':'page','in':'query','schema':{'type':'integer','default':1}},
                                {'name':'sort','in':'query','schema':{'type':'string'},'example':'timestamp:desc'},
                                {'name':'a_party','in':'query','schema':{'type':'string'}},
                                {'name':'b_party','in':'query','schema':{'type':'string'}},
                                {'name':'a_parties','in':'query','schema':{'type':'string'},'example':'9199...,192.168.1.2'},
                                {'name':'b_parties','in':'query','schema':{'type':'string'}},
                                {'name':'service_type','in':'query','schema':{'type':'string','enum':['VOICE','SMS','DATA']}},
                                {'name':'from','in':'query','schema':{'type':'string','format':'date-time'}},
                                {'name':'to','in':'query','schema':{'type':'string','format':'date-time'}},
                                {'name':'min_duration','in':'query','schema':{'type':'integer'}},
                                {'name':'max_duration','in':'query','schema':{'type':'integer'}},
                                {'name':'contains','in':'query','schema':{'type':'string'},'description':'Regex match on a_party or b_party'}
                            ]
                        }
                    },
                    '/api/v1/records/export': {'get': {'summary': 'Export records CSV', 'parameters':[{'name':'service_type','in':'query','schema':{'type':'string'}}]}},
                    '/api/v1/network/summary': {'get': {'summary': 'Network summary'}},
                    '/api/v1/network/graph': {'get': {'summary': 'Limited graph'}},
                    '/api/v1/network/ego': {'get': {'summary': 'Ego network'}},
                    '/api/v1/patterns': {'get': {'summary': 'Patterns'}}
                }
            }
            return jsonify(doc)

        @api.route('/docs')
        def api_docs_ui():
            # Minimal Swagger UI served via CDN
            html = (
                "<!DOCTYPE html><html><head><meta charset='utf-8'/>"
                "<title>IPDR API Docs</title>"
                "<link rel='stylesheet' href='https://unpkg.com/swagger-ui-dist@5/swagger-ui.css'>"
                "</head><body>"
                "<div id='swagger-ui'></div>"
                "<script src='https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js'></script>"
                "<script>window.ui = SwaggerUIBundle({url: '/api/v1/docs/openapi.json', dom_id: '#swagger-ui'});</script>"
                "</body></html>"
            )
            return Response(html, mimetype='text/html')

        @api.route('/contributors')
        def api_contributors():
            contributors = [
                {
                    'name': 'Divya Bhaskar',
                    'year': '2nd/3rd',
                    'department': 'VIT Bhopal/ Btech Computer Science (cyber security)',
                    'city_state': 'Bhopal/MP',
                    'gender': 'Male',
                    'email': 'divya.24bcy10061@vitbhopal.ac.in',
                    'mobile': '8628896159'
                },
                {
                    'name': 'Sounak Bera',
                    'year': '2nd/3rd',
                    'department': 'VIT Bhopal/ Btech Computer Science (cyber security)',
                    'city_state': 'Bhopal/MP',
                    'gender': 'Male',
                    'email': 'sounak.24bcy10012@vitbhopal.ac.in',
                    'mobile': '8240308506'
                },
                {
                    'name': 'Ashqua Islam',
                    'year': '2nd/3rd',
                    'department': 'VIT Bhopal/ Btech Computer Science (cyber security)',
                    'city_state': 'Bhopal/MP',
                    'gender': 'Female',
                    'email': 'ashqua.24bcy10345@vitbhopal.ac.in',
                    'mobile': '6360007954'
                },
                {
                    'name': 'Sakshya Patel',
                    'year': '2nd/3rd',
                    'department': 'VIT Bhopal/ Btech Computer Science (cyber security)',
                    'city_state': 'Bhopal/MP',
                    'gender': 'Male',
                    'email': 'sakshya.24bcy10027@vitbhopal.ac.in',
                    'mobile': '9696053006'
                },
                {
                    'name': 'Aditya Nayak',
                    'year': '2nd/3rd',
                    'department': 'VIT Bhopal/ Btech Computer Science (cyber security)',
                    'city_state': 'Bhopal/MP',
                    'gender': 'Male',
                    'email': 'aditya.24bcy10283@vitbhopal.ac.in',
                    'mobile': '9301359332'
                },
            ]
            return jsonify({'success': True, 'data': contributors})

        # Admin endpoints for API keys (protected)
        @api.route('/admin/password')
        def api_admin_password():
            # Only expose auto-generated password and only to localhost
            client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
            if not (self.admin_password_auto and client_ip in {'127.0.0.1', '::1'}):
                return jsonify({'success': False, 'error': {'code': 'forbidden', 'message': 'Not available'}}), 403
            return jsonify({'success': True, 'data': {'password': self.admin_password, 'auto_generated': True}})
        @api.route('/admin/keys')
        def api_keys_list():
            if not self._admin_authorized():
                return jsonify({'success': False, 'error': {'code': 'forbidden', 'message': 'Admin access denied'}}), 403
            keys = list(self._load_api_keys_from_file())
            return jsonify({'success': True, 'data': keys})

        @api.route('/admin/keys', methods=['POST'])
        def api_keys_add():
            if not self._admin_authorized():
                return jsonify({'success': False, 'error': {'code': 'forbidden', 'message': 'Admin access denied'}}), 403
            body = request.get_json(silent=True) or {}
            key = (body.get('key') or '').strip()
            if not key:
                return jsonify({'success': False, 'error': {'code': 'bad_request', 'message': 'key required'}}), 400
            path = os.path.join(self.config_dir, 'api_keys.json')
            keys = set(self._load_api_keys_from_file())
            keys.add(key)
            with open(path, 'w') as f:
                json.dump({'keys': sorted(list(keys))}, f, indent=2)
            return jsonify({'success': True})

        @api.route('/admin/keys/<key>', methods=['DELETE'])
        def api_keys_delete(key):
            if not self._admin_authorized():
                return jsonify({'success': False, 'error': {'code': 'forbidden', 'message': 'Admin access denied'}}), 403
            path = os.path.join(self.config_dir, 'api_keys.json')
            keys = set(self._load_api_keys_from_file())
            if key in keys:
                keys.remove(key)
                with open(path, 'w') as f:
                    json.dump({'keys': sorted(list(keys))}, f, indent=2)
            return jsonify({'success': True})

        # Register blueprint on the app
        self.app.register_blueprint(api)

    def _cors_response(self, response):
        try:
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Headers'] = 'Authorization, X-API-Key, Content-Type'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        except Exception:
            pass
        return response

    def _load_api_keys_from_file(self):
        try:
            path = os.path.join(self.config_dir, 'api_keys.json')
            if not os.path.exists(path):
                return []
            with open(path, 'r') as f:
                data = json.load(f)
                return data.get('keys', [])
        except Exception:
            return []

    def _load_or_generate_admin_password(self):
        # If ADMIN_PASSWORD set via env, use it and mark non-auto
        env_pw = os.environ.get('ADMIN_PASSWORD')
        path = os.path.join(self.config_dir, 'admin_password.json')
        if env_pw:
            return env_pw, False
        # Try file
        try:
            if os.path.exists(path):
                with open(path, 'r') as f:
                    data = json.load(f)
                    pw = data.get('password')
                    if pw:
                        return pw, data.get('auto_generated', True)
        except Exception:
            pass
        import secrets, string
        alphabet = string.ascii_letters + string.digits
        pw = ''.join(secrets.choice(alphabet) for _ in range(24))
        try:
            with open(path, 'w') as f:
                json.dump({'password': pw, 'auto_generated': True}, f, indent=2)
        except Exception:
            pass
        return pw, True

    def _persist_jobs(self):
        try:
            path = os.path.join(self.config_dir, 'jobs.json')
            with open(path, 'w') as f:
                json.dump(self.jobs, f, indent=2)
            self._cleanup_old_exports()
        except Exception:
            pass

    def _load_jobs_from_file(self):
        path = os.path.join(self.config_dir, 'jobs.json')
        if not os.path.exists(path):
            return {}
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except Exception:
            return {}

    def _cleanup_old_exports(self):
        try:
            keep_days = int(os.environ.get('IPDR_EXPORT_KEEP_DAYS', '3'))
            cutoff = datetime.now() - timedelta(days=keep_days)
            to_delete = []
            for job_id, job in list(self.jobs.items()):
                ts = job.get('created')
                try:
                    created_dt = datetime.fromisoformat(ts) if ts else datetime.now()
                except Exception:
                    created_dt = datetime.now()
                if created_dt < cutoff:
                    # Delete file if present
                    path = job.get('result_path')
                    if path and os.path.exists(path):
                        try: os.remove(path)
                        except Exception: pass
                    to_delete.append(job_id)
            for jid in to_delete:
                self.jobs.pop(jid, None)
            # Persist after cleanup
            path = os.path.join(self.config_dir, 'jobs.json')
            with open(path, 'w') as f:
                json.dump(self.jobs, f, indent=2)
        except Exception:
            pass

    def _admin_authorized(self):
        # Check ADMIN_PASSWORD or IP allowlist
        admin_pw = self.admin_password
        ip_allow = os.environ.get('ADMIN_IP_ALLOW', '')
        allowed_ips = {ip.strip() for ip in ip_allow.split(',') if ip.strip()}
        client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        if allowed_ips and client_ip not in allowed_ips:
            return False
        if admin_pw:
            supplied = request.headers.get('X-Admin-Password') or request.args.get('admin_password')
            if supplied != admin_pw:
                return False
        return True
def create_app():
    """Create and configure the Flask app"""
    dashboard = IPDRDashboard()
    return dashboard.app, dashboard.socketio

if __name__ == '__main__':
    app, socketio = create_app()
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
