#!/usr/bin/env python3
"""
Phone Control API - Python wrapper for ADB shell scripts
Endpoints: Create Contact, Send SMS, Get Calls, Get SMS, Unified Monitor
Local-only API running on localhost:5000
Multi-phone support: pass device_ip on every request to target a specific phone.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import os
import re
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Script paths
SCRIPTS = {
    'add_contact': '/tmp/add_contact.sh',
    'send_sms': '/tmp/send_sms.sh',
    'get_calls': '/tmp/get_calls.sh',
    'get_sms': '/tmp/get_sms.sh',
    'unified_monitor': '/root/.openclaw/workspace/unified_monitor.sh'
}

def run_script(script_name, device_ip, args=None):
    """Run a shell script with device_ip as the first argument and return output"""
    try:
        if script_name not in SCRIPTS:
            return {'success': False, 'error': f'Unknown script: {script_name}'}

        script_path = SCRIPTS[script_name]
        if not os.path.exists(script_path):
            return {'success': False, 'error': f'Script not found: {script_path}'}

        cmd = [script_path, device_ip]
        if args:
            cmd.extend(args)

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

        return {
            'success': result.returncode == 0,
            'output': result.stdout,
            'error': result.stderr if result.returncode != 0 else None
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

@app.route('/', methods=['GET'])
def health():
    """Health check"""
    return jsonify({
        'service': 'Phone Control API',
        'version': '2.0.0',
        'status': 'running',
        'note': 'device_ip is required on every request to identify the target phone',
        'endpoints': [
            'POST /api/create_contact  (body: device_ip, full_name, phone_number)',
            'POST /api/send_sms        (body: device_ip, phone_number, message)',
            'GET  /api/get_calls       (query: device_ip, [since])',
            'GET  /api/get_sms         (query: device_ip, [since])',
            'GET  /api/unified_monitor (query: device_ip)'
        ]
    })

@app.route('/api/create_contact', methods=['POST'])
def create_contact():
    """Create contact and prefill dialer - uses BASH script for reliability"""
    try:
        data = request.get_json()
        device_ip = data.get('device_ip')
        full_name = data.get('full_name')
        phone_number = data.get('phone_number')

        if not device_ip:
            return jsonify({'success': False, 'error': 'Missing device_ip'}), 400
        if not full_name or not phone_number:
            return jsonify({'success': False, 'error': 'Missing full_name or phone_number'}), 400

        # Call bash script which handles everything; device_ip is passed as $1
        result = subprocess.run(
            ['/tmp/create_contact_full.sh', device_ip, full_name, phone_number],
            capture_output=True, text=True, timeout=30
        )

        if result.returncode != 0:
            return jsonify({
                'success': False,
                'error': 'Failed to create contact',
                'device_ip': device_ip,
                'output': result.stdout,
                'error_output': result.stderr
            }), 500

        # Extract contact ID from output
        contact_id = 1
        match = re.search(r'New ID will be: (\d+)', result.stdout)
        if match:
            contact_id = int(match.group(1))

        return jsonify({
            'success': True,
            'message': f'Contact created and dialer opened: {full_name}',
            'device_ip': device_ip,
            'contact_id': contact_id,
            'full_name': full_name,
            'phone_number': phone_number,
            'dialer_opened': True,
            'script_output': result.stdout
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/send_sms', methods=['POST'])
def send_sms():
    """Send SMS message"""
    try:
        data = request.get_json()
        device_ip = data.get('device_ip')
        phone_number = data.get('phone_number')
        message = data.get('message')

        if not device_ip:
            return jsonify({'success': False, 'error': 'Missing device_ip'}), 400
        if not phone_number or not message:
            return jsonify({'success': False, 'error': 'Missing parameters'}), 400

        result = run_script('send_sms', device_ip, [phone_number, message])

        return jsonify({
            'success': result['success'],
            'message': f'SMS sent to {phone_number}' if result['success'] else 'Failed',
            'device_ip': device_ip,
            'phone_number': phone_number,
            'sms_text': message,
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/get_calls', methods=['GET'])
def get_calls():
    """Get call history (optionally filtered by datetime)"""
    try:
        device_ip = request.args.get('device_ip')
        since = request.args.get('since')  # Format: "2026-03-16 18:00:00"

        if not device_ip:
            return jsonify({'success': False, 'error': 'Missing device_ip'}), 400

        args = [since] if since else []
        result = run_script('get_calls', device_ip, args)

        return jsonify({
            'success': result['success'],
            'device_ip': device_ip,
            'mode': 'filtered' if since else 'all',
            'filter': since,
            'output': result['output'],
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/get_sms', methods=['GET'])
def get_sms():
    """Get SMS messages (optionally filtered by datetime)"""
    try:
        device_ip = request.args.get('device_ip')
        since = request.args.get('since')  # Format: "2026-03-16 18:00:00"

        if not device_ip:
            return jsonify({'success': False, 'error': 'Missing device_ip'}), 400

        args = [since] if since else []
        result = run_script('get_sms', device_ip, args)

        return jsonify({
            'success': result['success'],
            'device_ip': device_ip,
            'mode': 'filtered' if since else 'all',
            'filter': since,
            'output': result['output'],
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/unified_monitor', methods=['GET'])
def unified_monitor():
    """Get real-time unified monitoring (dialer, SMS, calls, contacts)"""
    try:
        device_ip = request.args.get('device_ip')

        if not device_ip:
            return jsonify({'success': False, 'error': 'Missing device_ip'}), 400

        result = run_script('unified_monitor', device_ip)

        return jsonify({
            'success': result['success'],
            'device_ip': device_ip,
            'monitoring': 'active',
            'output': result['output'],
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    # Run on localhost only - not accessible from outside
    app.run(host='127.0.0.1', port=5000, debug=False)
