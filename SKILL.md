---
name: openclaw-skill-icloud-findmy
description: Get Apple Find My device locations and battery status via pyicloud.
homepage: https://github.com/ohheyrj/openclaw-skill-icloud-findmy
metadata: {"clawdbot":{"emoji":"📍"}}
---

# iCloud Find My

Access Apple Find My device locations and battery status via the `pyicloud` CLI on a designated macOS node.

Installation, authentication, and session maintenance are one-time operator tasks and live in `README.md` — they do not belong in agent context.

---

## Execution Target

This skill runs on a designated macOS node where `pyicloud` is installed and an authenticated session exists. The agent does not run it locally.

Invoke via the node runner:

```
nodes.run(
  node="<target-node>",
  command=["icloud", "devices", "list", "--locate", "--format", "json"]
)
```

The target node and Apple ID are stored in the workspace configuration (`TOOLS.md` or equivalent).

---

## When to Use (Triggers)

- Where is my phone, watch, iPad, or Mac?
- Where am I right now?
- Is my device charging?
- What battery levels do my devices have?
- Show my Find My devices
- Check device locations or status

---

## The Command

```
icloud devices list --locate --format json
```

One call returns everything: device metadata, battery, and (with `--locate`) live location. There are no separate per-device subcommands — fetch the full list, then filter in your own code.

For other flags (family-sharing scope, etc.), check `icloud devices --help` on the target node.

---

## Response Shape

Returns a JSON array. Each entry:

```json
{
  "id": "opaque-base64-string",
  "name": "Richard's iPhone",
  "display_name": "iPhone 17 Pro Max",
  "device_class": "iPhone",
  "device_model": "iPhone17-1-8-0",
  "battery_level": 0.13,
  "battery_status": "NotCharging",
  "location": {
    "latitude": 51.43786,
    "longitude": -0.16078,
    "horizontalAccuracy": 6.18,
    "timeStamp": 1777848724174,
    "isOld": false,
    "isInaccurate": false,
    "locationFinished": true,
    "positionType": "Wifi"
  }
}
```

### Field notes

- `id` — stable opaque identifier. Use this when disambiguating by exact device.
- `name` — user-set name. `display_name` — Apple's product name. Match against either when picking a device by user reference.
- `device_class` — `iPhone` | `iPad` | `MacBookPro` | `Watch` | `Macmini` | `Accessory` | etc.
- `battery_level` — float `0.0–1.0`. **Multiply by 100 for percent.**
- `battery_status` — `Charging` | `NotCharging` | `Charged` | `Unknown`.
- `location` — object or `null`. When non-null:
  - `timeStamp` is **milliseconds since epoch** (Apple's convention).
  - `isOld: true` means cached/stale — flag this to the user.
  - `isInaccurate: true` means low-confidence fix.
  - `locationFinished: false` means partial fix; another call may improve it.
  - `positionType` narrows confidence: `GPS` > `Wifi` > `Cellular` > `Unknown`.

---

## Picking a Device

Match by `name` or `display_name` over the array (case-insensitive substring is usually enough). Default to the iPhone for "where am I" / location queries — it's the device the user actually carries.

---

## Behaviour Notes

- Devices that haven't checked in recently come back with `battery_level: 0.0`, `battery_status: "Unknown"`, `location: null`. That's not an error — Apple just hasn't heard from the device. Surface this as "no recent data" rather than treating it as a failure.
- `--locate` requests a live ping. Apple rate-limits; calling repeatedly within seconds returns the same value.
- Battery values for AirPods and similar accessories are often `0.0/Unknown` even when in use — Apple's API exposes them inconsistently.

---

## Recovery

If the call returns an authentication error (HTTP 421, "Invalid global session"), the pyicloud session on the target node has expired. Tell the user to re-authenticate on the target node:

```
icloud auth login --username <APPLE_ID>
```

This requires their Apple password and a 2FA code on a trusted Apple device. Don't attempt to recover the session yourself — the full procedure is in `README.md`.
