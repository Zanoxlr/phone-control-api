"""
Phone Control API Configuration
"""

import os
from datetime import datetime

# Server Configuration
HOST = '127.0.0.1'  # Local only
PORT = 5000
DEBUG = False

# Device Information
DEVICE_IP = '100.103.46.48'  # Tailscale IP
DEVICE_ADB_PORT = 5555

# Script Paths
SCRIPTS_DIR = '/tmp'
WORKSPACE_DIR = '/root/.openclaw/workspace'

# API Configuration
API_VERSION = '1.0.0'
API_TITLE = 'Phone Control API'

# Logging
LOG_DIR = './logs'
LOG_LEVEL = 'INFO'

# Device Startup Info
STARTUP_TIME = datetime.utcnow().isoformat()
DEVICE_CONFIG = {
    'device_ip': DEVICE_IP,
    'adb_port': DEVICE_ADB_PORT,
    'api_version': API_VERSION,
    'startup': STARTUP_TIME
}
