# iCloud Find My — OpenClaw Skill

A secure OpenClaw skill for accessing Apple **Find My** device locations and battery status using `pyicloud`.

This project replaces fragile shell parsing with a structured, agent-friendly interface.

---

## Why This Is Forked

This repo started as the `icloud-findmy` skill from ClawHub. It was forked after an incident where the agent host tried to auto-install `pyicloud` on itself, because the original skill's `clawdbot` metadata declared `requires.bins` and an `install` step that resolved against the agent host.

In practice this skill must run on a designated macOS node — the one with an authenticated pyicloud session and Find My access. Installing on the agent host can't make the skill work and only causes the agent to mistakenly target itself.

This fork:

- Removes the auto-install metadata so the agent never tries to install pyicloud locally.
- Adds an explicit **Execution Target** section in `SKILL.md` documenting that the wrapper runs on a remote macOS node.
- Treats install on the target node as a one-time manual step.

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

> ⚠️ **Install on the target macOS node, not on the agent host.**
> The agent does not run this skill locally. It invokes the wrapper remotely via `nodes.run`. Installing on the agent host gives it nothing to call into and risks the agent mistakenly targeting itself — which is the original incident this fork was created to prevent.

These are one-time operator steps. Run them on the macOS machine that will hold the authenticated pyicloud session (in an openclaw setup, that's the node bound to this skill — e.g. `little-claw`).

### 1. Install pyicloud

```bash
brew install pipx
pipx install pyicloud
```

### 2. Install the wrapper

From a clone of this repo on the target node:

```bash
cp scripts/icloud-findmy.py /usr/local/bin/icloud-findmy
chmod +x /usr/local/bin/icloud-findmy
```

Verify:

```bash
which icloud-findmy
icloud-findmy --help
```

### 3. Authenticate

```bash
icloud --username you@icloud.com --list
```

For Family Sharing devices:

```bash
icloud --username you@icloud.com --with-family --list
```

You'll be prompted for your Apple password and a 2FA code. The session persists locally on the target node and typically lasts 1–2 months.

### 4. Record the binding in your workspace

Add the target node, Apple ID, and family flag to your workspace config (e.g. `TOOLS.md`), so the agent knows which node to call against:

```
## iCloud Find My
Target Node: little-claw
Apple ID: you@icloud.com
Include Family Devices: true
```

---

## Session Maintenance

The pyicloud session expires every 1–2 months. Either run a heartbeat task that calls `icloud-findmy ... list` on the target node and pings you on failure, or set a cron on the target node:

```
0 9 * * * icloud-findmy --username APPLE_ID list > /dev/null 2>&1 || echo "icloud-findmy session expired" >> /var/log/icloud-findmy.log
```

When the session expires, re-run step 3 above.

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