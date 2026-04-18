from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import asyncio

app = Flask(__name__)
socketio = SocketIO(app)

# استيراد وحدات النظام
from vulnerability_hunter.pattern_matching.web_vuln_scanner import WebVulnerabilityScanner
from exploit_developer.exploit_builder.from_vulnerability import ExploitBuilder

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/api/scan', methods=['POST'])
def api_scan():
    data = request.json
    url = data.get('url')
    
    async def scan():
        scanner = WebVulnerabilityScanner()
        return await scanner.scan_url(url, {})
    
    vulns = asyncio.run(scan())
    return jsonify([v.to_dict() for v in vulns])

@app.route('/api/exploit', methods=['POST'])
def api_exploit():
    data = request.json
    vuln_info = data.get('vulnerability')
    
    builder = ExploitBuilder(simulation_mode=True)
    exploit = builder.build_from_vulnerability(vuln_info)
    
    return jsonify(exploit.to_dict())

@socketio.on('beacon')
def handle_beacon(data):
    """استقبال beacon من implants"""
    emit('response', {'status': 'received'})

if __name__ == '__main__':
    socketio.run(app, host='127.0.0.1', port=5000, debug=True)