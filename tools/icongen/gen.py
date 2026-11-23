#!/usr/bin/env python3
"""HyperIcon icon generator.

Builds every theme x category icon as SVG, renders to 512px PNG with headless Chromium
(tools/icongen/render.js), post-processes, and writes Themes/<id>/{theme.json,preview.png,*.png}.

Usage: python3 tools/icongen/gen.py [theme-id ...]
"""
import json
import os
import subprocess
import sys
import tempfile

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from glyphs import CATEGORIES, GLYPHS, LABELS  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "Themes")
SIZE = 512

SHAPES = {
    "round": (
        "M40 150Q40 118 72 118H196Q212 118 222 130L240 150H440Q472 150 472 182V400Q472 432 440 432H72Q40 432 40 400Z",
        "M40 206Q40 178 68 178H444Q472 178 472 206V404Q472 436 440 436H72Q40 436 40 404Z",
    ),
    "sharp": (
        "M40 118H200L224 150H472V432H40Z",
        "M40 178H472V436H40Z",
    ),
    "chamfer": (
        "M40 140 62 118H196L228 150H450L472 172V432H40Z",
        "M40 200 62 178H472V414L450 436H40Z",
    ),
}

MONO = 'font-family="JetBrains Mono, DejaVu Sans Mono, monospace" font-weight="700"'


def scallops(depths, y0=214, fill="#fff"):
    """A band hugging the top of the round front shape with a scalloped lower edge."""
    w = 432 / len(depths)
    d = f"M40 206Q40 178 68 178H444Q472 178 472 206V{y0}"
    for dep in depths:
        d += f"q{-w / 2:.1f} {dep} {-w:.1f} 0"
    return f'<path d="{d}Z" fill="{fill}"/>'


def lin(id_, stops, x2=0, y2=1):
    s = "".join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in stops)
    return f'<linearGradient id="{id_}" x1="0" y1="0" x2="{x2}" y2="{y2}">{s}</linearGradient>'


def glow(id_, std=6):
    return (f'<filter id="{id_}" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="{std}" result="b"/>'
            f'<feMerge><feMergeNode in="b"/><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>')


FILTERS = (
    '<filter id="fshadow" x="-20%" y="-20%" width="140%" height="150%">'
    '<feDropShadow dx="0" dy="10" stdDeviation="12" flood-color="#000" flood-opacity=".3"/></filter>'
    '<filter id="gshadow" x="-20%" y="-20%" width="140%" height="140%">'
    '<feDropShadow dx="0" dy="3" stdDeviation="3" flood-color="#000" flood-opacity=".3"/></filter>'
    '<filter id="neon" x="-30%" y="-30%" width="160%" height="160%">'
    '<feMorphology in="SourceGraphic" operator="erode" radius="2.6" result="e"/>'
    '<feComposite in="SourceGraphic" in2="e" operator="out" result="o"/>'
    '<feGaussianBlur in="o" stdDeviation="7" result="b"/>'
    '<feMerge><feMergeNode in="b"/><feMergeNode in="b"/><feMergeNode in="o"/></feMerge></filter>'
    + glow("glow") + glow("softglow", 3)
)


def compose(cat, *, shape="round", back, front, defs="", under="", over="", top="", glyph="#fff",
            gfilter="gshadow", ffilter="fshadow", gcenter=(256, 310), gsize=150, pre=""):
    bd, fd = SHAPES[shape]
    gx, gy = gcenter[0] - gsize / 2, gcenter[1] - gsize / 2
    gf = f' filter="url(#{gfilter})"' if gfilter else ""
    ff = f' filter="url(#{ffilter})"' if ffilter else ""
    g = ""
    if GLYPHS[cat]:
        g = (f'<mask id="gm" maskUnits="userSpaceOnUse" x="0" y="0" width="{SIZE}" height="{SIZE}">'
             f'<g transform="translate({gx} {gy}) scale({gsize / 100})">{GLYPHS[cat]}</g></mask>'
             f'<g{gf}><rect width="{SIZE}" height="{SIZE}" fill="{glyph}" mask="url(#gm)"/></g>')
    pre = pre.replace("{BACK}", bd).replace("{FRONT}", fd)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{SIZE}" height="{SIZE}" viewBox="0 0 {SIZE} {SIZE}">'
            f'<defs>{FILTERS}{defs}<clipPath id="fc"><path d="{fd}"/></clipPath></defs>{pre}'
            f'<g{ff}><path d="{bd}" {back}/>{under}<path d="{fd}" {front}/></g>'
            f'<g clip-path="url(#fc)">{over}</g>{g}{top}</svg>')


HEART = "M0 6C0-2 10-2 10 4C10-2 20-2 20 6C20 13 12 17 10 22C8 17 0 13 0 6Z"
LEAF = "M0 0C14-22 44-22 58 0C44 22 14 22 0 0Z"


def dots(points, fill="#fff"):
    return "".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" opacity="{o}"/>' for x, y, r, o in points)


# ---------------------------------------------------------------- themes

def winter(cat):
    return compose(
        cat, back='fill="#8a1620"', front='fill="url(#f)"',
        defs=lin("f", [(0, "#e8434a"), (1, "#b31d27")]),
        under='<path d="M58 124H198" stroke="#fff" stroke-width="16" stroke-linecap="round"/>',
        over=scallops([26, 34, 22, 36, 28, 20, 34, 24, 30, 22])
        + dots([(84, 262, 5, .8), (432, 276, 6, .8), (104, 404, 4, .7), (414, 398, 5, .7), (446, 338, 3, .6),
                (72, 336, 3, .6), (150, 250, 3, .5), (372, 252, 3, .5)]),
        glyph="#fff", gcenter=(256, 326), gsize=140)


def halloween(cat):
    web = "".join(f'<path d="M472 436L{x} {y}" stroke="#2b1040" stroke-width="2.5" opacity=".55"/>'
                  for x, y in ((352, 436), (372, 372), (424, 328), (472, 316)))
    web += "".join(f'<path d="M{472 - r} 436Q{472 - r * .62:.0f} {436 - r * .62:.0f} 472 {436 - r}" fill="none" '
                   f'stroke="#2b1040" stroke-width="2.5" opacity=".55"/>' for r in (40, 76, 112))
    return compose(
        cat, back='fill="#2b1040"', front='fill="url(#f)"',
        defs=lin("f", [(0, "#ff9426"), (1, "#e55a00")]),
        over=scallops([34, 62, 26, 48, 30, 70, 28, 44, 58, 30], fill="#4a1a78") + web,
        glyph="#2b1040", gfilter=None, gcenter=(256, 330), gsize=136)


def valentine(cat):
    spots = [(70, 200, 1.6, -15), (410, 196, 1.9, 12), (84, 372, 1.3, 10), (420, 380, 1.5, -12),
             (236, 190, 1.1, 0), (160, 400, 1.0, 20), (340, 402, 1.1, -18)]
    hearts = "".join(f'<path d="{HEART}" fill="#fff" opacity=".36" transform="translate({x} {y}) rotate({r}) scale({s})"/>'
                     for x, y, s, r in spots)
    return compose(
        cat, back='fill="#b0124f"', front='fill="url(#f)"',
        defs=lin("f", [(0, "#ff8db6"), (1, "#ee3f7c")]),
        under=f'<path d="{HEART}" fill="#ffd1e1" transform="translate(96 124) scale(2.2)"/>',
        over=hearts, glyph="#fff", gcenter=(256, 306), gsize=146)


def harvest(cat):
    leaves = (f'<g transform="translate(60 150) rotate(-38)"><path d="{LEAF}" fill="#b3261e"/>'
              f'<path d="M4 0H70" stroke="#6b1410" stroke-width="3"/></g>'
              f'<g transform="translate(98 172) rotate(-8) scale(.9)"><path d="{LEAF}" fill="#f2c230"/>'
              f'<path d="M4 0H70" stroke="#a87b0c" stroke-width="3"/></g>')
    return compose(
        cat, back='fill="#6b3410"', front='fill="url(#f)"',
        defs=lin("f", [(0, "#eb9a2c"), (1, "#c65f18")]),
        over='<rect x="56" y="194" width="400" height="226" rx="18" fill="none" stroke="#ffe9bd" stroke-width="3.5" '
             'stroke-dasharray="12 9" opacity=".85"/>',
        top=leaves, glyph="#fff3d6", gcenter=(256, 310), gsize=142)


def scifi(cat):
    lines = "".join(f'<path d="M40 {y}H472" stroke="#45f0ff" stroke-width="1" opacity=".1"/>' for y in range(186, 436, 8))
    hud = ('<path d="M58 222V198H84M454 392V416H428" fill="none" stroke="#45f0ff" stroke-width="3"/>'
           f'<text x="96" y="206" {MONO} font-size="13" fill="#45f0ff" opacity=".75">HX-07 // ONLINE</text>'
           + "".join(f'<rect x="{60 + i * 16}" y="412" width="11" height="6" fill="#45f0ff" opacity="{.9 if i < 5 else .25}"/>'
                     for i in range(9)))
    return compose(
        cat, shape="chamfer", back='fill="#0a1a2a" stroke="#2bd9f0" stroke-width="3"',
        front='fill="url(#f)" stroke="#45f0ff" stroke-width="4"',
        defs=lin("f", [(0, "#123752"), (1, "#06121e")]),
        over=lines + hud, glyph="#7df7ff", gfilter="glow", gcenter=(256, 312), gsize=140)


def synthwave(cat):
    grid = '<rect x="40" y="350" width="432" height="90" fill="#180736" opacity=".8"/>'
    grid += "".join(f'<path d="M40 {y}H472" stroke="#37e6ff" stroke-width="2" opacity=".6"/>' for y in (350, 358, 370, 388, 414))
    for b in range(-340, 860, 80):
        x0 = 256 + (b - 256) * (50 / 136)
        grid += f'<path d="M{x0:.0f} 350L{b} 436" stroke="#37e6ff" stroke-width="2" opacity=".6"/>'
    return compose(
        cat, back='fill="#2b0b52"', front='fill="url(#f)"',
        defs=lin("f", [(0, "#ff62a6"), (.55, "#9a36ee"), (1, "#2a1058")]) + lin("gg", [(.2, "#fff36b"), (.8, "#ff9a3c")]),
        over=grid, glyph="url(#gg)", gfilter="softglow", gcenter=(256, 272), gsize=136)


def neon(cat):
    stars = dots([(80, 210, 2, .8), (430, 230, 2, .7), (100, 400, 2, .6), (420, 404, 2, .8), (250, 200, 1.5, .6)], "#fff")
    return compose(
        cat, shape="chamfer", ffilter="glow",
        back='fill="#0b0b14" stroke="#ff2bd6" stroke-width="5"',
        front='fill="#11111c" stroke="#ff2bd6" stroke-width="5"',
        over=stars, glyph="#39ff14", gfilter="neon", gcenter=(256, 308), gsize=150)


def crt(cat):
    scan = '<rect x="40" y="178" width="432" height="258" fill="url(#sl)"/>'
    prompt = f'<text x="62" y="420" {MONO} font-size="22" fill="#35ff6a" filter="url(#softglow)">&gt; _</text>'
    return compose(
        cat, back='fill="#0c1a0c" stroke="#1c5c28" stroke-width="3"',
        front='fill="#021002" stroke="#35ff6a" stroke-width="3"',
        defs='<pattern id="sl" width="6" height="6" patternUnits="userSpaceOnUse">'
             '<rect width="6" height="2" fill="#35ff6a" opacity=".1"/></pattern>',
        over=scan + prompt, glyph="#35ff6a", gfilter="glow", gcenter=(256, 300), gsize=136)


def pixel(cat):
    return compose(
        cat, shape="sharp", ffilter=None, gfilter=None,
        back='fill="#b8641a" stroke="#2b1600" stroke-width="16" stroke-linejoin="miter"',
        front='fill="#ffb52e" stroke="#2b1600" stroke-width="16" stroke-linejoin="miter"',
        over='<rect x="48" y="186" width="416" height="16" fill="#ffe08a"/>'
             '<rect x="48" y="412" width="416" height="16" fill="#d98a17"/>',
        glyph="#2b1600", gcenter=(256, 308), gsize=160)


def platinum(cat):
    bevel = ('<path d="M47 428V185H466" fill="none" stroke="#fff" stroke-width="5"/>'
             '<path d="M465 188V429H50" fill="none" stroke="#7676b4" stroke-width="5"/>')
    return compose(
        cat, shape="sharp", ffilter=None, gfilter=None,
        back='fill="#8d8dc4" stroke="#15152b" stroke-width="5"',
        front='fill="#bfbfee" stroke="#15152b" stroke-width="5"',
        under='<path d="M48 126H196" stroke="#c9c9f2" stroke-width="5"/>',
        over=bevel, glyph="#24244f", gcenter=(256, 308), gsize=148)


def nineties(cat):
    bevel = ('<path d="M47 428V185H466" fill="none" stroke="#fff6c2" stroke-width="6"/>'
             '<path d="M465 188V429H50" fill="none" stroke="#b78a00" stroke-width="6"/>')
    shadow = '<g transform="translate(14 14)" opacity=".32"><path d="{BACK}"/><path d="{FRONT}"/></g>'
    return compose(
        cat, shape="sharp", ffilter=None, gfilter=None, pre=shadow,
        back='fill="#c99700" stroke="#000" stroke-width="5"',
        front='fill="#ffd633" stroke="#000" stroke-width="5"',
        over=bevel, glyph="#00007a", gcenter=(256, 308), gsize=148)


def aqua(cat):
    over = ('<rect x="40" y="178" width="432" height="258" fill="url(#ps)"/>'
            '<ellipse cx="256" cy="186" rx="270" ry="76" fill="#fff" opacity=".42"/>'
            '<ellipse cx="256" cy="452" rx="220" ry="44" fill="#bfe6ff" opacity=".35"/>')
    return compose(
        cat, back='fill="url(#b)"', front='fill="url(#f)" stroke="#0d4aa3" stroke-width="2"',
        defs=lin("b", [(0, "#3d93ee"), (1, "#1557b8")]) + lin("f", [(0, "#8fd2ff"), (1, "#2380e8")])
        + '<pattern id="ps" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="1.4" fill="#fff" opacity=".16"/></pattern>',
        over=over, glyph="#fff", gcenter=(256, 314), gsize=146)


THEMES = [
    dict(id="winter-holiday", name="Winter Holiday", group="Holidays", build=winter, accent="#e8434a", bg="#0f2a3a",
         description="Snow-capped red folders for the festive season."),
    dict(id="halloween", name="Halloween", group="Holidays", build=halloween, accent="#ff9426", bg="#1a0b26",
         description="Pumpkin-orange folders dripping with purple slime."),
    dict(id="valentine", name="Valentine", group="Holidays", build=valentine, accent="#ee3f7c", bg="#fff0f5",
         description="Pink folders scattered with hearts."),
    dict(id="harvest", name="Harvest", group="Holidays", build=harvest, accent="#eb9a2c", bg="#f6ead6",
         description="Warm autumn folders with stitched edges and fallen leaves."),
    dict(id="scifi-hud", name="Sci-Fi HUD", group="Sci-Fi", build=scifi, accent="#45f0ff", bg="#050d16",
         description="Angular starship console panels with a cyan glow."),
    dict(id="synthwave-84", name="Synthwave '84", group="80s", build=synthwave, accent="#ff62a6", bg="#160a2e",
         description="Sunset gradients over a neon grid."),
    dict(id="neon-arcade", name="Neon Arcade", group="80s", build=neon, accent="#ff2bd6", bg="#07070d",
         description="Glowing neon tube outlines straight from the arcade."),
    dict(id="green-phosphor", name="Green Phosphor CRT", group="Computer Retro", build=crt, accent="#35ff6a", bg="#030a03",
         description="Monochrome terminal green with scanlines."),
    dict(id="8-bit-pixel", name="8-Bit Pixel", group="Computer Retro", build=pixel, accent="#ffb52e", bg="#22304a",
         description="Chunky low-resolution pixel art.", pixel=64),
    dict(id="platinum-classic", name="Platinum Classic", group="OS Classics", build=platinum, accent="#8d8dc4", bg="#dcdcdc",
         description="Lavender bevelled folders in the style of late-90s desktops."),
    dict(id="nineties-desktop", name="Nineties Desktop", group="OS Classics", build=nineties, accent="#ffd633", bg="#008080",
         description="Manila yellow, black outlines and hard shadows."),
    dict(id="aqua-gloss", name="Aqua Gloss", group="OS Classics", build=aqua, accent="#2380e8", bg="#e9f2fb",
         description="Glossy pinstriped blue from the early 2000s."),
]


def pixelate(img, grid):
    small = img.resize((grid, grid), Image.BOX)
    r, g, b, a = small.split()
    a = a.point(lambda v: 255 if v >= 110 else 0)
    rgb = Image.merge("RGB", (r, g, b)).quantize(colors=12, method=Image.MEDIANCUT).convert("RGB")
    small = Image.merge("RGBA", (*rgb.split(), a))
    return small.resize(img.size, Image.NEAREST)


def contact_sheet(theme, cats, cols, cell, path):
    from PIL import ImageColor
    rows = (len(cats) + cols - 1) // cols
    pad = cell // 8
    sheet = Image.new("RGBA", (cols * cell + pad * 2, rows * cell + pad * 2), ImageColor.getrgb(theme["bg"]) + (255,))
    for i, c in enumerate(cats):
        icon = Image.open(os.path.join(OUT, theme["id"], f"{c}.png")).resize((cell, cell), Image.LANCZOS)
        sheet.alpha_composite(icon, (pad + (i % cols) * cell, pad + (i // cols) * cell))
    sheet.convert("RGB").save(path, optimize=True)


APP_ICON = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="1024" height="1024" viewBox="0 0 1024 1024"><defs>'
    '<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#6a3df0"/>'
    '<stop offset=".55" stop-color="#e0409a"/><stop offset="1" stop-color="#ff9a3c"/></linearGradient>'
    '<linearGradient id="ff" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff"/><stop offset="1" stop-color="#e9e4ff"/></linearGradient>'
    '<filter id="s" x="-20%" y="-20%" width="140%" height="150%"><feDropShadow dx="0" dy="14" stdDeviation="18" flood-opacity=".3"/></filter>'
    '</defs><rect x="100" y="100" width="824" height="824" rx="186" fill="url(#bg)" filter="url(#s)"/>'
    '<g transform="translate(152 172) scale(1.406)" filter="url(#s)">'
    f'<path d="{SHAPES["round"][0]}" fill="#d9ceff"/><path d="{SHAPES["round"][1]}" fill="url(#ff)"/>'
    '<g transform="translate(256 308)" fill="#7a3df0">'
    '<path d="M0-78C8-26 26-8 78 0C26 8 8 26 0 78C-8 26-26 8-78 0C-26-8-8-26 0-78Z"/>'
    '<path fill="#e0409a" d="M92-70C96-48 104-40 126-36C104-32 96-24 92-2C88-24 80-32 58-36C80-40 88-48 92-70Z"/>'
    '<path fill="#ff9a3c" d="M-96 30C-93 46-88 51-72 54C-88 57-93 62-96 78C-99 62-104 57-120 54C-104 51-99 46-96 30Z"/>'
    '</g></g></svg>'
)


def app_icon():
    dest = os.path.join(ROOT, "App", "Resources", "Assets.xcassets", "AppIcon.appiconset")
    os.makedirs(dest, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        svg, png, jf = (os.path.join(tmp, n) for n in ("icon.svg", "icon.png", "jobs.json"))
        with open(svg, "w") as f:
            f.write(APP_ICON)
        with open(jf, "w") as f:
            json.dump([{"svg": svg, "png": png, "size": 1024}], f)
        subprocess.run(["node", os.path.join(os.path.dirname(__file__), "render.js"), jf], check=True)
        master = Image.open(png).convert("RGBA")
    images = []
    for points in (16, 32, 128, 256, 512):
        for scale in (1, 2):
            px = points * scale
            name = f"icon_{px}.png"
            master.resize((px, px), Image.LANCZOS).save(os.path.join(dest, name), optimize=True)
            images.append({"idiom": "mac", "size": f"{points}x{points}", "scale": f"{scale}x", "filename": name})
    with open(os.path.join(dest, "Contents.json"), "w") as f:
        json.dump({"images": images, "info": {"author": "xcode", "version": 1}}, f, indent=2)
    with open(os.path.join(os.path.dirname(dest), "Contents.json"), "w") as f:
        json.dump({"info": {"author": "xcode", "version": 1}}, f, indent=2)
    os.makedirs(os.path.join(ROOT, "site", "assets"), exist_ok=True)
    master.resize((512, 512), Image.LANCZOS).save(os.path.join(ROOT, "site", "assets", "app-icon.png"), optimize=True)
    print("built app icon")


def main():
    if sys.argv[1:] == ["appicon"]:
        return app_icon()
    wanted = set(sys.argv[1:])
    themes = [t for t in THEMES if not wanted or t["id"] in wanted]
    jobs = []
    with tempfile.TemporaryDirectory() as tmp:
        for t in themes:
            os.makedirs(os.path.join(OUT, t["id"]), exist_ok=True)
            for c in CATEGORIES:
                svg = os.path.join(tmp, f'{t["id"]}__{c}.svg')
                with open(svg, "w") as f:
                    f.write(t["build"](c))
                jobs.append({"svg": svg, "png": os.path.join(OUT, t["id"], f"{c}.png"), "size": SIZE})
        jf = os.path.join(tmp, "jobs.json")
        with open(jf, "w") as f:
            json.dump(jobs, f)
        subprocess.run(["node", os.path.join(os.path.dirname(__file__), "render.js"), jf], check=True)

    for t in themes:
        d = os.path.join(OUT, t["id"])
        for c in CATEGORIES:
            p = os.path.join(d, f"{c}.png")
            img = Image.open(p).convert("RGBA")
            if t.get("pixel"):
                img = pixelate(img, t["pixel"])
            img.save(p, optimize=True)
        meta = {k: t[k] for k in ("id", "name", "group", "description", "accent")}
        meta.update(background=t["bg"], version=1, author="HyperIcon", categories=CATEGORIES)
        with open(os.path.join(d, "theme.json"), "w") as f:
            json.dump(meta, f, indent=2)
            f.write("\n")
        contact_sheet(t, ["folder", "git", "documents", "images", "music", "code"], 3, 128, os.path.join(d, "preview.png"))
        print("built", t["id"])

    with open(os.path.join(OUT, "categories.json"), "w") as f:
        json.dump([{"id": c, "label": LABELS[c]} for c in CATEGORIES], f, indent=2)
        f.write("\n")


if __name__ == "__main__":
    main()
