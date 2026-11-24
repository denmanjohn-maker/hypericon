#!/usr/bin/env python3
"""Fails if any bundled theme is missing a manifest field, a category icon or a place icon."""
import json
import os
import struct
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Themes")
categories = [c["id"] for c in json.load(open(os.path.join(ROOT, "categories.json")))]
places = [p["id"] for p in json.load(open(os.path.join(ROOT, "places.json")))]
errors = []


def edges_transparent(path, band=40):
    """Artwork is drawn over HyperIcon's own folder, so its outer border must be empty. Place icons are whole
    icons and may use more of the canvas, but still keep a small margin like any macOS icon."""
    try:
        from PIL import Image
    except ImportError:
        return True
    alpha = Image.open(path).convert("RGBA").getchannel("A")
    w, h = alpha.size
    for box in ((0, 0, w, band), (0, h - band, w, h), (0, 0, band, h), (w - band, 0, w, h)):
        if alpha.crop(box).getbbox():
            return False
    return True
themes = sorted(d for d in os.listdir(ROOT) if os.path.isdir(os.path.join(ROOT, d)) and not d.startswith("_"))
BASE_COLOURS = ["blue", "gray", "green", "purple", "yellow", "red", "orange"]


def png_info(path):
    with open(path, "rb") as f:
        header = f.read(24)
    if header[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    return struct.unpack(">II", header[16:24])


for colour in BASE_COLOURS:
    path = os.path.join(ROOT, "_base", f"{colour}.png")
    if not os.path.exists(path):
        errors.append(f"_base: missing {colour}.png")
    elif png_info(path) != (512, 512):
        errors.append(f"_base: {colour}.png is not a 512x512 PNG")

for theme in themes:
    base = os.path.join(ROOT, theme)
    try:
        manifest = json.load(open(os.path.join(base, "theme.json")))
    except (OSError, ValueError) as exc:
        errors.append(f"{theme}: theme.json unreadable ({exc})")
        continue
    for field in ("id", "name", "group", "description"):
        if not manifest.get(field):
            errors.append(f"{theme}: theme.json has no '{field}'")
    if manifest.get("id") != theme:
        errors.append(f"{theme}: id '{manifest.get('id')}' does not match its folder name")
    for name in categories + ["preview"]:
        path = os.path.join(base, f"{name}.png")
        if not os.path.exists(path):
            errors.append(f"{theme}: missing {name}.png")
            continue
        size = png_info(path)
        if size is None:
            errors.append(f"{theme}: {name}.png is not a PNG")
        elif name != "preview" and size != (512, 512):
            errors.append(f"{theme}: {name}.png is not 512x512")
        elif name != "preview" and not edges_transparent(path):
            errors.append(f"{theme}: {name}.png is not transparent at the edges (artwork only, no folder or background)")

    for place in places:
        path = os.path.join(base, "places", f"{place}.png")
        if not os.path.exists(path):
            errors.append(f"{theme}: missing places/{place}.png")
        elif png_info(path) != (512, 512):
            errors.append(f"{theme}: places/{place}.png is not a 512x512 PNG")
        elif not edges_transparent(path, band=16):
            errors.append(f"{theme}: places/{place}.png reaches the edge (keep a 16 px transparent margin)")

if errors:
    print("\n".join(errors))
    sys.exit(1)
print(f"{len(themes)} themes x {len(categories)} categories + {len(places)} places OK")
