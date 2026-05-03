#!/usr/bin/env python3

from __future__ import annotations

import argparse
import ast
import json
import re
import subprocess
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

SEP_LINE = "------------------------------"
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


# ----------------------------
# Validation
# ----------------------------

def validate_username(username: str) -> str:
    username = (username or "").strip()
    if not EMAIL_RE.match(username):
        raise ValueError("Invalid --username (expected Apple ID email).")
    return username


def validate_device_name(name: str) -> str:
    name = (name or "").strip()
    if not name:
        raise ValueError("Invalid --name (empty).")
    if len(name) > 200:
        raise ValueError("Invalid --name (too long).")
    return name


# ----------------------------
# Helpers
# ----------------------------

def ts_ms_to_iso(ts_ms: Any) -> Optional[str]:
    if isinstance(ts_ms, (int, float)) and ts_ms > 0:
        return datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc).isoformat()
    return None


def run_icloud(username: str, with_family: bool) -> str:
    username = validate_username(username)

    cmd = ["icloud", "--username", username]
    if with_family:
        cmd.append("--with-family")
    cmd.append("--list")

    return subprocess.check_output(cmd, text=True)


# ----------------------------
# Parsing
# ----------------------------

def parse_output(text: str) -> List[Dict[str, Any]]:
    blocks = [b.strip() for b in text.split(SEP_LINE) if b.strip()]
    devices: List[Dict[str, Any]] = []

    for block in blocks:
        d: Dict[str, Any] = {
            "name": None,
            "display_name": None,
            "device_class": None,
            "device_model": None,
            "battery_percent": None,
            "battery_status": None,
            "location": None,
            "timestamp": None,
        }

        for line in block.splitlines():
            if " - " not in line:
                continue

            key, val = line.split(" - ", 1)
            key = key.strip()
            val = val.strip()

            if key == "Name":
                d["name"] = val

            elif key == "Display Name":
                d["display_name"] = val

            elif key == "Device Class":
                d["device_class"] = val

            elif key == "Device Model":
                d["device_model"] = val

            elif key == "Battery Level":
                try:
                    d["battery_percent"] = round(float(val) * 100, 1)
                except ValueError:
                    pass

            elif key == "Battery Status":
                d["battery_status"] = val

            elif key == "Location":
                if val != "None":
                    loc = ast.literal_eval(val)
                    d["location"] = {
                        "latitude": loc.get("latitude"),
                        "longitude": loc.get("longitude"),
                        "horizontalAccuracy": loc.get("horizontalAccuracy"),
                        "isOld": loc.get("isOld"),
                    }
                    d["timestamp"] = ts_ms_to_iso(loc.get("timeStamp"))

        devices.append(d)

    return devices


# ----------------------------
# Device lookup
# ----------------------------

def find_device(devices: List[Dict[str, Any]], query: str):
    q = query.casefold()

    for d in devices:
        if (d.get("name") or "").casefold() == q:
            return d
        if (d.get("display_name") or "").casefold() == q:
            return d

    for d in devices:
        if q in (d.get("name") or "").casefold():
            return d
        if q in (d.get("display_name") or "").casefold():
            return d

    return None


# ----------------------------
# Output builders
# ----------------------------

def build_locations(devices):
    return [
        {
            "name": d["display_name"] or d["name"],
            "location": d["location"],
            "timestamp": d["timestamp"],
        }
        for d in devices
    ]


def build_batteries(devices):
    return [
        {
            "name": d["display_name"] or d["name"],
            "battery_percent": d["battery_percent"],
            "battery_status": d["battery_status"],
        }
        for d in devices
    ]


# ----------------------------
# Main CLI
# ----------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--username", required=True)
    ap.add_argument("--with-family", action="store_true")

    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("list")

    p_device = sub.add_parser("device")
    p_device.add_argument("--name", required=True)

    p_loc = sub.add_parser("location")
    p_loc.add_argument("--name")

    p_bat = sub.add_parser("battery")
    p_bat.add_argument("--name")

    args = ap.parse_args()

    raw = run_icloud(args.username, args.with_family)
    devices = parse_output(raw)

    # ---- list ----
    if args.cmd == "list":
        print(json.dumps({"devices": devices}, indent=2))
        return

    # ---- device ----
    if args.cmd == "device":
        name = validate_device_name(args.name)
        d = find_device(devices, name)
        if not d:
            print(json.dumps({"error": "device_not_found"}))
            return
        print(json.dumps(d, indent=2))
        return

    # ---- location ----
    if args.cmd == "location":
        if args.name:
            name = validate_device_name(args.name)
            d = find_device(devices, name)
            if not d:
                print(json.dumps({"error": "device_not_found"}))
                return
            print(json.dumps(build_locations([d])[0], indent=2))
        else:
            print(json.dumps({"devices": build_locations(devices)}, indent=2))
        return

    # ---- battery ----
    if args.cmd == "battery":
        if args.name:
            name = validate_device_name(args.name)
            d = find_device(devices, name)
            if not d:
                print(json.dumps({"error": "device_not_found"}))
                return
            print(json.dumps(build_batteries([d])[0], indent=2))
        else:
            print(json.dumps({"devices": build_batteries(devices)}, indent=2))
        return


if __name__ == "__main__":
    main()