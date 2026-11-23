#!/usr/bin/env python3
"""HyperIcon icon generator.

Themes carry no folder and no colour. For each theme x category this renders a transparent 512 px
artwork layer (a themed object carrying the content symbol) that the app draws on top of a plain
folder in the colour of the folder's Finder tag. The plain folders, one per tag colour, are rendered
to Themes/_base/. Rendering uses headless Chromium (tools/icongen/render.js).

Usage: python3 tools/icongen/gen.py [theme-id ...]     (base folders are always rebuilt)
       python3 tools/icongen/gen.py appicon
"""
import json
import os
import subprocess
import sys
import tempfile

from PIL import Image, ImageColor

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
    # carve: a cut-out with a dark rind around it and light spilling out.
    + '<filter id="carve" x="-30%" y="-30%" width="160%" height="160%">'
    '<feMorphology in="SourceAlpha" operator="dilate" radius="4" result="d"/>'
    '<feFlood flood-color="#6b2a00"/><feComposite in2="d" operator="in" result="rind"/>'
    '<feGaussianBlur in="SourceGraphic" stdDeviation="9" result="b"/>'
    '<feMerge><feMergeNode in="b"/><feMergeNode in="rind"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
    # burn: branded into wood, with a scorched soft edge.
    '<filter id="burn" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="3.5" result="b"/>'
    '<feComponentTransfer in="b" result="s"><feFuncA type="linear" slope=".55"/></feComponentTransfer>'
    '<feMerge><feMergeNode in="s"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
    # emboss: raised gel with a light edge above and a shadow below.
    '<filter id="emboss" x="-20%" y="-20%" width="140%" height="140%">'
    '<feDropShadow dx="0" dy="4" stdDeviation="3" flood-color="#0b3f8f" flood-opacity=".55"/></filter>'
)


def compose(cat, *, shape="round", back, front, defs="", under="", over="", top="", glyph="#fff",
            gfilter="gshadow", ffilter="fshadow", gcenter=(256, 310), gsize=150, pre="", mid=""):
    """Assembles one icon. Layers, back to front: pre, folder back, under, folder front, over (clipped to the
    front), mid, the symbol, top. `shape` is a SHAPES key or a (back path, front path) pair."""
    bd, fd = SHAPES[shape] if isinstance(shape, str) else shape
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
            f'<g clip-path="url(#fc)">{over}</g>{mid}{g}{top}</svg>')


HEART = "M0 6C0-2 10-2 10 4C10-2 20-2 20 6C20 13 12 17 10 22C8 17 0 13 0 6Z"
LEAF = "M0 0C14-22 44-22 58 0C44 22 14 22 0 0Z"

# ---------------------------------------------------------------- base folders
# Plain macOS-style folders, one per Finder tag colour. "blue" is also used for untagged folders.
# Keys match FolderColor raw values in Core/Sources/HyperIconCore/FolderColor.swift.

BASE_COLORS = {
    "blue": "#3f9cf0",
    "gray": "#9a9aa2",
    "green": "#3cc35c",
    "purple": "#b05ad8",
    "yellow": "#f5c624",
    "red": "#f0504a",
    "orange": "#ff9a2e",
}
BACK = SHAPES["round"][0]
FRONT = SHAPES["round"][1]


def _mix(hex_colour, other, t):
    a, b = ImageColor.getrgb(hex_colour), ImageColor.getrgb(other)
    return "#%02x%02x%02x" % tuple(round(x + (y - x) * t) for x, y in zip(a, b))


def base_folder(colour):
    c = BASE_COLORS[colour]
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{SIZE}" height="{SIZE}" viewBox="0 0 {SIZE} {SIZE}"><defs>{FILTERS}'
            + lin("f", [(0, _mix(c, "#ffffff", .32)), (1, _mix(c, "#ffffff", .06))])
            + lin("b", [(0, _mix(c, "#000000", .05)), (1, _mix(c, "#000000", .22))])
            + f'</defs><g filter="url(#fshadow)"><path d="{BACK}" fill="url(#b)"/>'
            f'<path d="{FRONT}" fill="url(#f)"/></g>'
            f'<path d="M40 210Q40 180 68 180H444Q472 180 472 210" fill="none" stroke="#fff" stroke-opacity=".5" stroke-width="3"/>'
            '</svg>')


# ---------------------------------------------------------------- artwork
# Each theme draws one object from its world, centred on the folder's front, carrying the symbol.
# No folder and no background: everything outside the object stays transparent.

CX, CY = 256, 312          # centre of the folder front


def art(cat, obj, *, glyph, gcenter=(CX, CY), gsize=96, gfilter=None, defs="", top="", shadow=True):
    gx, gy = gcenter[0] - gsize / 2, gcenter[1] - gsize / 2
    gf = f' filter="url(#{gfilter})"' if gfilter else ""
    g = ""
    if GLYPHS[cat]:
        g = (f'<mask id="gm" maskUnits="userSpaceOnUse" x="0" y="0" width="{SIZE}" height="{SIZE}">'
             f'<g transform="translate({gx} {gy}) scale({gsize / 100})">{GLYPHS[cat]}</g></mask>'
             f'<g{gf}><rect width="{SIZE}" height="{SIZE}" fill="{glyph}" mask="url(#gm)"/></g>')
    sh = ' filter="url(#oshadow)"' if shadow else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{SIZE}" height="{SIZE}" viewBox="0 0 {SIZE} {SIZE}">'
            f'<defs>{FILTERS}<filter id="oshadow" x="-20%" y="-20%" width="140%" height="150%">'
            '<feDropShadow dx="0" dy="6" stdDeviation="6" flood-color="#000" flood-opacity=".35"/></filter>'
            f'{defs}</defs><g{sh}>{obj}</g>{g}{top}</svg>')


def halloween(cat):
    """A jack-o'-lantern with the symbol carved out and lit from inside."""
    body = ('<path d="M256 226C204 214 140 230 136 300C132 372 196 404 256 400C316 404 380 372 376 300C372 230 308 214 256 226Z" fill="url(#pk)"/>'
            '<path d="M256 228C222 234 206 290 212 340C216 376 236 398 256 400C276 398 296 376 300 340C306 290 290 234 256 228Z" fill="none" stroke="#c4530a" stroke-width="5"/>'
            '<path d="M200 232C166 252 154 300 162 344M312 232C346 252 358 300 350 344" fill="none" stroke="#c4530a" stroke-width="5"/>'
            '<ellipse cx="196" cy="262" rx="26" ry="11" fill="#ffd9a0" opacity=".45" transform="rotate(-25 196 262)"/>'
            '<path d="M248 230C244 212 246 196 256 186L270 190C262 200 262 214 266 228Z" fill="#5f7d2b"/>'
            '<path d="M268 196C292 176 322 192 312 210C302 222 288 210 294 202" fill="none" stroke="#5f7d2b" stroke-width="5" stroke-linecap="round"/>')
    face = ""
    if cat == "folder":
        face = ('<g fill="url(#lit)" stroke="#6b2a00" stroke-width="5" stroke-linejoin="round">'
                '<path d="M196 300 220 262 244 300Z"/><path d="M268 300 292 262 316 300Z"/>'
                '<path d="M196 336 214 348 232 336 250 350 268 336 286 350 304 336 318 344Q256 392 196 336Z"/></g>')
    return art(cat, body + face, glyph="url(#lit)", gfilter="carve", gcenter=(256, 318), gsize=92,
               defs=lin("pk", [(0, "#ffa23a"), (1, "#e35f0d")])
               + '<radialGradient id="lit" cx=".5" cy=".6" r=".7"><stop offset="0" stop-color="#fff6b0"/><stop offset="1" stop-color="#ffb21a"/></radialGradient>')


def winter(cat):
    """A gift tag tied with string and a sprig of holly; the symbol is printed on the tag."""
    tag = ('<g transform="rotate(-8 256 316)">'
           '<path d="M174 232H360Q376 232 376 248V392Q376 408 360 408H174Q158 408 158 392V284L140 266V256Q150 232 174 232Z" fill="#fff8ea"/>'
           '<circle cx="164" cy="262" r="8" fill="#c9bea6"/><circle cx="164" cy="262" r="4.5" fill="#e9e0cc"/>'
           '<rect x="174" y="246" width="190" height="150" rx="8" fill="none" stroke="#c0392b" stroke-width="3" stroke-dasharray="1 8" stroke-linecap="round"/></g>')
    string = '<path d="M162 258C128 236 118 206 136 184" fill="none" stroke="#b3261e" stroke-width="4" stroke-linecap="round"/>'
    holly = ('<g transform="translate(330 226) rotate(20)">'
             f'<path d="{LEAF}" transform="translate(-58 0) scale(.9)" fill="#1f7a45"/><path d="{LEAF}" transform="rotate(-50) scale(.9)" fill="#2a8f53"/>'
             '<circle cx="-4" cy="4" r="9" fill="#d62b2b"/><circle cx="10" cy="-6" r="9" fill="#e23b3b"/><circle cx="12" cy="12" r="8" fill="#c21f1f"/></g>')
    return art(cat, tag + string, glyph="#1f6b40", gcenter=(268, 322), gsize=100, top=holly)


def thanksgiving(cat):
    """A turkey's feather fan behind a pilgrim buckle; the symbol sits in the buckle."""
    colours = ["#8a4a1c", "#d9792b", "#b3261e", "#e8b23a", "#b3261e", "#d9792b", "#8a4a1c"]
    fan = ""
    for i, colour in enumerate(colours):
        angle = -60 + i * 20
        fan += (f'<g transform="rotate({angle} 256 340)"><path d="M256 340C224 300 228 228 256 196C284 228 288 300 256 340Z" fill="{colour}"/>'
                f'<path d="M256 196C242 216 236 232 236 244Q256 232 276 244C276 232 270 216 256 196Z" fill="#fff1cf"/></g>')
    buckle = ('<rect x="186" y="262" width="140" height="132" rx="14" fill="url(#gold)"/>'
              '<rect x="204" y="280" width="104" height="96" rx="6" fill="#2b1d12"/>'
              '<rect x="192" y="268" width="128" height="120" rx="11" fill="none" stroke="#fff3c4" stroke-width="2" opacity=".7"/>')
    return art(cat, fan + buckle, glyph="#f6d568", gcenter=(256, 328), gsize=74,
               defs=lin("gold", [(0, "#f6d568"), (1, "#c8922a")], x2=1))


def valentine(cat):
    """A love letter closed with a large wax heart; the symbol is pressed into the wax."""
    env = ('<rect x="146" y="238" width="220" height="150" rx="10" fill="#fff4f7"/>'
           '<path d="M150 244 256 320 362 244" fill="none" stroke="#e7a7b9" stroke-width="4" stroke-linejoin="round"/>'
           '<path d="M150 384 226 318M362 384 286 318" stroke="#f0c2cf" stroke-width="3"/>')
    seal = (f'<path d="{HEART}" transform="translate(176 232) scale(8)" fill="url(#wax)"/>'
            f'<path d="{HEART}" transform="translate(190 246) scale(6.6)" fill="none" stroke="#f17d97" stroke-width=".35"/>')
    return art(cat, env + seal, glyph="#ffe4ea", gcenter=(256, 318), gsize=76,
               defs=lin("wax", [(0, "#e0365d"), (1, "#a8102f")]))


def harvest(cat):
    """A small wooden crate panel with the symbol branded into the planks."""
    crate = ""
    for i, y in enumerate((232, 288, 344)):
        crate += f'<rect x="150" y="{y}" width="212" height="54" fill="{("#d6a05f", "#cc9352", "#d39a58")[i]}"/>'
        crate += f'<path d="M{170 + i * 22} {y + 18}q46 8 96 0M{226 - i * 14} {y + 38}q40 -6 84 0" fill="none" stroke="#a8713a" stroke-width="2.5" opacity=".6"/>'
        crate += f'<rect x="150" y="{y + 52}" width="212" height="4" fill="#6f4520"/>'
    crate += "".join(f'<rect x="{x}" y="228" width="26" height="176" fill="#b27a3d" stroke="#6f4520" stroke-width="2"/>'
                     + "".join(f'<circle cx="{x + 13}" cy="{y}" r="4" fill="#5b3a1c"/>' for y in (248, 316, 384)) for x in (140, 346))
    wheat = ('<g transform="translate(340 222) rotate(25)" fill="#e2b54c">'
             + "".join(f'<ellipse cx="{dx}" cy="{-i * 11}" rx="5" ry="9" transform="rotate({dx * 3} {dx} {-i * 11})"/>' for i in range(5) for dx in (-6, 6))
             + '<path d="M0 0V40" stroke="#b9892a" stroke-width="3"/></g>')
    return art(cat, crate, glyph="#4a2409", gfilter="burn", gcenter=(256, 318), gsize=96, top=wheat)


def scifi(cat):
    """A riveted console screen with the symbol as a hologram."""
    panel = ('<path d="M150 236 166 220H346L362 236V392L346 408H166L150 392Z" fill="url(#gm2)" stroke="#2a323b" stroke-width="3"/>'
             '<rect x="170" y="240" width="172" height="142" rx="8" fill="#06131d" stroke="#2a3540" stroke-width="4"/>'
             + "".join(f'<path d="M174 {y}H338" stroke="#45f0ff" stroke-width="1" opacity=".14"/>' for y in range(248, 380, 7))
             + "".join(f'<circle cx="{x}" cy="{y}" r="4" fill="#c6cfd8"/>' for x, y in ((160, 232), (352, 232), (160, 396), (352, 396)))
             + '<rect x="190" y="390" width="40" height="6" rx="3" fill="#3ddc84"/><rect x="236" y="390" width="20" height="6" rx="3" fill="#ffc233"/>')
    return art(cat, panel, glyph="#7df7ff", gfilter="glow", gcenter=(256, 311), gsize=96,
               defs=lin("gm2", [(0, "#8794a2"), (1, "#56616e")]))


def synthwave(cat):
    """A cassette tape; the symbol is printed on its striped label."""
    reel = ('<circle r="13" fill="#f4f4f6"/><circle r="5" fill="#24242b"/>'
            + "".join(f'<rect x="-2" y="-12" width="4" height="6" fill="#24242b" transform="rotate({a})"/>' for a in range(0, 360, 60)))
    tape = ('<rect x="128" y="236" width="256" height="166" rx="14" fill="#2c2c35"/>'
            '<rect x="144" y="248" width="224" height="104" rx="8" fill="#fbf3e3"/>'
            + "".join(f'<rect x="144" y="{248 + i * 6}" width="224" height="6" fill="{c}"/>' for i, c in enumerate(("#ffcf4a", "#ff8a3d", "#f0478c", "#8a3de0")))
            + '<path d="M184 362H328L340 402H172Z" fill="#3a3a44"/>'
            '<rect x="200" y="366" width="112" height="26" rx="13" fill="#15151a"/>'
            f'<g transform="translate(222 379)">{reel}</g><g transform="translate(290 379)">{reel}</g>'
            + "".join(f'<circle cx="{x}" cy="{y}" r="4" fill="#8c8c98"/>' for x, y in ((140, 248), (372, 248), (140, 390), (372, 390))))
    return art(cat, tape, glyph="#2a2a33", gcenter=(256, 306), gsize=66)


def neon(cat):
    """An arcade cabinet front: a lit marquee over a dark screen with the symbol in neon."""
    cab = ('<path d="M164 222H348L340 404H172Z" fill="#232842"/>'
           '<rect x="164" y="222" width="184" height="26" rx="4" fill="#ffe36b"/>'
           f'<text x="256" y="241" {MONO} font-size="15" text-anchor="middle" fill="#b3261e" letter-spacing="3">ARCADE</text>'
           '<rect x="180" y="256" width="152" height="118" rx="14" fill="#05060c" stroke="#3a3f58" stroke-width="6"/>'
           '<circle cx="204" cy="390" r="7" fill="#e23b3b"/><circle cx="292" cy="390" r="6" fill="#ffd23f"/><circle cx="312" cy="390" r="6" fill="#3ddc84"/>')
    return art(cat, cab, glyph="#ff4fd8", gfilter="neon", gcenter=(256, 315), gsize=88)


def crt(cat):
    """A small beige terminal with the symbol glowing on its green screen."""
    term = ('<rect x="150" y="224" width="212" height="166" rx="18" fill="url(#bz)"/>'
            '<rect x="166" y="238" width="180" height="128" rx="22" fill="#021a06"/>'
            '<rect x="166" y="238" width="180" height="128" rx="22" fill="url(#sl)"/>'
            '<path d="M190 380H322L334 404H178Z" fill="#c9c0aa"/>'
            '<circle cx="340" cy="378" r="4" fill="#3ddc84"/>')
    return art(cat, term, glyph="#35ff6a", gfilter="glow", gcenter=(256, 302), gsize=84,
               defs=lin("bz", [(0, "#e8e0cc"), (1, "#c9c0aa")])
               + '<pattern id="sl" width="5" height="5" patternUnits="userSpaceOnUse"><rect width="5" height="2" fill="#35ff6a" opacity=".1"/></pattern>')


def pixel(cat):
    """A chunky pixel-art badge."""
    badge = ('<rect x="164" y="226" width="184" height="172" fill="#ffb52e" stroke="#2b1600" stroke-width="14"/>'
             '<rect x="171" y="233" width="170" height="12" fill="#ffe08a"/><rect x="171" y="379" width="170" height="12" fill="#d98a17"/>')
    return art(cat, badge, glyph="#2b1600", gcenter=(256, 312), gsize=110, shadow=False)


def platinum(cat):
    """A bevelled grey plate, late-90s desktop style."""
    plate = ('<rect x="160" y="232" width="192" height="164" fill="#dcdcdc" stroke="#15152b" stroke-width="4"/>'
             '<path d="M164 392V236H348" fill="none" stroke="#fff" stroke-width="5"/>'
             '<path d="M348 238V392H166" fill="none" stroke="#8e8e9e" stroke-width="5"/>')
    return art(cat, plate, glyph="#24244f", gcenter=(256, 314), gsize=104, shadow=False)


def nineties(cat):
    """A little window with a title bar and a hard drop shadow."""
    win = ('<rect x="172" y="240" width="190" height="164" fill="#000" opacity=".35"/>'
           '<rect x="158" y="226" width="190" height="164" fill="#c0c0c0" stroke="#000" stroke-width="3"/>'
           '<rect x="164" y="232" width="178" height="22" fill="#00007a"/>'
           '<rect x="326" y="236" width="12" height="14" fill="#c0c0c0" stroke="#000" stroke-width="1.5"/>'
           '<rect x="164" y="258" width="178" height="126" fill="#fff" stroke="#808080" stroke-width="2"/>')
    return art(cat, win, glyph="#000", gcenter=(253, 321), gsize=92, shadow=False)


def aqua(cat):
    """A glossy white gel lozenge with a blue symbol."""
    gel = ('<rect x="160" y="236" width="192" height="156" rx="40" fill="url(#gel)" stroke="#9ab8d8" stroke-width="2"/>'
           '<rect x="174" y="242" width="164" height="56" rx="28" fill="#fff" opacity=".75"/>'
           '<rect x="160" y="236" width="192" height="156" rx="40" fill="url(#ps)"/>')
    return art(cat, gel, glyph="#1f6fd1", gfilter="emboss", gcenter=(256, 318), gsize=96,
               defs=lin("gel", [(0, "#ffffff"), (1, "#cfe2f6")])
               + '<pattern id="ps" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="1.3" fill="#7aa9d8" opacity=".14"/></pattern>')


THEMES = [
    dict(id="winter-holiday", name="Winter Holiday", group="Holidays", build=winter,
         description="A gift tag with holly on every folder."),
    dict(id="halloween", name="Halloween", group="Holidays", build=halloween,
         description="Jack-o'-lanterns with the symbol carved and candle-lit."),
    dict(id="thanksgiving", name="Thanksgiving", group="Holidays", build=thanksgiving,
         description="A turkey's feather fan behind a pilgrim buckle."),
    dict(id="valentine", name="Valentine", group="Holidays", build=valentine,
         description="Love letters sealed with a wax heart."),
    dict(id="harvest", name="Harvest", group="Holidays", build=harvest,
         description="Wooden crates with branded symbols and a sheaf of wheat."),
    dict(id="scifi-hud", name="Sci-Fi HUD", group="Sci-Fi", build=scifi,
         description="Riveted console screens with holographic symbols."),
    dict(id="synthwave-84", name="Synthwave '84", group="80s", build=synthwave,
         description="Cassette tapes with striped labels."),
    dict(id="neon-arcade", name="Neon Arcade", group="80s", build=neon,
         description="Arcade cabinets with neon symbols on the screen."),
    dict(id="green-phosphor", name="Green Phosphor CRT", group="Computer Retro", build=crt,
         description="Beige terminals with a glowing green screen."),
    dict(id="8-bit-pixel", name="8-Bit Pixel", group="Computer Retro", build=pixel,
         description="Chunky low-resolution pixel badges.", pixel=64),
    dict(id="platinum-classic", name="Platinum Classic", group="OS Classics", build=platinum,
         description="Bevelled grey plates in the style of late-90s desktops."),
    dict(id="nineties-desktop", name="Nineties Desktop", group="OS Classics", build=nineties,
         description="Little windows with title bars and hard shadows."),
    dict(id="aqua-gloss", name="Aqua Gloss", group="OS Classics", build=aqua,
         description="Glossy pinstriped gel badges from the early 2000s."),
]

PREVIEW_BG = "#30333d"


def pixelate(img, grid):
    small = img.resize((grid, grid), Image.BOX)
    r, g, b, a = small.split()
    a = a.point(lambda v: 255 if v >= 110 else 0)
    rgb = Image.merge("RGB", (r, g, b)).quantize(colors=12, method=Image.MEDIANCUT).convert("RGB")
    small = Image.merge("RGBA", (*rgb.split(), a))
    return small.resize(img.size, Image.NEAREST)


def composite(theme_id, cat, colour="blue"):
    """What the app draws: the base folder in a tag colour with the theme's artwork on top."""
    img = Image.open(os.path.join(OUT, "_base", f"{colour}.png")).convert("RGBA")
    img.alpha_composite(Image.open(os.path.join(OUT, theme_id, f"{cat}.png")).convert("RGBA"))
    return img


def contact_sheet(theme, cats, cols, cell, path, colours=None):
    rows = (len(cats) + cols - 1) // cols
    pad = cell // 8
    sheet = Image.new("RGBA", (cols * cell + pad * 2, rows * cell + pad * 2), ImageColor.getrgb(PREVIEW_BG) + (255,))
    for i, c in enumerate(cats):
        colour = colours[i % len(colours)] if colours else "blue"
        icon = composite(theme["id"], c, colour).resize((cell, cell), Image.LANCZOS)
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


def render(jobs):
    with tempfile.TemporaryDirectory() as tmp:
        for i, job in enumerate(jobs):
            svg = os.path.join(tmp, f"{i}.svg")
            with open(svg, "w") as f:
                f.write(job.pop("svgtext"))
            job["svg"] = svg
        jf = os.path.join(tmp, "jobs.json")
        with open(jf, "w") as f:
            json.dump(jobs, f)
        subprocess.run(["node", os.path.join(os.path.dirname(__file__), "render.js"), jf], check=True)


def main():
    if sys.argv[1:] == ["appicon"]:
        return app_icon()
    wanted = set(sys.argv[1:])
    themes = [t for t in THEMES if not wanted or t["id"] in wanted]

    os.makedirs(os.path.join(OUT, "_base"), exist_ok=True)
    jobs = [{"svgtext": base_folder(c), "png": os.path.join(OUT, "_base", f"{c}.png"), "size": SIZE} for c in BASE_COLORS]
    for t in themes:
        os.makedirs(os.path.join(OUT, t["id"]), exist_ok=True)
        jobs += [{"svgtext": t["build"](c), "png": os.path.join(OUT, t["id"], f"{c}.png"), "size": SIZE} for c in CATEGORIES]
    render(jobs)

    for t in themes:
        d = os.path.join(OUT, t["id"])
        for c in CATEGORIES:
            p = os.path.join(d, f"{c}.png")
            img = Image.open(p).convert("RGBA")
            if t.get("pixel"):
                img = pixelate(img, t["pixel"])
            img.save(p, optimize=True)
        meta = {k: t[k] for k in ("id", "name", "group", "description")}
        meta.update(version=3, format="artwork", author="HyperIcon", categories=CATEGORIES)
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
