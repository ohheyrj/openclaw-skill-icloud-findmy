# iCloud Find My — OpenClaw Skill

An OpenClaw skill for accessing Apple **Find My** device locations and battery status via the `pyicloud` CLI on a designated macOS node.

The skill is documentation only — there is no wrapper script. It records:

- Where the underlying `icloud` command runs (a designated macOS node, **not** the agent host)
- Which native pyicloud command shape to invoke
- The response schema and how to interpret each field
- Recovery procedure when the session expires

---

## Why This Is Forked

This repo started as the `icloud-findmy` skill from ClawHub. It was forked after an incident where the agent host tried to auto-install `pyicloud` on itself, because the original skill's `clawdbot` metadata declared `requires.bins` and an `install` step that resolved against the agent host.

In practice this skill must run on a designated macOS node — the one with an authenticated pyicloud session and Find My access. Installing on the agent host can't make the skill work and only causes the agent to mistakenly target itself.

This fork:

- **Removes the auto-install metadata** so the agent never tries to install pyicloud locally.
- **Adds an explicit Execution Target** in `SKILL.md` so the agent knows the skill runs remotely via `nodes.run`.
- **Drops the wrapper script.** The original skill bundled a Python wrapper to convert pyicloud's text output into JSON. pyicloud 2.x emits JSON natively (`icloud devices list --locate --format json`), so the wrapper is no longer needed. Less code to maintain, no parser to break when pyicloud's text format drifts.

---

## Installation

> ⚠️ **Install on the target macOS node, not on the agent host.**
> The agent does not run this skill locally. It invokes `icloud` remotely via `nodes.run`. Installing on the agent host gives it nothing to call into and risks the agent mistakenly targeting itself — which is the original incident this fork was created to prevent.

These are one-time operator steps. Run them on the macOS machine that will hold the authenticated pyicloud session (in an openclaw setup, that's the node bound to this skill — e.g. `little-claw`).

### 1. Install pyicloud

```bash
brew install pipx
pipx install pyicloud
```

This provides the `icloud` CLI. Version 2.x or later is required — earlier versions don't emit JSON natively.

### 2. Authenticate

```bash
icloud auth login --username you@icloud.com
```

You'll be prompted for your Apple password and a 2FA code on a trusted Apple device. Confirm "Trust this device" when offered — this elevates the session for full CloudKit access.

The session persists locally on the target node and typically lasts 1–2 months.

### 3. Verify

```bash
icloud devices list --locate --format json
```

Should return a JSON array of devices with battery and (where available) location.

### 4. Record the binding in your workspace

Add the target node and Apple ID to your workspace config (e.g. `TOOLS.md`), so the agent knows which node to call against:

```
## iCloud Find My
Target Node: little-claw
Apple ID: you@icloud.com
```

---

## Session Maintenance

The pyicloud session expires every 1–2 months. Either run a heartbeat task that calls `icloud devices list --format json` on the target node and pings you on failure, or set a cron on the target node:

```
0 9 * * * icloud devices list --format json > /dev/null 2>&1 || echo "icloud session expired" >> /var/log/icloud.log
```

When the session expires, re-run step 2 above.

---

## Recovery

If the agent reports an authentication error (HTTP 421, "Invalid global session"), the session has lapsed. Re-run step 2 on the target node.

Note: pyicloud has different trust scopes per service. If you've authenticated for Find My (`icloud devices`) but get `421` on other services like `icloud reminders`, those services need a fully-trusted session — make sure you confirmed "Trust this device" during authentication.

---

## Limitations

- Apple does not provide official Find My API access; pyicloud uses a reverse-engineered endpoint.
- Location can be cached up to several minutes; `--locate` triggers a live ping but is rate-limited.
- Some accessories (AirPods, accessories without GPS) often report `null` location and `0.0/Unknown` battery even when in use.

---

## Requirements

- macOS on the target node
- Python 3.10+
- `pyicloud` 2.x
- Apple ID with Find My enabled on relevant devices

---

## Credits

- pyicloud: https://github.com/picklepete/pyicloud (the underlying library and CLI)
- ClawHub `icloud-findmy` skill (original, pre-fork)
