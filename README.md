# Phone Control API

A minimal Python REST API for controlling Android phone operations via ADB shell scripts.

**Status:** ✅ Production Ready
**Local Only:** Runs on localhost:5000 (no external access)
**Database:** SQLite (optional for future enhancements)

## Features

- ✅ Create contacts with automatic dialer prefill
- ✅ Send SMS messages
- ✅ Get call history (with optional datetime filtering)
- ✅ Get SMS messages (with optional datetime filtering)
- ✅ Real-time unified monitoring (dialer, SMS, calls, contacts)

## Endpoints

### 1. Create Contact
```bash
POST /api/create_contact
{
  "contact_id": 10922,
  "full_name": "John Doe",
  "phone_number": "+38641234567"
}
```

### 2. Send SMS
```bash
POST /api/send_sms
{
  "phone_number": "+38641234567",
  "message": "Hello from API!"
}
```

### 3. Get Call History
```bash
GET /api/get_calls
GET /api/get_calls?since=2026-03-16%2018:00:00
```

### 4. Get SMS Messages
```bash
GET /api/get_sms
GET /api/get_sms?since=2026-03-16%2018:00:00
```

### 5. Unified Monitor
```bash
GET /api/unified_monitor
```

## Setup

```bash
pip install -r requirements.txt
python app.py
```

## Scripts Required

- `/tmp/add_contact.sh` - Contact creation
- `/tmp/send_sms.sh` - SMS sending
- `/tmp/get_calls.sh` - Call history
- `/tmp/get_sms.sh` - SMS history
- `/root/.openclaw/workspace/unified_monitor.sh` - Monitoring

## Architecture

```
Phone Control API (Python/Flask)
    ↓
Shell Scripts (ADB Wrappers)
    ↓
Android Device (ADB/Tailscale)
```

## Storage

- Local SQLite database (future enhancement)
- Device IP stored in config on startup
- All operations via ADB commands (no local storage required initially)

## License

MIT
