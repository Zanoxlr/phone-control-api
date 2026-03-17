# Phone Control API

A minimal Python REST API for controlling Android phone operations via ADB shell scripts.

**Status:** ✅ Production Ready  
**Local Only:** Runs on localhost:5000 (no external access)  
**Multi-Phone:** Target any phone by passing `device_ip` on every request

## Features

- ✅ Create contacts with automatic dialer prefill
- ✅ Send SMS messages
- ✅ Get call history (with optional datetime filtering)
- ✅ Get SMS messages (with optional datetime filtering)
- ✅ Real-time unified monitoring (dialer, SMS, calls, contacts)
- ✅ Multi-phone support via `device_ip` parameter

## Endpoints

### 1. Create Contact
```bash
POST /api/create_contact
{
  "device_ip": "100.103.46.48",
  "full_name": "John Doe",
  "phone_number": "+38641234567"
}
```

### 2. Send SMS
```bash
POST /api/send_sms
{
  "device_ip": "100.103.46.48",
  "phone_number": "+38641234567",
  "message": "Hello from API!"
}
```

### 3. Get Call History
```bash
GET /api/get_calls?device_ip=100.103.46.48
GET /api/get_calls?device_ip=100.103.46.48&since=2026-03-16%2018:00:00
```

### 4. Get SMS Messages
```bash
GET /api/get_sms?device_ip=100.103.46.48
GET /api/get_sms?device_ip=100.103.46.48&since=2026-03-16%2018:00:00
```

### 5. Unified Monitor
```bash
GET /api/unified_monitor?device_ip=100.103.46.48
```

### Targeting Different Phones
```bash
# Phone A
GET /api/get_calls?device_ip=100.103.46.48

# Phone B
GET /api/get_calls?device_ip=100.103.55.21
```

## Parameters

| Parameter  | Required | Description |
|------------|----------|-------------|
| `device_ip` | **Yes** | Tailscale IP of the target Android phone |
| `since`     | No       | Filter results after this datetime (`YYYY-MM-DD HH:MM:SS`) |

`device_ip` is **required** on every request. The API returns `400` if it is missing.

## Setup

```bash
pip install -r requirements.txt
python app.py
```

## Scripts Required

Each script receives `device_ip` as `$1` and uses `adb -s $1:5555` to target the correct phone:

- `/tmp/create_contact_full.sh` - Contact creation + dialer prefill (used by `/api/create_contact`)
- `/tmp/send_sms.sh` - SMS sending (used by `/api/send_sms`)
- `/tmp/get_calls.sh` - Call history (used by `/api/get_calls`)
- `/tmp/get_sms.sh` - SMS history (used by `/api/get_sms`)
- `/root/.openclaw/workspace/unified_monitor.sh` - Monitoring (used by `/api/unified_monitor`)

## Architecture

```
Another Service (localhost)
        ↓
Phone Control API (127.0.0.1:5000)
        ↓  device_ip passed as $1 to every script
Shell Scripts (adb -s $DEVICE_IP:5555)
        ↓  Tailscale VPN
  ┌─────┴──────┐
Phone A        Phone B  ...
(100.103.46.48) (100.103.xx.xx)
```

## License

MIT
