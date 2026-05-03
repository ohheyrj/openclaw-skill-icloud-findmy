# iCloud Find My — OpenClaw Skill

A secure OpenClaw skill for accessing Apple **Find My** device locations and battery status using `pyicloud`.

This project replaces fragile shell parsing with a structured, agent-friendly interface.

---

## Why This Exists

The standard pyicloud CLI outputs human-readable text, not JSON.

Many examples online suggest unsafe parsing techniques (`eval()`), which introduce security risks.

This skill provides:

- ✅ Safe parsing
- ✅ Structured JSON output
- ✅ Reliable agent integration
- ✅ No shell grep pipelines
- ✅ OpenClaw security scanner friendly

---

## Architecture

```
pyicloud CLI
      ↓
icloud-findmy (Python wrapper)
      ↓
Structured JSON
      ↓
OpenClaw Skill
```

The wrapper converts pyicloud output into normalized device objects.

---

## Installation

### Install pyicloud

```bash
brew install pipx
pipx install pyicloud
```

### Authenticate

```bash
icloud --username you@icloud.com --with-family --list
```

Complete password + 2FA.

Session persists locally.

---

## Usage

### List devices

```bash
icloud-findmy --username you@icloud.com list
```

---

### Get device

```bash
icloud-findmy --username you@icloud.com device --name "Richard's iPhone"
```

---

### Get location

```bash
icloud-findmy --username you@icloud.com location --name "Richard's iPhone"
```

---

### Get battery

```bash
icloud-findmy --username you@icloud.com battery --name "Apple Watch Ultra 2"
```

---

## Output Schema

### Device

```json
{
  "name": "Richard's iPhone",
  "display_name": "iPhone 17 Pro Max",
  "device_class": "iPhone",
  "battery_percent": 75,
  "battery_status": "NotCharging",
  "location": {
    "latitude": 51.43,
    "longitude": -0.16
  }
}
```

---

## Security Model

- Uses `ast.literal_eval()` for safe parsing
- Never executes dynamic code
- No credential storage beyond pyicloud session
- Compatible with OpenClaw security scanning

---

## Requirements

- macOS
- Python 3.10+
- pyicloud
- Apple ID with Find My enabled

---

## Limitations

- Apple does not provide official Find My API access
- Location may be cached
- Some accessories may not report battery/location

---

## Future Ideas

- Home/away detection
- Background battery alerts
- Geofence triggers
- Automatic location context for agents
- Multi-user support

---

## Credits

- pyicloud: https://github.com/picklepete/pyicloud
- Apple Find My ecosystem