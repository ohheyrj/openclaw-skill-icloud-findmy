---
name: openclaw-skill-icloud-findmy
description: Get Apple Find My device locations and battery status using a secure pyicloud wrapper.
homepage: https://github.com/picklepete/pyicloud
metadata: {"clawdbot":{"emoji":"📍"}}
---

# iCloud Find My (Secure)

This skill provides access to Apple Find My device locations and battery status using the `pyicloud` CLI and a secure local wrapper script.

The wrapper script should be installed on PATH as `icloud-findmy`.

Family Sharing support is optional.

---

## Execution Target

This skill executes on a designated macOS node where `pyicloud` is installed and an authenticated session exists. The agent invokes the wrapper remotely (e.g. via SSH) against that node — it does **not** run locally on the agent host.

Do not install `pyicloud` or the wrapper on the agent host. The agent host has no Apple ID session and cannot reach Find My; installing locally will not make this skill work and may cause the agent to mistakenly target itself.

The target macOS node must have:

- `pyicloud` installed (provides the `icloud` CLI)
- The `icloud-findmy` wrapper on `PATH`
- A current authenticated pyicloud session for the relevant Apple ID

---

## When to Use (Triggers)

Use this skill when the user asks:

- Where is my phone, watch, iPad, or Mac?
- Where am I right now?
- Is my device charging?
- What battery levels do my devices have?
- Show my Find My devices
- Check device locations or status

---

## Setup

### 1. Install Dependencies

brew install pipx
pipx install pyicloud

### 2. Install Wrapper Script

cp scripts/icloud-findmy.py /usr/local/bin/icloud-findmy
chmod +x /usr/local/bin/icloud-findmy

### 3. Authenticate (One-Time)

Run:

icloud --username their.email@example.com --list

If Family Sharing devices should also be included:

icloud --username their.email@example.com --with-family --list

The user will enter their password and complete Apple 2FA.

The authenticated session is stored locally and typically lasts 1–2 months.

### 4. Store Apple ID

Add the Apple ID to workspace configuration:

## iCloud Find My
Apple ID: their.email@example.com
Include Family Devices: true

`Include Family Devices` is optional.

---

## Commands

### List All Devices

icloud-findmy --username APPLE_ID list

Returns structured JSON describing all devices.

---

### Get Device Details (Single Device)

icloud-findmy --username APPLE_ID device --name "Richard's iPhone"

The `--name` argument is required.

Matching is case-insensitive with fuzzy fallback.

---

### Get Device Locations

All devices:

icloud-findmy --username APPLE_ID location

Single device:

icloud-findmy --username APPLE_ID location --name "Richard's iPhone"

When `--name` is omitted, locations for all devices are returned.

Example output:

{
  "name": "Richard's iPhone",
  "location": {
    "latitude": 51.43788,
    "longitude": -0.16075,
    "horizontalAccuracy": 4.08,
    "isOld": false
  },
  "timestamp": "2026-03-02T12:34:56+00:00"
}

---

### Get Battery Status

All devices:

icloud-findmy --username APPLE_ID battery

Single device:

icloud-findmy --username APPLE_ID battery --name "Apple Watch Ultra 2"

When `--name` is omitted, battery status for all devices is returned.

Example output:

{
  "name": "Apple Watch Ultra 2",
  "battery_percent": 75.0,
  "battery_status": "NotCharging"
}

---

## Behaviour Notes

- pyicloud outputs Python-style literals (single quotes, None, False)
- The wrapper safely parses data using Python literal parsing
- Battery levels are normalized to percentage values (0–100)
- Location timestamps are converted to ISO-8601 format

---

## Security Model

- No dynamic code execution
- No unsafe parsing techniques
- External commands executed without shell usage
- Inputs validated before execution
- Credentials handled only by pyicloud session storage

---

## Session Maintenance

The pyicloud session expires every 1–2 months. Set up a cron job to verify the session is still valid.

### Example Cron (daily at 9am)
```
0 9 * * * icloud-findmy --username APPLE_ID list > /dev/null 2>&1 || echo "icloud-findmy session expired" >> /var/log/icloud-findmy.log
```

If the agent encounters an authentication error during normal use, it should alert the user using the notification channel configured in `tools.md` and suggest re-running:
```
icloud --username APPLE_ID --list
```

---

## Notes

- Requires macOS
- Apple Find My must be enabled on devices
- Family Sharing support is optional
- Location updates typically occur every 1–5 minutes while devices are active