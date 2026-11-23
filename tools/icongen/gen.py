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


def dots(points, fill="#fff"):
    return "".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" opacity="{o}"/>' for x, y, r, o in points)


# ---------------------------------------------------------------- themes
# Each theme builds its own folder: the silhouette, what it is made of, and how symbols sit on it.

ROUND, SHARP, CHAMFER = SHAPES["round"], SHAPES["sharp"], SHAPES["chamfer"]


def halloween(cat):
    """A jack-o'-lantern: ribbed pumpkin, stem and vine on the tab, symbols carved and lit from inside."""
    back = "M40 170Q40 118 92 118H190Q212 118 224 132L240 150H420Q472 150 472 202V384Q472 432 424 432H88Q40 432 40 384Z"
    front = "M40 236Q40 178 98 178H414Q472 178 472 236V378Q472 436 414 436H98Q40 436 40 378Z"
    ribs = "".join(f'<ellipse cx="256" cy="307" rx="{rx}" ry="150" fill="none" stroke="#c9560a" stroke-width="5" opacity=".75"/>'
                   for rx in (58, 128, 196))
    shine = '<ellipse cx="150" cy="232" rx="60" ry="22" fill="#ffd08a" opacity=".35" transform="rotate(-18 150 232)"/>'
    stem = ('<path d="M96 126q-10-44 26-58l18 16q-18 12-10 42z" fill="#5d7a2a"/>'
            '<path d="M108 116q-4-26 14-38" fill="none" stroke="#3f5a1a" stroke-width="4" stroke-linecap="round"/>'
            '<path d="M134 104c28-34 70 4 46 26c-16 14-34-6-18-18" fill="none" stroke="#5d7a2a" stroke-width="6" stroke-linecap="round"/>'
            '<path d="M178 86c14-18 40-8 34 12c-14-2-26-4-34-12z" fill="#6f9433"/>')
    grin = ('<path d="M112 380 144 400 172 380 200 400 228 380 256 400 284 380 312 400 340 380 368 400 400 380Q256 452 112 380Z" '
            'fill="url(#lit)" stroke="#6b2a00" stroke-width="7" stroke-linejoin="round"/>')
    face = ""
    if cat == "folder":
        face = ('<g fill="url(#lit)" stroke="#6b2a00" stroke-width="7" stroke-linejoin="round">'
                '<path d="M150 300 196 228 232 300Z"/><path d="M280 300 316 228 362 300Z"/><path d="M256 312 276 348H236Z"/></g>')
    return compose(
        cat, shape=(back, front), back='fill="#b5480a"', front='fill="url(#f)"',
        defs=lin("f", [(0, "#ff9a2b"), (1, "#e2630c")])
        + '<radialGradient id="lit" cx=".5" cy=".6" r=".7"><stop offset="0" stop-color="#fff6b0"/><stop offset="1" stop-color="#ffb21a"/></radialGradient>',
        over=ribs + shine, mid=grin + face, top=stem, glyph="url(#lit)", gfilter="carve", gcenter=(256, 286), gsize=140)


def winter(cat):
    """A wrapped gift: ribbon and bow, snow on the lid, symbols printed on a gift tag."""
    paper = "".join(f'<circle cx="{x}" cy="{y}" r="5" fill="#fff" opacity=".22"/>'
                    for y in range(200, 440, 34) for x in range(58 + (y // 34 % 2) * 20, 472, 40))
    ribbon = ('<rect x="88" y="178" width="46" height="258" fill="#f2c94c"/>'
              '<rect x="88" y="178" width="8" height="258" fill="#fbe38d"/><rect x="126" y="178" width="8" height="258" fill="#c99a1e"/>')
    bow = ('<g transform="translate(111 150)"><path d="M0 0C-26-44-78-46-72-8C-68 22-22 14 0 0Z" fill="#f2c94c"/>'
           '<path d="M0 0C26-44 78-46 72-8C68 22 22 14 0 0Z" fill="#e5b62f"/>'
           '<path d="M-6 6-34 62-14 54-4 74 6 14Z" fill="#e5b62f"/><path d="M6 6 40 56 20 54 14 74-2 14Z" fill="#f2c94c"/>'
           '<circle r="15" fill="#fbe38d" stroke="#c99a1e" stroke-width="3"/></g>')
    tag = ""
    if GLYPHS[cat]:
        tag = ('<path d="M140 168C170 196 176 214 196 236" fill="none" stroke="#f6efe0" stroke-width="3"/>'
               '<g filter="url(#gshadow)"><path d="M214 216H418Q434 216 434 232V396Q434 412 418 412H214Q198 412 198 396V264L190 240Q196 216 214 216Z" fill="#fff7e6"/></g>'
               '<circle cx="212" cy="238" r="8" fill="#b31d27"/>'
               '<rect x="212" y="226" width="208" height="176" rx="10" fill="none" stroke="#2f7d4f" stroke-width="3" stroke-dasharray="2 9" stroke-linecap="round"/>')
    return compose(
        cat, shape=ROUND, back='fill="#8a1620"', front='fill="url(#f)"',
        defs=lin("f", [(0, "#e2434b"), (1, "#b71f29")]),
        under='<path d="M58 124H198" stroke="#fff" stroke-width="16" stroke-linecap="round"/>',
        over=paper + ribbon + scallops([24, 32, 20, 34, 26, 18, 32, 22, 28, 20], y0=206), mid=tag, top=bow,
        glyph="#1f6b40", gfilter=None, gcenter=(320, 316), gsize=132)


def valentine(cat):
    """A love letter: envelope with a pointed flap and a heart wax seal, symbols stamped on the paper."""
    flap = ('<path d="M40 178H472L256 300Z" fill="#fff" opacity=".55"/>'
            '<path d="M40 206Q40 178 68 178H444Q472 178 472 206L256 304Z" fill="#ffd3df"/>'
            '<path d="M44 192 256 304 468 192" fill="none" stroke="#e39ab0" stroke-width="4" stroke-linejoin="round"/>'
            '<path d="M40 436 190 330M472 436 322 330" stroke="#efb4c5" stroke-width="3"/>')
    seal = (f'<g transform="translate(256 262)" filter="url(#gshadow)"><path d="{HEART}" transform="translate(-33 -34) scale(3.3)" fill="#c2183f"/>'
            f'<path d="{HEART}" transform="translate(-21 -22) scale(2.1)" fill="none" stroke="#e8627f" stroke-width="1.2"/></g>')
    letter = '<path d="M70 150H442V190H70Z" fill="#fffdf8"/><path d="M92 164H300M92 178H240" stroke="#f1b8c6" stroke-width="4" stroke-linecap="round"/>'
    return compose(
        cat, shape=ROUND, back='fill="#d9416f"', front='fill="url(#f)"',
        defs=lin("f", [(0, "#fff0f4"), (1, "#ffdbe5")]),
        under=letter, over=flap, mid=seal, glyph="#cf2857", gfilter=None, gcenter=(256, 370), gsize=118)


def harvest(cat):
    """A wooden crate: planks, corner posts and nails, a rope handle, symbols branded into the wood."""
    planks = ""
    for i, y in enumerate((178, 266, 354)):
        h = 82
        planks += f'<rect x="40" y="{y}" width="432" height="{h}" fill="{("#d39a58", "#c88d4c", "#d6a05f")[i]}"/>'
        planks += f'<rect x="40" y="{y + h}" width="432" height="6" fill="#6f4520"/>'
        planks += "".join(f'<path d="M{x} {y + 14 + (j * 23) % 50}q40 {8 if j % 2 else -8} 90 0" fill="none" stroke="#a8713a" stroke-width="3" opacity=".6"/>'
                          for j, x in enumerate((92, 214, 330)))
    posts = "".join(f'<rect x="{x}" y="178" width="40" height="258" fill="#b27a3d"/>'
                    + "".join(f'<circle cx="{x + 20}" cy="{y}" r="6" fill="#5b3a1c"/><circle cx="{x + 18}" cy="{y - 2}" r="2" fill="#e8c493"/>'
                              for y in (220, 308, 396)) for x in (40, 432))
    rope = ('<path d="M70 132C90 78 172 78 190 132" fill="none" stroke="#b8935a" stroke-width="14" stroke-linecap="round"/>'
            '<path d="M70 132C90 78 172 78 190 132" fill="none" stroke="#e6cf9c" stroke-width="14" stroke-linecap="butt" stroke-dasharray="7 9"/>')
    return compose(
        cat, shape=SHARP, back='fill="#9a6631" stroke="#5b3a1c" stroke-width="5"',
        front='fill="#c88d4c" stroke="#5b3a1c" stroke-width="5"',
        over=planks + posts, top=rope, glyph="#4a2409", gfilter="burn", gcenter=(256, 307), gsize=138)


def thanksgiving(cat):
    """A turkey's tail-feather fan behind the folder, with a pilgrim hat band and buckle holding the symbol."""
    colours = ["#8a4a1c", "#d9792b", "#b3261e", "#e8b23a", "#b3261e", "#d9792b", "#8a4a1c"]
    fan = ""
    for i, colour in enumerate(colours):
        angle = -51 + i * 17
        fan += (f'<g transform="rotate({angle} 256 262)"><path d="M256 262C206 200 212 84 256 18C300 84 306 200 256 262Z" fill="{colour}"/>'
                f'<path d="M256 18C232 54 222 84 220 108Q256 86 292 108C290 84 280 54 256 18Z" fill="#fff1cf"/>'
                f'<path d="M256 40V250" stroke="#4a2a12" stroke-width="3" opacity=".55"/></g>')
    band = ('<rect x="40" y="262" width="432" height="92" fill="#2b1d12"/>'
            '<rect x="40" y="262" width="432" height="6" fill="#4a3320"/><rect x="40" y="348" width="432" height="6" fill="#170e07"/>')
    buckle = ('<g filter="url(#gshadow)"><rect x="170" y="222" width="172" height="172" rx="18" fill="url(#gold)"/></g>'
              '<rect x="190" y="242" width="132" height="132" rx="8" fill="#2b1d12"/>'
              '<rect x="176" y="228" width="160" height="160" rx="14" fill="none" stroke="#fff3c4" stroke-width="2" opacity=".7"/>')
    return compose(
        cat, shape=ROUND, pre=f'<g filter="url(#fshadow)">{fan}</g>',
        back='fill="#5a3a1f"', front='fill="url(#f)"',
        defs=lin("f", [(0, "#8a5a32"), (1, "#6b4222")]) + lin("gold", [(0, "#f6d568"), (1, "#c8922a")], x2=1),
        over=band, mid=buckle, glyph="#f6d568", gfilter=None, gcenter=(256, 308), gsize=104)


def scifi(cat):
    """A hinged console panel: gunmetal plates, rivets, status lights and a holographic display."""
    rivets = "".join(f'<circle cx="{x}" cy="{y}" r="6" fill="#8c98a6"/><circle cx="{x - 1.5}" cy="{y - 1.5}" r="2.4" fill="#dfe6ee"/>'
                     for x, y in ((66, 204), (446, 204), (66, 410), (430, 410)))
    hinges = "".join(f'<rect x="{x}" y="166" width="62" height="22" rx="11" fill="#9aa6b4" stroke="#39424d" stroke-width="3"/>'
                     f'<path d="M{x + 20} 168V186M{x + 42} 168V186" stroke="#39424d" stroke-width="3"/>' for x in (96, 354))
    screen = ('<rect x="128" y="212" width="256" height="176" rx="10" fill="#06131d" stroke="#2a3540" stroke-width="6"/>'
              + "".join(f'<path d="M134 {y}H378" stroke="#45f0ff" stroke-width="1" opacity=".12"/>' for y in range(222, 386, 8))
              + '<path d="M140 240V224H156M372 360V376H356" fill="none" stroke="#45f0ff" stroke-width="2.5"/>')
    lights = "".join(f'<circle cx="{84}" cy="{y}" r="8" fill="{c}"/><circle cx="82" cy="{y - 2}" r="2.5" fill="#fff" opacity=".7"/>'
                     for y, c in ((262, "#3ddc84"), (296, "#ffc233"), (330, "#ff5a4d")))
    vents = "".join(f'<rect x="408" y="{y}" width="40" height="7" rx="3.5" fill="#333d48"/>' for y in (258, 276, 294, 312, 330))
    plate = '<path d="M40 300H110M402 300H472" stroke="#4a5562" stroke-width="2"/>'
    return compose(
        cat, shape=CHAMFER, back='fill="#56616e" stroke="#2a323b" stroke-width="4"',
        front='fill="url(#f)" stroke="#2a323b" stroke-width="4"',
        defs=lin("f", [(0, "#7c8896"), (1, "#56616e")]),
        over=plate + screen + lights + vents + rivets, top=hinges,
        glyph="#7df7ff", gfilter="glow", gcenter=(256, 300), gsize=124)


def synthwave(cat):
    """A cassette tape: striped label, two reels and corner screws, symbols printed on the label."""
    screws = "".join(f'<circle cx="{x}" cy="{y}" r="8" fill="#9a9aa6"/><path d="M{x - 5} {y}H{x + 5}M{x} {y - 5}V{y + 5}" stroke="#3a3a44" stroke-width="2.5"/>'
                     for x, y in ((62, 200), (450, 200), (62, 414), (450, 414)))
    label = ('<rect x="84" y="192" width="344" height="164" rx="12" fill="#fbf3e3"/>'
             '<rect x="84" y="192" width="344" height="8" fill="#ffcf4a"/><rect x="84" y="200" width="344" height="8" fill="#ff8a3d"/>'
             '<rect x="84" y="208" width="344" height="8" fill="#f0478c"/><rect x="84" y="216" width="344" height="8" fill="#8a3de0"/>'
             '<path d="M104 338H180M332 338H408" stroke="#c9bfa8" stroke-width="3" stroke-linecap="round"/>')
    reel = ('<circle r="20" fill="#f4f4f6"/><circle r="7" fill="#24242b"/>'
            + "".join(f'<rect x="-3" y="-18" width="6" height="9" fill="#24242b" transform="rotate({a})"/>' for a in range(0, 360, 60)))
    window = ('<rect x="160" y="366" width="192" height="54" rx="14" fill="#15151a" stroke="#5a5a66" stroke-width="3"/>'
              f'<g transform="translate(200 393)">{reel}</g><g transform="translate(312 393)">{reel}</g>'
              '<rect x="234" y="378" width="44" height="30" rx="4" fill="#3b2a22"/>')
    return compose(
        cat, shape=ROUND, back='fill="#1e1e25"', front='fill="url(#f)"',
        defs=lin("f", [(0, "#3b3b46"), (1, "#2a2a33")]),
        under='<path d="M60 134H204" stroke="#55555f" stroke-width="6" stroke-linecap="round"/>',
        over=label + window + screws, glyph="#2a2a33", gfilter=None, gcenter=(256, 286), gsize=106)


def neon(cat):
    """An arcade cabinet: lit marquee, screen, joystick and buttons, symbols drawn in neon on the screen."""
    marquee = ('<path d="M52 128 66 124H192L212 146H52Z" fill="#ffe36b"/>'
               f'<text x="126" y="143" {MONO} font-size="17" text-anchor="middle" fill="#b3261e" letter-spacing="3">ARCADE</text>')
    screen = ('<rect x="86" y="196" width="340" height="168" rx="16" fill="#3a3f58"/>'
              '<rect x="100" y="208" width="312" height="144" rx="22" fill="#05060c"/>'
              '<path d="M118 222Q256 206 394 222" fill="none" stroke="#fff" stroke-width="3" opacity=".12"/>')
    panel = ('<path d="M40 378H472V414L450 436H40Z" fill="#30354c"/><path d="M40 378H472" stroke="#565d80" stroke-width="4"/>'
             '<rect x="143" y="382" width="8" height="26" fill="#c9ccd6"/><circle cx="147" cy="380" r="14" fill="#e23b3b"/>'
             '<circle cx="143" cy="376" r="4" fill="#fff" opacity=".6"/><ellipse cx="147" cy="412" rx="20" ry="6" fill="#161927"/>'
             + "".join(f'<circle cx="{x}" cy="406" r="13" fill="#161927"/><circle cx="{x}" cy="403" r="11" fill="{c}"/>'
                       for x, c in ((292, "#ffd23f"), (334, "#3ddc84"), (376, "#4aa8ff"))))
    return compose(
        cat, shape=CHAMFER, back='fill="#1c2033" stroke="#0c0e18" stroke-width="4"',
        front='fill="#232842" stroke="#0c0e18" stroke-width="4"',
        under=marquee, over=screen + panel, glyph="#ff4fd8", gfilter="neon", gcenter=(256, 280), gsize=118)


def crt(cat):
    """A beige terminal: plastic bezel, curved green screen and a prompt, symbols in glowing phosphor."""
    screen = ('<rect x="70" y="198" width="372" height="192" rx="26" fill="#a9a08a"/>'
              '<rect x="82" y="208" width="348" height="172" rx="34" fill="#021a06"/>'
              '<rect x="82" y="208" width="348" height="172" rx="34" fill="url(#sl)"/>'
              '<path d="M104 226Q256 208 408 226" fill="none" stroke="#fff" stroke-width="3" opacity=".1"/>'
              f'<text x="104" y="366" {MONO} font-size="20" fill="#35ff6a" filter="url(#softglow)">&gt; _</text>')
    trim = ('<circle cx="424" cy="412" r="7" fill="#3ddc84"/><rect x="366" y="406" width="40" height="12" rx="3" fill="#b8ae97"/>'
            + "".join(f'<rect x="{x}" y="402" width="5" height="20" rx="2" fill="#a9a08a"/>' for x in range(74, 170, 12)))
    return compose(
        cat, shape=ROUND, back='fill="#bdb49d"', front='fill="url(#f)"',
        defs=lin("f", [(0, "#e4dcc8"), (1, "#cfc6af")])
        + '<pattern id="sl" width="6" height="6" patternUnits="userSpaceOnUse"><rect width="6" height="2" fill="#35ff6a" opacity=".1"/></pattern>',
        under='<path d="M60 132H204" stroke="#d8d0bb" stroke-width="5" stroke-linecap="round"/>',
        over=screen + trim, glyph="#35ff6a", gfilter="glow", gcenter=(256, 288), gsize=118)


def pixel(cat):
    """Chunky low-resolution pixel art."""
    return compose(
        cat, shape=SHARP, ffilter=None, gfilter=None,
        back='fill="#b8641a" stroke="#2b1600" stroke-width="16" stroke-linejoin="miter"',
        front='fill="#ffb52e" stroke="#2b1600" stroke-width="16" stroke-linejoin="miter"',
        over='<rect x="48" y="186" width="416" height="16" fill="#ffe08a"/>'
             '<rect x="48" y="412" width="416" height="16" fill="#d98a17"/>',
        glyph="#2b1600", gcenter=(256, 308), gsize=160)


def platinum(cat):
    """A bevelled late-90s desktop folder."""
    bevel = ('<path d="M47 428V185H466" fill="none" stroke="#fff" stroke-width="5"/>'
             '<path d="M465 188V429H50" fill="none" stroke="#7676b4" stroke-width="5"/>')
    return compose(
        cat, shape=SHARP, ffilter=None, gfilter=None,
        back='fill="#8d8dc4" stroke="#15152b" stroke-width="5"',
        front='fill="#bfbfee" stroke="#15152b" stroke-width="5"',
        under='<path d="M48 126H196" stroke="#c9c9f2" stroke-width="5"/>',
        over=bevel, glyph="#24244f", gcenter=(256, 308), gsize=148)


def nineties(cat):
    """A manila folder with black outlines and a hard shadow."""
    bevel = ('<path d="M47 428V185H466" fill="none" stroke="#fff6c2" stroke-width="6"/>'
             '<path d="M465 188V429H50" fill="none" stroke="#b78a00" stroke-width="6"/>')
    shadow = '<g transform="translate(14 14)" opacity=".32"><path d="{BACK}"/><path d="{FRONT}"/></g>'
    return compose(
        cat, shape=SHARP, ffilter=None, gfilter=None, pre=shadow,
        back='fill="#c99700" stroke="#000" stroke-width="5"',
        front='fill="#ffd633" stroke="#000" stroke-width="5"',
        over=bevel, glyph="#00007a", gcenter=(256, 308), gsize=148)


def aqua(cat):
    """A glossy, pinstriped early-2000s folder with gel symbols."""
    over = ('<rect x="40" y="178" width="432" height="258" fill="url(#ps)"/>'
            '<ellipse cx="256" cy="186" rx="270" ry="76" fill="#fff" opacity=".42"/>'
            '<ellipse cx="256" cy="452" rx="220" ry="44" fill="#bfe6ff" opacity=".35"/>')
    return compose(
        cat, shape=ROUND, back='fill="url(#b)"', front='fill="url(#f)" stroke="#0d4aa3" stroke-width="2"',
        defs=lin("b", [(0, "#3d93ee"), (1, "#1557b8")]) + lin("f", [(0, "#8fd2ff"), (1, "#2380e8")])
        + '<pattern id="ps" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="1.4" fill="#fff" opacity=".16"/></pattern>',
        over=over, glyph="#fff", gfilter="emboss", gcenter=(256, 314), gsize=146)


THEMES = [
    dict(id="winter-holiday", name="Winter Holiday", group="Holidays", build=winter,
         description="Folders wrapped as gifts, with ribbon, a bow and a tag."),
    dict(id="halloween", name="Halloween", group="Holidays", build=halloween,
         description="Jack-o'-lantern folders with carved, candle-lit symbols."),
    dict(id="thanksgiving", name="Thanksgiving", group="Holidays", build=thanksgiving,
         description="A turkey's feather fan and a pilgrim buckle on every folder."),
    dict(id="valentine", name="Valentine", group="Holidays", build=valentine,
         description="Love-letter envelopes sealed with a wax heart."),
    dict(id="harvest", name="Harvest", group="Holidays", build=harvest,
         description="Wooden market crates with rope handles and branded symbols."),
    dict(id="scifi-hud", name="Sci-Fi HUD", group="Sci-Fi", build=scifi,
         description="Riveted console panels with holographic displays."),
    dict(id="synthwave-84", name="Synthwave '84", group="80s", build=synthwave,
         description="Cassette tapes with striped labels and spinning reels."),
    dict(id="neon-arcade", name="Neon Arcade", group="80s", build=neon,
         description="Arcade cabinets with a joystick, buttons and a neon screen."),
    dict(id="green-phosphor", name="Green Phosphor CRT", group="Computer Retro", build=crt,
         description="Beige terminals with a glowing green screen."),
    dict(id="8-bit-pixel", name="8-Bit Pixel", group="Computer Retro", build=pixel,
         description="Chunky low-resolution pixel art.", pixel=64),
    dict(id="platinum-classic", name="Platinum Classic", group="OS Classics", build=platinum,
         description="Bevelled folders in the style of late-90s desktops."),
    dict(id="nineties-desktop", name="Nineties Desktop", group="OS Classics", build=nineties,
         description="Manila folders with black outlines and hard shadows."),
    dict(id="aqua-gloss", name="Aqua Gloss", group="OS Classics", build=aqua,
         description="Glossy pinstriped folders from the early 2000s."),
]

# One neutral backdrop for every preview, so colour never stands in for the theme.
PREVIEW_BG = "#30333d"


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
    sheet = Image.new("RGBA", (cols * cell + pad * 2, rows * cell + pad * 2), ImageColor.getrgb(PREVIEW_BG) + (255,))
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
        meta = {k: t[k] for k in ("id", "name", "group", "description")}
        meta.update(version=2, author="HyperIcon", categories=CATEGORIES)
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
