---
name: openclaw-skill-icloud-findmy
description: Get Apple Find My device locations and battery status using a secure pyicloud wrapper.
homepage: https://github.com/picklepete/pyicloud
metadata: {"clawdbot":{"emoji":"📍"}}
---

# iCloud Find My (Secure)

Access Apple Find My device locations and battery status via a secure `pyicloud` wrapper.

Installation, authentication, and session maintenance are one-time operator tasks and live in `README.md` — they do not belong in agent context.

---

## Execution Target

This skill runs on a designated macOS node where `pyicloud` is installed and an authenticated session exists. The agent does not run it locally.

Invoke every command via the node runner:

```
nodes.run(node="<target-node>", command=["icloud-findmy", "--username", "<APPLE_ID>", ...])
```

The target node, Apple ID, and family-sharing flag are stored in the workspace configuration (`TOOLS.md` or equivalent).

---

## When to Use (Triggers)

- Where is my phone, watch, iPad, or Mac?
- Where am I right now?
- Is my device charging?
- What battery levels do my devices have?
- Show my Find My devices
- Check device locations or status

---

## Commands

All commands execute on the target node. Wrap each in `nodes.run(node="<target>", command=[...])`.

### List all devices

```
icloud-findmy --username APPLE_ID list
```

Returns structured JSON for every device.

---

### Get a single device

```
icloud-findmy --username APPLE_ID device --name "Richard's iPhone"
```

`--name` is required. Matching is case-insensitive with fuzzy fallback.

---

### Get device locations

All devices:

```
icloud-findmy --username APPLE_ID location
```

Single device:

```
icloud-findmy --username APPLE_ID location --name "Richard's iPhone"
```

Example output:

```json
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
```

---

### Get battery status

All devices:

```
icloud-findmy --username APPLE_ID battery
```

Single device:

```
icloud-findmy --username APPLE_ID battery --name "Apple Watch Ultra 2"
```

Example output:

```json
{
  "name": "Apple Watch Ultra 2",
  "battery_percent": 75.0,
  "battery_status": "NotCharging"
}
```

---

## Behaviour Notes

- pyicloud outputs Python-style literals (single quotes, `None`, `False`); the wrapper parses them safely with `ast.literal_eval`.
- Battery levels are normalized to 0–100.
- Location timestamps are ISO-8601.

---

## Recovery

If a command returns an authentication error, the pyicloud session on the target node has expired. Tell the user to re-authenticate on the target node:

```
icloud --username <APPLE_ID> --list
```

This requires their Apple password and a 2FA code. Do not attempt to install or recover the session yourself — the full procedure is in `README.md`.
