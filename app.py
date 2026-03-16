#!/usr/bin/env python3
"""
Phone Control API - Python wrapper for ADB shell scripts
Endpoints: Create Contact, Send SMS, Get Calls, Get SMS, Unified Monitor
Local-only API running on localhost:5000
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import json
import os
import re
import time
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

def run_script(script_name, args=None):
    """Run a shell script and return output"""
    try:
        if script_name not in SCRIPTS:
            return {'success': False, 'error': f'Unknown script: {script_name}'}
        
        script_path = SCRIPTS[script_name]
        if not os.path.exists(script_path):
            return {'success': False, 'error': f'Script not found: {script_path}'}
        
        cmd = [script_path]
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
        'version': '1.0.0',
        'status': 'running',
        'endpoints': [
            'POST /api/create_contact',
            'POST /api/send_sms',
            'GET /api/get_calls',
            'GET /api/get_sms',
            'GET /api/unified_monitor'
        ]
    })

@app.route('/api/create_contact', methods=['POST'])
def create_contact():
    """Create contact and prefill dialer - uses BASH script for reliability"""
    try:
        data = request.get_json()
        full_name = data.get('full_name')
        phone_number = data.get('phone_number')
        
        if not full_name or not phone_number:
            return jsonify({'success': False, 'error': 'Missing full_name or phone_number'}), 400
        
        # Call bash script which handles everything
        result = subprocess.run(['/tmp/create_contact_full.sh', full_name, phone_number],
            capture_output=True, text=True, timeout=30
        )
        
        if result.returncode != 0:
            return jsonify({
                'success': False,
                'error': 'Failed to create contact',
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
        phone_number = data.get('phone_number')
        message = data.get('message')
        
        if not phone_number or not message:
            return jsonify({'success': False, 'error': 'Missing parameters'}), 400
        
        result = run_script('send_sms', [phone_number, message])
        
        return jsonify({
            'success': result['success'],
            'message': f'SMS sent to {phone_number}' if result['success'] else 'Failed',
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
        since = request.args.get('since')  # Format: "2026-03-16 18:00:00"
        
        args = [since] if since else []
        result = run_script('get_calls', args)
        
        return jsonify({
            'success': result['success'],
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
        since = request.args.get('since')  # Format: "2026-03-16 18:00:00"
        
        args = [since] if since else []
        result = run_script('get_sms', args)
        
        return jsonify({
            'success': result['success'],
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
        result = run_script('unified_monitor')
        
        return jsonify({
            'success': result['success'],
            'monitoring': 'active',
            'output': result['output'],
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    # Run on localhost only - not accessible from outside
    app.run(host='127.0.0.1', port=5000, debug=False)
