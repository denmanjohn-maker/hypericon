#!/usr/bin/env python3
"""Fails if any bundled theme is missing a manifest field or a category icon."""
import json
import os
import struct
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Themes")
categories = [c["id"] for c in json.load(open(os.path.join(ROOT, "categories.json")))]
errors = []
themes = sorted(d for d in os.listdir(ROOT) if os.path.isdir(os.path.join(ROOT, d)))

for theme in themes:
    base = os.path.join(ROOT, theme)
    try:
        manifest = json.load(open(os.path.join(base, "theme.json")))
    except (OSError, ValueError) as exc:
        errors.append(f"{theme}: theme.json unreadable ({exc})")
        continue
    for field in ("id", "name", "group", "description", "accent"):
        if not manifest.get(field):
            errors.append(f"{theme}: theme.json has no '{field}'")
    if manifest.get("id") != theme:
        errors.append(f"{theme}: id '{manifest.get('id')}' does not match its folder name")
    for name in categories + ["preview"]:
        path = os.path.join(base, f"{name}.png")
        if not os.path.exists(path):
            errors.append(f"{theme}: missing {name}.png")
            continue
        with open(path, "rb") as f:
            header = f.read(24)
        if header[:8] != b"\x89PNG\r\n\x1a\n":
            errors.append(f"{theme}: {name}.png is not a PNG")
        elif name != "preview" and struct.unpack(">II", header[16:24]) != (512, 512):
            errors.append(f"{theme}: {name}.png is not 512x512")

if errors:
    print("\n".join(errors))
    sys.exit(1)
print(f"{len(themes)} themes x {len(categories)} categories OK")
