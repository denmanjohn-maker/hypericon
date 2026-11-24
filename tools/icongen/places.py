"""Standalone artwork for places: favorite folders, the home folder and disks.

Unlike folder artwork, a place icon is the whole icon. There is no folder underneath and no tag colour.
Each theme draws hero objects from its world: something for the startup disk, external drives, network
shares and the home folder, plus a "carrier" object that holds a favorite folder's symbol.
All artwork is original; nothing is copied from an operating system or a vendor.
"""
import math

from glyphs import FAVORITES, GLYPHS, PLACE_GLYPHS

SIZE = 512
MONO = 'font-family="JetBrains Mono, DejaVu Sans Mono, monospace" font-weight="700"'
SANS = 'font-family="Inter, Helvetica, Arial, sans-serif" font-weight="900"'


def lin(id_, stops, x1=0, y1=0, x2=0, y2=1):
    s = "".join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in stops)
    return f'<linearGradient id="{id_}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}">{s}</linearGradient>'


def rad(id_, stops, cx=.5, cy=.5, r=.5, fx=None, fy=None):
    s = "".join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in stops)
    f = f' fx="{fx}" fy="{fy}"' if fx is not None else ""
    return f'<radialGradient id="{id_}" cx="{cx}" cy="{cy}" r="{r}"{f}>{s}</radialGradient>'


def glow(id_, std=6):
    return (f'<filter id="{id_}" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="{std}" result="b"/>'
            f'<feMerge><feMergeNode in="b"/><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>')


DEFS = (
    '<filter id="oshadow" x="-20%" y="-20%" width="140%" height="150%">'
    '<feDropShadow dx="0" dy="8" stdDeviation="8" flood-color="#000" flood-opacity=".35"/></filter>'
    '<filter id="gshadow" x="-20%" y="-20%" width="140%" height="140%">'
    '<feDropShadow dx="0" dy="3" stdDeviation="3" flood-color="#000" flood-opacity=".3"/></filter>'
    + glow("glow") + glow("softglow", 3) + glow("bigglow", 14)
    + '<filter id="carve" x="-30%" y="-30%" width="160%" height="160%">'
    '<feMorphology in="SourceAlpha" operator="dilate" radius="4" result="d"/>'
    '<feFlood flood-color="#2a1f33"/><feComposite in2="d" operator="in" result="rind"/>'
    '<feGaussianBlur in="SourceGraphic" stdDeviation="8" result="b"/>'
    '<feMerge><feMergeNode in="b"/><feMergeNode in="rind"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
    '<filter id="neon" x="-30%" y="-30%" width="160%" height="160%">'
    '<feMorphology in="SourceGraphic" operator="erode" radius="2.6" result="e"/>'
    '<feComposite in="SourceGraphic" in2="e" operator="out" result="o"/>'
    '<feGaussianBlur in="o" stdDeviation="7" result="b"/>'
    '<feMerge><feMergeNode in="b"/><feMergeNode in="b"/><feMergeNode in="o"/></feMerge></filter>'
)


def scene(obj, defs="", top="", shadow=True):
    sh = ' filter="url(#oshadow)"' if shadow else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{SIZE}" height="{SIZE}" viewBox="0 0 {SIZE} {SIZE}">'
            f'<defs>{DEFS}{defs}</defs><g{sh}>{obj}</g>{top}</svg>')


def sym(name, cx, cy, size, fill, filt=None, mid="pm", rot=0, opacity=1):
    """A glyph painted in `fill`, centred on (cx, cy)."""
    g = PLACE_GLYPHS.get(name) or GLYPHS[name]
    x, y = cx - size / 2, cy - size / 2
    f = f' filter="url(#{filt})"' if filt else ""
    r = f' transform="rotate({rot} {cx} {cy})"' if rot else ""
    return (f'<mask id="{mid}" maskUnits="userSpaceOnUse" x="0" y="0" width="{SIZE}" height="{SIZE}">'
            f'<g{r}><g transform="translate({x} {y}) scale({size / 100})">{g}</g></g></mask>'
            f'<g{f}><rect width="{SIZE}" height="{SIZE}" fill="{fill}" opacity="{opacity}" mask="url(#{mid})"/></g>')


SHINE = ('<linearGradient id="shine" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".9"/>'
         '<stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>')


def stars(points, fill="#fff", r=3):
    return "".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}"/>' for x, y in points)


def sparkle(x, y, s, fill="#fff"):
    return (f'<path d="M{x} {y - s}C{x + s * .15} {y - s * .15} {x + s * .15} {y - s * .15} {x + s} {y}'
            f'C{x + s * .15} {y + s * .15} {x + s * .15} {y + s * .15} {x} {y + s}C{x - s * .15} {y + s * .15} {x - s * .15} {y + s * .15} {x - s} {y}'
            f'C{x - s * .15} {y - s * .15} {x - s * .15} {y - s * .15} {x} {y - s}Z" fill="{fill}"/>')


# ================================================================ Halloween

class Halloween:
    lit = ["#ffb21a", "#8cff5a", "#c78bff", "#ff7a2a", "#ffe066", "#5ff0d0", "#ff5fa2"]

    @staticmethod
    def boot():
        """A bubbling cauldron over a fire."""
        fire = ('<path d="M150 452C150 410 178 404 186 372C200 404 214 392 222 360C236 396 250 380 256 344'
                'C262 380 276 396 290 360C298 392 312 404 326 372C334 404 362 410 362 452Z" fill="url(#fire)"/>')
        legs = '<path d="M150 400 128 448H150L172 410ZM362 400 384 448H362L340 410Z" fill="#17111c"/>'
        pot = ('<path d="M104 236H408C428 310 404 382 350 414C320 432 288 438 256 438C224 438 192 432 162 414C108 382 84 310 104 236Z" fill="url(#iron)"/>'
               '<path d="M136 270C130 320 150 370 196 398" fill="none" stroke="#6b5a78" stroke-width="7" stroke-linecap="round" opacity=".6"/>')
        rim = ('<ellipse cx="256" cy="236" rx="166" ry="34" fill="#2b2333"/>'
               '<ellipse cx="256" cy="232" rx="146" ry="24" fill="url(#brew)"/>'
               '<path d="M152 240C160 270 170 280 166 300C160 300 156 280 152 262Z" fill="#7cf04a"/>'
               '<path d="M330 244C336 262 344 268 340 284C334 282 330 266 330 252Z" fill="#7cf04a"/>')
        bubbles = ('<g fill="#9dff6a" filter="url(#softglow)">'
                   '<circle cx="210" cy="210" r="16"/><circle cx="272" cy="196" r="22"/><circle cx="318" cy="216" r="11"/>'
                   '<circle cx="246" cy="160" r="9"/><circle cx="296" cy="140" r="7"/><circle cx="232" cy="118" r="5"/></g>'
                   '<g fill="#e3ffcf" opacity=".8"><circle cx="204" cy="204" r="4"/><circle cx="264" cy="188" r="6"/></g>')
        return scene(fire + legs + pot + rim, top=bubbles,
                     defs=lin("fire", [(0, "#ffe066"), (.5, "#ff8a1c"), (1, "#c62f0c")])
                     + lin("iron", [(0, "#4a3d58"), (1, "#141018")], x2=1, y2=.4)
                     + rad("brew", [(0, "#c6ff7a"), (1, "#3fae2a")]))

    @staticmethod
    def external():
        """A coffin with a bat on the lid."""
        lid = ('<path d="M206 56H306L366 150 334 456H178L146 150Z" fill="url(#wood)" stroke="#2a1608" stroke-width="6" stroke-linejoin="round"/>'
               '<path d="M214 78H298L342 152 314 432H198L170 152Z" fill="none" stroke="#c68a52" stroke-width="4" opacity=".55"/>'
               + "".join(f'<path d="M{x} 110 {x - 6} 420" stroke="#4a2810" stroke-width="2" opacity=".35"/>' for x in (222, 256, 290)))
        bat = ('<path d="M256 236C248 222 236 222 226 228C214 214 196 214 180 222C194 230 198 244 196 256C210 248 226 252 236 264'
               'C242 254 250 250 256 250C262 250 270 254 276 264C286 252 302 248 316 256C314 244 318 230 332 222'
               'C316 214 298 214 286 228C276 222 264 222 256 236Z" fill="#1b1022"/>'
               '<path d="M248 232 250 220 256 228 262 220 264 232Z" fill="#1b1022"/>'
               '<circle cx="251" cy="238" r="2.5" fill="#ffb21a"/><circle cx="261" cy="238" r="2.5" fill="#ffb21a"/>')
        handles = "".join(f'<rect x="{x}" y="{y}" width="12" height="30" rx="5" fill="url(#brass)"/>'
                          for x, y in ((150, 196), (350, 196), (160, 330), (340, 330)))
        moon = '<path d="M372 60A44 44 0 1 0 420 120A34 34 0 1 1 372 60Z" fill="#fff2b8" filter="url(#softglow)"/>'
        return scene(lid + bat + handles, top=moon,
                     defs=lin("wood", [(0, "#8a4f24"), (1, "#4b2610")], x2=1, y2=1) + lin("brass", [(0, "#f2cf6a"), (1, "#a8741e")]))

    @staticmethod
    def network():
        """A crystal ball with swirling mist and stars."""
        stand = ('<path d="M168 392C168 362 344 362 344 392L366 444C366 458 146 458 146 444Z" fill="url(#claw)"/>'
                 '<path d="M190 380 176 412M256 374V414M322 380 336 412" stroke="#e0b25a" stroke-width="6" stroke-linecap="round"/>')
        ball = ('<circle cx="256" cy="236" r="160" fill="url(#orb)"/>'
                '<path d="M140 250C180 190 230 300 290 230C330 186 370 236 380 200" fill="none" stroke="#f3c6ff" stroke-width="14" stroke-linecap="round" opacity=".45" filter="url(#softglow)"/>'
                '<path d="M150 300C200 270 250 330 330 280" fill="none" stroke="#a46bff" stroke-width="10" stroke-linecap="round" opacity=".5"/>'
                + stars([(200, 170), (300, 150), (330, 300), (190, 320), (256, 210)], "#fff8d6", 4)
                + sparkle(300, 196, 16, "#fff8d6")
                + '<ellipse cx="196" cy="150" rx="52" ry="28" fill="#fff" opacity=".35" transform="rotate(-30 196 150)"/>')
        waves = ('<g fill="none" stroke="#c78bff" stroke-width="8" stroke-linecap="round" filter="url(#softglow)">'
                 '<path d="M408 120A120 120 0 0 1 432 210"/><path d="M432 80A170 170 0 0 1 466 210"/>'
                 '<path d="M104 120A120 120 0 0 0 80 210"/><path d="M80 80A170 170 0 0 0 46 210"/></g>')
        return scene(stand + ball, top=waves,
                     defs=rad("orb", [(0, "#d9a8ff"), (.55, "#6a2fb8"), (1, "#24103e")], fx=.4, fy=.35)
                     + lin("claw", [(0, "#4a3426"), (1, "#1c120c")]))

    @staticmethod
    def home():
        """A crooked haunted house with lit windows under a full moon."""
        moon = '<circle cx="360" cy="130" r="72" fill="#fff2b8" filter="url(#softglow)"/><circle cx="380" cy="116" r="12" fill="#efdc96"/><circle cx="340" cy="150" r="8" fill="#efdc96"/>'
        house = ('<path d="M108 456V250L176 196 244 250V456Z" fill="#2c2238"/>'
                 '<path d="M94 258 176 186 258 258" fill="none" stroke="#17111c" stroke-width="18" stroke-linejoin="round"/>'
                 '<path d="M226 456V196L286 130 352 196V456Z" fill="#3a2d48"/>'
                 '<path d="M212 204 286 118 366 204" fill="none" stroke="#17111c" stroke-width="18" stroke-linejoin="round"/>'
                 '<path d="M268 140V70L300 40 318 76V130Z" fill="#2c2238"/><path d="M262 78 300 30 326 82" fill="none" stroke="#17111c" stroke-width="12"/>'
                 '<rect x="88" y="446" width="300" height="14" rx="4" fill="#17111c"/>')
        win = ('<g fill="url(#lamp)" stroke="#17111c" stroke-width="5">'
               '<rect x="140" y="290" width="40" height="52"/><rect x="262" y="230" width="44" height="56"/>'
               '<rect x="262" y="320" width="44" height="56"/><path d="M286 70A12 12 0 0 1 298 82V100H274V82A12 12 0 0 1 286 70Z" transform="translate(4 0)"/>'
               '<path d="M134 456V392A26 26 0 0 1 186 392V456Z"/></g>'
               '<path d="M160 290V342M140 316H180M284 230V286M262 258H306" stroke="#17111c" stroke-width="4"/>')
        bats = ''.join(f'<path d="M{x} {y}q-10 -12 -22 -4q8 2 8 10q8 -6 14 2q6 -8 14 -2q0 -8 8 -10q-12 -8 -22 4Z" fill="#17111c"/>'
                       for x, y in ((420, 220), (400, 260), (110, 140)))
        return scene(moon + house + win, top=bats, shadow=False,
                     defs=rad("lamp", [(0, "#fff3a0"), (1, "#ff9a1c")]))

    @classmethod
    def fav(cls, place, i):
        """A tombstone with the symbol carved and lit."""
        stone = ('<path d="M136 446V200C136 120 196 76 256 76C316 76 376 120 376 200V446Z" fill="url(#stone)"/>'
                 '<path d="M156 430V204C156 136 204 98 256 98C308 98 356 136 356 204V430" fill="none" stroke="#9e98a8" stroke-width="4" opacity=".5"/>'
                 '<path d="M150 160C164 150 170 176 186 166" fill="none" stroke="#5e8a3a" stroke-width="7" stroke-linecap="round"/>'
                 '<path d="M110 448C150 420 180 452 220 432C260 452 300 420 340 440C370 426 392 444 404 452H108Z" fill="#3f6b2a"/>')
        pumpkin = ('<g transform="translate(358 404)"><ellipse rx="40" ry="32" fill="#ff8a1c"/><ellipse rx="16" ry="32" fill="none" stroke="#c4530a" stroke-width="4"/>'
                   '<path d="M-2 -30 0 -44 8 -42 4 -30Z" fill="#4f6b22"/></g>')
        return scene(stone + pumpkin, top=sym(place, 256, 272, 150, cls.lit[i], "carve"),
                     defs=lin("stone", [(0, "#8b8496"), (1, "#4d4757")], x2=1, y2=1))


# ================================================================ Winter Holiday

class Winter:
    baubles = ["#c62828", "#1f7a45", "#d9a21b", "#1f5fbf", "#7b3db8", "#9aa7b4", "#e2662a"]

    @staticmethod
    def boot():
        """A snow globe with a little forest inside."""
        base = ('<path d="M128 396H384L408 452H104Z" fill="url(#base)"/><rect x="128" y="384" width="256" height="20" rx="6" fill="#e8b23a"/>'
                '<rect x="128" y="392" width="256" height="4" fill="#fff3c4" opacity=".7"/>')
        globe = ('<circle cx="256" cy="232" r="168" fill="url(#glass)"/>'
                 '<path d="M100 300C150 270 210 290 256 280C310 270 360 280 410 300C400 350 340 398 256 398C172 398 110 350 100 300Z" fill="#f4f9ff"/>'
                 '<path d="M256 120 302 200H284L318 258H296L330 310H182L216 258H194L228 200H210Z" fill="#1f7a45"/>'
                 '<rect x="246" y="306" width="20" height="18" fill="#6f4520"/>'
                 '<path d="M176 210 196 250H186L204 282H148L166 250H156Z" fill="#2a8f53"/>'
                 '<path d="M334 214 352 250H344L360 280H310L326 250H316Z" fill="#2a8f53"/>'
                 '<path d="M256 108 262 120H250Z" fill="#ffd54a"/>'
                 + "".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#fff"/>' for x, y, r in
                           ((150, 160, 5), (190, 120, 4), (330, 120, 5), (370, 190, 4), (300, 160, 3), (220, 170, 3), (140, 250, 4), (380, 250, 5), (260, 80, 4)))
                 + '<path d="M150 130A150 150 0 0 1 270 72" fill="none" stroke="#fff" stroke-width="14" stroke-linecap="round" opacity=".55"/>')
        return scene(base + globe, defs=rad("glass", [(0, "#ffffff"), (.7, "#bfe3ff"), (1, "#7fb8e8")], fx=.35, fy=.3)
                     + lin("base", [(0, "#b3261e"), (1, "#6e1410")]))

    @staticmethod
    def external():
        """A wrapped present with a big bow and a tag."""
        box = ('<rect x="112" y="226" width="288" height="222" rx="10" fill="url(#paper)"/>'
               '<rect x="96" y="190" width="320" height="64" rx="10" fill="#d23a3a"/>'
               '<rect x="96" y="240" width="320" height="10" fill="#8e1818" opacity=".4"/>'
               '<rect x="230" y="190" width="52" height="258" fill="url(#rib)"/>'
               + "".join(f'<circle cx="{x}" cy="{y}" r="7" fill="#fff" opacity=".85"/>' for x, y in
                         ((150, 290), (190, 340), (150, 400), (330, 290), (370, 350), (320, 410), (200, 420), (360, 230), (140, 220))))
        bow = ('<path d="M256 192C220 120 140 120 150 166C158 200 220 196 256 192Z" fill="url(#rib)"/>'
               '<path d="M256 192C292 120 372 120 362 166C354 200 292 196 256 192Z" fill="url(#rib)"/>'
               '<path d="M244 196 206 256 226 258 250 214ZM268 196 306 256 286 258 262 214Z" fill="#127a3c"/>'
               '<ellipse cx="256" cy="192" rx="24" ry="20" fill="#1f9a52"/>')
        tag = ('<g transform="rotate(14 380 300)"><path d="M352 272H412V336H352L340 304Z" fill="#fff8ea" stroke="#c9bea6" stroke-width="2"/>'
               '<circle cx="354" cy="304" r="4" fill="#c9bea6"/><path d="M366 296H398M366 312H390" stroke="#c62828" stroke-width="4" stroke-linecap="round"/></g>')
        return scene(box + bow + tag, defs=lin("paper", [(0, "#e53935"), (1, "#a31c1c")]) + lin("rib", [(0, "#2fbf6a"), (1, "#167a40")], x2=1, y2=0))

    @staticmethod
    def network():
        """A red sleigh with gold runners, piled with presents."""
        presents = ('<rect x="200" y="124" width="76" height="76" rx="6" fill="#1f5fbf"/><rect x="232" y="124" width="12" height="76" fill="#ffd54a"/>'
                    '<rect x="270" y="98" width="86" height="102" rx="6" fill="#1f7a45"/><rect x="306" y="98" width="14" height="102" fill="#e8b23a"/>'
                    '<rect x="150" y="150" width="62" height="50" rx="6" fill="#7b3db8"/><rect x="176" y="150" width="10" height="50" fill="#fff"/>')
        body = ('<path d="M96 196H372C400 196 418 172 424 146C436 150 444 164 440 186C430 250 380 300 300 300H160C118 300 96 270 96 236Z" fill="url(#sl)"/>'
                '<path d="M110 214H380" stroke="#ffd54a" stroke-width="6" stroke-linecap="round"/>'
                '<path d="M120 236Q180 280 250 246Q320 280 380 236" fill="none" stroke="#ffd54a" stroke-width="5"/>')
        runners = ('<g fill="none" stroke="url(#gold)" stroke-width="14" stroke-linecap="round">'
                   '<path d="M150 300 140 360M330 300 340 360"/>'
                   '<path d="M70 362H404C440 362 458 340 452 312C448 296 432 292 424 302"/></g>')
        snow = "".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#fff"/>' for x, y, r in ((80, 120, 6), (130, 80, 4), (420, 90, 5), (460, 230, 4), (60, 260, 4), (390, 420, 5), (110, 430, 4)))
        trail = '<path d="M60 404C140 420 240 400 300 420" fill="none" stroke="#fff" stroke-width="5" stroke-dasharray="2 14" stroke-linecap="round" opacity=".8"/>'
        return scene(presents + body + runners, top=snow + trail,
                     defs=lin("sl", [(0, "#e53935"), (1, "#8e1818")]) + lin("gold", [(0, "#ffe08a"), (1, "#c8922a")]))

    @staticmethod
    def home():
        """A gingerbread house with icing, gumdrops and a candy-cane door."""
        walls = ('<rect x="130" y="230" width="252" height="216" fill="url(#gb)"/>'
                 '<path d="M96 246 256 96 416 246" fill="#a8622e"/>'
                 '<path d="M96 246 256 96 416 246" fill="none" stroke="#fff" stroke-width="20" stroke-linejoin="round" stroke-linecap="round"/>'
                 '<path d="M118 256Q132 276 146 256Q160 276 174 256Q188 276 202 256Q216 276 230 256Q244 276 258 256Q272 276 286 256Q300 276 314 256Q328 276 342 256Q356 276 370 256Q384 276 398 256" fill="none" stroke="#fff" stroke-width="9" stroke-linecap="round"/>'
                 '<rect x="318" y="118" width="36" height="70" fill="#a8622e"/><rect x="312" y="108" width="48" height="16" rx="8" fill="#fff"/>')
        door = ('<path d="M220 446V356A36 36 0 0 1 292 356V446Z" fill="#fff"/>'
                + "".join(f'<path d="M{220 + k * 18} 446 {238 + k * 18} 330" stroke="#d62b2b" stroke-width="7"/>' for k in range(-1, 4))
                + '<path d="M220 446V356A36 36 0 0 1 292 356V446" fill="none" stroke="#7a3d14" stroke-width="5"/>')
        door = f'<clipPath id="dc"><path d="M220 446V356A36 36 0 0 1 292 356V446Z"/></clipPath><g clip-path="url(#dc)">{door}</g>'
        windows = ('<g fill="#ffe28a" stroke="#fff" stroke-width="7"><rect x="152" y="290" width="54" height="54" rx="6"/><rect x="306" y="290" width="54" height="54" rx="6"/></g>'
                   '<path d="M179 290V344M152 317H206M333 290V344M306 317H360" stroke="#fff" stroke-width="5"/>')
        drops = "".join(f'<path d="M{x - 11} {y}A11 11 0 0 1 {x + 11} {y}Z" fill="{c}"/>' for x, y, c in
                        ((150, 232, "#e53935"), (200, 186, "#2fbf6a"), (256, 136, "#ffd54a"), (312, 186, "#7b3db8"), (362, 232, "#1f9ae0")))
        snow = '<path d="M110 446H402" stroke="#fff" stroke-width="14" stroke-linecap="round"/>'
        return scene(walls + windows + door + drops + snow, defs=lin("gb", [(0, "#c67a3e"), (1, "#9a5524")]))

    @classmethod
    def fav(cls, place, i):
        """A glass bauble with the symbol in frosted white."""
        c = cls.baubles[i]
        ball = ('<path d="M256 52C236 52 230 68 236 84" fill="none" stroke="#c8922a" stroke-width="7"/>'
                '<path d="M256 52C276 52 282 68 276 84" fill="none" stroke="#c8922a" stroke-width="7"/>'
                '<rect x="222" y="82" width="68" height="40" rx="6" fill="url(#cap)"/>'
                + "".join(f'<rect x="{x}" y="84" width="6" height="36" fill="#a8741e" opacity=".5"/>' for x in (232, 248, 264, 278))
                + f'<circle cx="256" cy="282" r="170" fill="url(#ball{i})"/>'
                '<path d="M110 250Q256 300 402 250" fill="none" stroke="#fff" stroke-width="6" stroke-dasharray="2 12" stroke-linecap="round" opacity=".6"/>'
                '<path d="M110 330Q256 380 402 330" fill="none" stroke="#fff" stroke-width="6" stroke-dasharray="2 12" stroke-linecap="round" opacity=".6"/>'
                '<ellipse cx="188" cy="190" rx="50" ry="30" fill="#fff" opacity=".45" transform="rotate(-35 188 190)"/>')
        return scene(ball, top=sym(place, 256, 290, 140, "#fffdf6", "gshadow"),
                     defs=lin("cap", [(0, "#ffe08a"), (1, "#c8922a")], x2=1, y2=0)
                     + rad(f"ball{i}", [(0, "#ffffff"), (.25, c), (1, "#1a1a1a")], fx=.35, fy=.3, r=.75))


# ================================================================ Thanksgiving

class Thanksgiving:
    nuts = ["#b8732e", "#a0522d", "#c98b3a", "#8a5a2b", "#d29a4a", "#9c4a1e", "#b5813f"]

    @staticmethod
    def boot():
        """A wicker cornucopia spilling over with produce."""
        horn = ('<path d="M436 92C420 70 392 76 386 100C376 140 330 176 250 196C190 210 150 240 140 300L332 360C356 300 380 250 402 200C420 160 450 120 436 92Z" fill="url(#wicker)"/>'
                + "".join(f'<path d="M{170 + k * 40} {320 - k * 30}Q{200 + k * 40} {250 - k * 36} {250 + k * 34} {226 - k * 32}" fill="none" stroke="#7a4a1c" stroke-width="5" opacity=".6"/>' for k in range(5))
                + '<ellipse cx="236" cy="330" rx="104" ry="52" fill="#6b3e16" transform="rotate(20 236 330)"/>')
        produce = ('<ellipse cx="150" cy="392" rx="70" ry="54" fill="#ff8a1c"/><path d="M150 340V444M112 352Q100 392 112 432M188 352Q200 392 188 432" fill="none" stroke="#d1610c" stroke-width="5"/>'
                   '<path d="M146 342 150 318 162 322 156 342Z" fill="#4f6b22"/>'
                   '<circle cx="262" cy="396" r="44" fill="#c62828"/><path d="M262 354Q270 340 284 336" stroke="#4f6b22" stroke-width="5" fill="none"/>'
                   '<ellipse cx="248" cy="380" rx="10" ry="6" fill="#fff" opacity=".4"/>'
                   + "".join(f'<circle cx="{x}" cy="{y}" r="16" fill="#6a2a8a"/>' for x, y in ((216, 304), (240, 318), (206, 334), (232, 346), (254, 300)))
                   + '<path d="M300 300C330 280 372 300 380 340C384 372 356 396 330 380C312 368 300 340 300 300Z" fill="#e8b23a"/>'
                   + "".join(f'<circle cx="{x}" cy="{y}" r="5" fill="#c88a1a"/>' for x, y in ((326, 320), (340, 336), (352, 352), (334, 352), (320, 338), (346, 370)))
                   + '<path d="M300 300C296 270 314 254 330 258C320 274 316 290 318 304Z" fill="#8bb04a"/>')
        return scene(horn + produce, defs=lin("wicker", [(0, "#e2b06a"), (1, "#a86a2a")], x2=1, y2=1))

    @staticmethod
    def external():
        """A lattice pie in its tin, with a slice of steam."""
        pie = ('<ellipse cx="256" cy="330" rx="200" ry="98" fill="#9aa2ab"/><ellipse cx="256" cy="318" rx="196" ry="92" fill="#c3cad1"/>'
               '<ellipse cx="256" cy="304" rx="178" ry="80" fill="url(#crust)"/>'
               '<ellipse cx="256" cy="300" rx="150" ry="64" fill="#a8341e"/>')
        lattice = ('<clipPath id="pc"><ellipse cx="256" cy="300" rx="150" ry="64"/></clipPath><g clip-path="url(#pc)" fill="#f0b766" stroke="#c98336" stroke-width="2">'
                   + "".join(f'<rect x="{x}" y="220" width="22" height="170" transform="rotate(-30 {x} 300)"/>' for x in range(110, 420, 50))
                   + "".join(f'<rect x="{x}" y="220" width="22" height="170" transform="rotate(30 {x} 300)"/>' for x in range(110, 420, 50))
                   + '</g>')
        rim = "".join(f'<ellipse cx="{256 + 178 * math.cos(a / 10)}" cy="{304 + 80 * math.sin(a / 10)}" rx="18" ry="10" fill="#e8a352"/>' for a in range(0, 63, 3))
        steam = ('<g fill="none" stroke="#fff" stroke-width="9" stroke-linecap="round" opacity=".75">'
                 '<path d="M210 210C190 180 230 160 210 120"/><path d="M262 200C242 160 282 140 262 90"/><path d="M314 210C294 180 334 160 314 124"/></g>')
        return scene(pie + lattice + rim, top=steam, defs=lin("crust", [(0, "#f2c27a"), (1, "#c98336")]))

    @staticmethod
    def network():
        """A wooden hay wagon carrying pumpkins."""
        hay = ('<path d="M100 236C110 190 160 170 200 178C230 150 300 150 330 176C370 166 412 196 412 236Z" fill="#f2cf6a"/>'
               + "".join(f'<path d="M{x} 236 {x + 10} {196 + (x % 30)}" stroke="#c8a03a" stroke-width="3"/>' for x in range(120, 400, 16)))
        pumpkins = ('<ellipse cx="190" cy="214" rx="44" ry="34" fill="#ff8a1c"/><ellipse cx="190" cy="214" rx="16" ry="34" fill="none" stroke="#d1610c" stroke-width="4"/>'
                    '<ellipse cx="300" cy="206" rx="54" ry="40" fill="#f07d12"/><ellipse cx="300" cy="206" rx="20" ry="40" fill="none" stroke="#c4530a" stroke-width="4"/>'
                    '<path d="M186 182 190 166 198 170 194 182ZM296 168 300 150 310 154 304 168Z" fill="#4f6b22"/>')
        bed = ('<rect x="84" y="236" width="344" height="92" rx="6" fill="url(#plank)"/>'
               + "".join(f'<path d="M84 {y}H428" stroke="#6f4520" stroke-width="3"/>' for y in (266, 298))
               + "".join(f'<rect x="{x}" y="236" width="12" height="92" fill="#6f4520"/>' for x in (96, 248, 404))
               + '<path d="M428 300 474 330" stroke="#6f4520" stroke-width="10" stroke-linecap="round"/>')
        def wheel(cx):
            return (f'<circle cx="{cx}" cy="370" r="58" fill="none" stroke="#5b3a1c" stroke-width="14"/>'
                    + "".join(f'<path d="M{cx} 370 {cx + 50 * c} {370 + 50 * s}" stroke="#5b3a1c" stroke-width="7"/>'
                              for c, s in ((1, 0), (-1, 0), (0, 1), (0, -1), (.7, .7), (-.7, .7), (.7, -.7), (-.7, -.7)))
                    + f'<circle cx="{cx}" cy="370" r="13" fill="#3a2410"/>')
        return scene(hay + pumpkins + bed + wheel(160) + wheel(352), defs=lin("plank", [(0, "#c68a52"), (1, "#8a5428")]))

    @staticmethod
    def home():
        """A white farmhouse with a red roof and an autumn tree."""
        tree = ('<rect x="388" y="300" width="18" height="150" fill="#5b3a1c"/>'
                '<circle cx="398" cy="270" r="62" fill="#d9792b"/><circle cx="360" cy="300" r="40" fill="#b3261e"/><circle cx="436" cy="300" r="38" fill="#e8b23a"/>')
        house = ('<rect x="96" y="250" width="270" height="198" fill="url(#siding)"/>'
                 + "".join(f'<path d="M96 {y}H366" stroke="#d8cfc0" stroke-width="2"/>' for y in range(266, 448, 16))
                 + '<path d="M72 262 231 120 390 262Z" fill="#a8341e"/><path d="M72 262 231 120 390 262" fill="none" stroke="#7a1e10" stroke-width="10" stroke-linejoin="round"/>'
                 '<rect x="300" y="128" width="32" height="76" fill="#8a3a20"/>'
                 '<rect x="96" y="366" width="270" height="14" fill="#7a1e10"/>'
                 + "".join(f'<rect x="{x}" y="380" width="10" height="68" fill="#fff"/>' for x in (100, 170, 290, 352))
                 + '<rect x="206" y="380" width="50" height="68" fill="#7a3d14"/><circle cx="246" cy="416" r="4" fill="#f2cf6a"/>'
                 + "".join(f'<g><rect x="{x}" y="288" width="52" height="58" fill="#ffe28a" stroke="#fff" stroke-width="6"/>'
                           f'<path d="M{x + 26} 288V346M{x} 317H{x + 52}" stroke="#fff" stroke-width="4"/>'
                           f'<rect x="{x - 14}" y="286" width="12" height="62" fill="#2c5f3a"/><rect x="{x + 54}" y="286" width="12" height="62" fill="#2c5f3a"/></g>' for x in (130, 278))
                 + '<circle cx="231" cy="210" r="22" fill="#ffe28a" stroke="#fff" stroke-width="6"/>')
        ground = '<path d="M60 448H460" stroke="#6b8a3a" stroke-width="12" stroke-linecap="round"/>'
        leaves = "".join(f'<ellipse cx="{x}" cy="{y}" rx="9" ry="5" fill="{c}" transform="rotate({x % 90} {x} {y})"/>'
                         for x, y, c in ((330, 420, "#d9792b"), (420, 440, "#b3261e"), (360, 380, "#e8b23a"), (450, 400, "#d9792b")))
        return scene(tree + house + ground, top=leaves, defs=lin("siding", [(0, "#fffaf0"), (1, "#eee4d2")]))

    @classmethod
    def fav(cls, place, i):
        """An acorn with the symbol stamped on the nut."""
        c = cls.nuts[i]
        acorn = (f'<path d="M136 220H376C380 320 330 420 256 456C182 420 132 320 136 220Z" fill="url(#nut{i})"/>'
                 '<path d="M176 250C170 320 196 380 236 420" fill="none" stroke="#fff" stroke-width="10" stroke-linecap="round" opacity=".25"/>'
                 '<path d="M110 228C110 150 180 112 256 112C332 112 402 150 402 228C402 244 110 244 110 228Z" fill="url(#cup)"/>'
                 + "".join(f'<path d="M{x} {y}l12 10 12 -10" fill="none" stroke="#5b3a1c" stroke-width="4" stroke-linejoin="round"/>'
                           for y in (150, 176, 202) for x in range(140 if y > 150 else 170, 372 if y > 150 else 342, 28))
                 + '<path d="M252 114C250 92 258 70 276 58" fill="none" stroke="#5b3a1c" stroke-width="14" stroke-linecap="round"/>'
                 '<path d="M282 70C320 40 372 54 380 80C350 96 308 92 282 70Z" fill="#8bb04a"/><path d="M286 72 372 78" stroke="#5f7d2b" stroke-width="3"/>')
        return scene(acorn, top=sym(place, 256, 332, 118, "#fff1cf", "gshadow"),
                     defs=lin(f"nut{i}", [(0, c), (1, "#4a2409")], x2=1, y2=1) + lin("cup", [(0, "#a8783f"), (1, "#6b4520")]))


# ================================================================ Valentine

class Valentine:
    candy = [("#ffd1dc", "#d6336c"), ("#d9f2e4", "#2f9e6a"), ("#fff1b8", "#d08a00"), ("#e3dcff", "#6a4fd8"),
             ("#ffe0cc", "#e2662a"), ("#d6ecff", "#2f74c0"), ("#ffd6f2", "#b02f8f")]

    @staticmethod
    def boot():
        """A heart-shaped jewellery box tied with a satin ribbon."""
        box = ('<path d="M256 452C190 404 80 344 80 230C80 156 136 112 196 120C226 124 246 140 256 160C266 140 286 124 316 120C376 112 432 156 432 230C432 344 322 404 256 452Z" fill="url(#box)"/>'
               '<path d="M256 412C200 372 116 324 116 236C116 180 158 150 200 156C224 160 242 174 256 196C270 174 288 160 312 156C354 150 396 180 396 236C396 324 312 372 256 412Z" fill="url(#lid)"/>'
               '<path d="M148 210C150 186 170 170 196 172" fill="none" stroke="#fff" stroke-width="12" stroke-linecap="round" opacity=".5"/>')
        ribbon = ('<path d="M256 160V430" stroke="url(#sat)" stroke-width="30"/>'
                  '<path d="M90 256Q256 300 422 256" fill="none" stroke="url(#sat)" stroke-width="26"/>'
                  '<path d="M256 250C220 200 160 200 166 236C172 266 224 262 256 250ZM256 250C292 200 352 200 346 236C340 266 288 262 256 250Z" fill="#ffe08a" stroke="#c8922a" stroke-width="4"/>'
                  '<circle cx="256" cy="254" r="18" fill="#ffd54a" stroke="#c8922a" stroke-width="4"/>')
        return scene(box + ribbon, top=sparkle(390, 110, 22, "#fff") + sparkle(120, 400, 14, "#ffd1dc"),
                     defs=lin("box", [(0, "#c2185b"), (1, "#7a0c33")]) + lin("lid", [(0, "#ff5c8a"), (1, "#d81b60")])
                     + lin("sat", [(0, "#ffe08a"), (1, "#e0a92a")], x2=1, y2=0))

    @staticmethod
    def external():
        """A gold heart locket on a chain with a gem."""
        chain = "".join(f'<ellipse cx="{x}" cy="{y}" rx="10" ry="6" fill="none" stroke="#d8a93a" stroke-width="4" transform="rotate({r} {x} {y})"/>'
                        for x, y, r in ((256, 56, 0), (232, 64, 20), (210, 80, 40), (194, 102, 60), (182, 126, 75),
                                        (280, 64, -20), (302, 80, -40), (318, 102, -60), (330, 126, -75)))
        locket = ('<rect x="240" y="120" width="32" height="34" rx="10" fill="url(#gold)"/>'
                  '<path d="M256 456C196 410 100 356 100 258C100 196 148 158 198 164C224 168 244 182 256 202C268 182 288 168 314 164C364 158 412 196 412 258C412 356 316 410 256 456Z" fill="url(#gold)"/>'
                  '<path d="M256 424C206 386 132 342 132 264C132 216 168 190 204 194C226 196 244 210 256 230C268 210 286 196 308 194C344 190 380 216 380 264C380 342 306 386 256 424Z" fill="none" stroke="#fff3c4" stroke-width="5" opacity=".7"/>'
                  + "".join(f'<circle cx="{x}" cy="{y}" r="3" fill="#a8741e"/>' for x, y in ((170, 250), (200, 220), (340, 250), (310, 220), (256, 400), (200, 340), (312, 340)))
                  + '<path d="M256 260 290 300 256 360 222 300Z" fill="url(#gem)" stroke="#fff" stroke-width="3"/>'
                  '<path d="M256 260 266 300 256 360 246 300Z" fill="#fff" opacity=".35"/>')
        return scene(chain + locket, top=sparkle(340, 220, 18),
                     defs=lin("gold", [(0, "#ffe08a"), (.5, "#e0a92a"), (1, "#a8741e")], x2=1, y2=1)
                     + lin("gem", [(0, "#ff7aa2"), (1, "#b0103c")]))

    @staticmethod
    def network():
        """A paper-plane love letter leaving a dotted trail of hearts."""
        trail = ('<path d="M70 420C120 380 140 440 200 390C230 364 236 330 262 320" fill="none" stroke="#ff7aa2" stroke-width="6" stroke-dasharray="4 14" stroke-linecap="round"/>'
                 + "".join(f'<path d="M0 6C0-2 10-2 10 4C10-2 20-2 20 6C20 13 12 17 10 22C8 17 0 13 0 6Z" transform="translate({x} {y}) scale({s})" fill="#e0365d"/>'
                           for x, y, s in ((56, 380, 2), (128, 434, 1.6), (176, 356, 1.4))))
        plane = ('<path d="M244 310 452 70 300 380 268 316Z" fill="#f4c6d2"/>'
                 '<path d="M244 310 452 70 176 236Z" fill="#fff4f7"/>'
                 '<path d="M268 316 452 70 300 380Z" fill="#fde3ea"/>'
                 '<path d="M244 310 268 316 262 362Z" fill="#e7a7b9"/>'
                 '<path d="M244 310 452 70" stroke="#e7a7b9" stroke-width="3"/>')
        seal = '<path d="M0 6C0-2 10-2 10 4C10-2 20-2 20 6C20 13 12 17 10 22C8 17 0 13 0 6Z" transform="translate(290 196) scale(3.2)" fill="url(#wax)"/>'
        return scene(plane + seal, top=trail, defs=lin("wax", [(0, "#e0365d"), (1, "#a8102f")]))

    @staticmethod
    def home():
        """A pink cottage with a heart door and climbing roses."""
        house = ('<rect x="122" y="236" width="268" height="212" fill="url(#wall)"/>'
                 '<path d="M90 252 256 110 422 252Z" fill="#c2185b"/>'
                 + "".join(f'<path d="M{110 + k * 26} {236 - k * 21}Q{124 + k * 26} {250 - k * 21} {138 + k * 26} {236 - k * 21}" fill="none" stroke="#8e0f3e" stroke-width="3"/>' for k in range(6))
                 + "".join(f'<path d="M{402 - k * 26} {236 - k * 21}Q{388 - k * 26} {250 - k * 21} {374 - k * 26} {236 - k * 21}" fill="none" stroke="#8e0f3e" stroke-width="3"/>' for k in range(6))
                 + '<path d="M90 252 256 110 422 252" fill="none" stroke="#8e0f3e" stroke-width="10" stroke-linejoin="round"/>'
                 '<path d="M256 448C226 420 200 404 200 372C200 350 218 338 234 342C244 344 252 350 256 360C260 350 268 344 278 342C294 338 312 350 312 372C312 404 286 420 256 448Z" fill="#e0365d" stroke="#8e0f3e" stroke-width="5"/>'
                 '<circle cx="290" cy="392" r="4" fill="#ffe08a"/>'
                 + "".join(f'<rect x="{x}" y="276" width="52" height="52" rx="26" fill="#ffe8ef" stroke="#fff" stroke-width="6"/>'
                           f'<path d="M{x + 26} 276V328M{x} 302H{x + 52}" stroke="#fff" stroke-width="4"/>' for x in (148, 312))
                 + '<path d="M256 204C246 196 240 192 240 184C240 178 246 174 250 176C253 177 255 179 256 182C257 179 259 177 262 176C266 174 272 178 272 184C272 192 266 196 256 204Z" fill="#ff7aa2"/>')
        vine = ('<path d="M122 448C110 400 140 360 120 320C104 290 128 260 122 240" fill="none" stroke="#3a8a4a" stroke-width="6"/>'
                + "".join(f'<circle cx="{x}" cy="{y}" r="11" fill="#e0365d"/><circle cx="{x}" cy="{y}" r="5" fill="#a8102f"/>' for x, y in ((116, 420), (130, 370), (112, 320), (126, 268)))
                + "".join(f'<ellipse cx="{x}" cy="{y}" rx="10" ry="5" fill="#3a8a4a" transform="rotate(-30 {x} {y})"/>' for x, y in ((136, 398), (104, 346), (138, 292))))
        ground = '<path d="M80 448H432" stroke="#f48fb1" stroke-width="12" stroke-linecap="round"/>'
        return scene(house + ground, top=vine, defs=lin("wall", [(0, "#ffd1dc"), (1, "#f6a5bd")]))

    @classmethod
    def fav(cls, place, i):
        """A candy conversation heart with the symbol printed on it."""
        light, ink = cls.candy[i]
        heart = (f'<path d="M256 452C186 404 72 340 72 226C72 150 132 104 194 112C224 116 244 134 256 156C268 134 288 116 318 112C380 104 440 150 440 226C440 340 326 404 256 452Z" fill="{ink}" opacity=".35" transform="translate(0 10)"/>'
                 f'<path d="M256 452C186 404 72 340 72 226C72 150 132 104 194 112C224 116 244 134 256 156C268 134 288 116 318 112C380 104 440 150 440 226C440 340 326 404 256 452Z" fill="url(#candy{i})"/>'
                 '<path d="M126 196C132 162 162 144 194 148" fill="none" stroke="#fff" stroke-width="14" stroke-linecap="round" opacity=".6"/>')
        return scene(heart, top=sym(place, 256, 272, 140, ink),
                     defs=rad(f"candy{i}", [(0, "#ffffff"), (.5, light), (1, light)], fx=.4, fy=.3, r=.7))


# ================================================================ Harvest

class Harvest:
    jams = ["#c62828", "#e8b23a", "#7b2d6b", "#e2662a", "#5a8a2a", "#8e1838", "#d29a4a"]

    @staticmethod
    def boot():
        """A tall grain silo with a domed cap and ladder."""
        silo = ('<rect x="176" y="130" width="160" height="320" fill="url(#steel)"/>'
                + "".join(f'<path d="M176 {y}H336" stroke="#8a929b" stroke-width="3"/>' for y in range(160, 450, 30))
                + '<path d="M168 136C168 70 344 70 344 136Z" fill="url(#dome)"/>'
                '<rect x="244" y="54" width="24" height="24" rx="4" fill="#9aa2ab"/>'
                '<path d="M312 136V450M332 136V450" stroke="#4b5560" stroke-width="5"/>'
                + "".join(f'<path d="M312 {y}H332" stroke="#4b5560" stroke-width="4"/>' for y in range(150, 450, 20)))
        barn = ('<rect x="72" y="300" width="116" height="150" fill="#b3261e"/><path d="M60 306 130 240 200 306Z" fill="#7a1e10"/>'
                '<rect x="104" y="370" width="52" height="80" fill="#fff"/><path d="M104 370 156 450M156 370 104 450" stroke="#b3261e" stroke-width="6"/>'
                '<rect x="104" y="370" width="52" height="80" fill="none" stroke="#fff" stroke-width="6"/>')
        wheat = ('<g transform="translate(398 450)">' + "".join(
            f'<g transform="rotate({r})"><path d="M0 0V-140" stroke="#c8a03a" stroke-width="4"/>'
            + "".join(f'<ellipse cx="{dx}" cy="{-150 + k * 14}" rx="6" ry="11" fill="#e2b54c" transform="rotate({dx * 3} {dx} {-150 + k * 14})"/>' for k in range(5) for dx in (-7, 7))
            + '</g>' for r in (-14, 0, 14)) + '</g>')
        return scene(silo + barn + wheat, defs=lin("steel", [(0, "#dfe4e8"), (.5, "#aab3bb"), (1, "#7d8790")], x2=1, y2=0)
                     + lin("dome", [(0, "#c3cad1"), (1, "#7d8790")]))

    @staticmethod
    def external():
        """An oak barrel with iron hoops."""
        barrel = ('<path d="M150 80H362C410 180 410 340 362 440H150C102 340 102 180 150 80Z" fill="url(#oak)"/>'
                  + "".join(f'<path d="M{x} 80C{x + (x - 256) * .4} 180 {x + (x - 256) * .4} 340 {x} 440" fill="none" stroke="#6f4520" stroke-width="3" opacity=".7"/>'
                            for x in (184, 220, 256, 292, 328))
                  + "".join(f'<path d="M{132 - abs(y - 260) * .1} {y}H{380 + abs(y - 260) * .1}" stroke="url(#iron)" stroke-width="18" stroke-linecap="round"/>' for y in (126, 210, 310, 394))
                  + '<ellipse cx="256" cy="82" rx="106" ry="18" fill="#a8713a"/><ellipse cx="256" cy="82" rx="90" ry="12" fill="#c68a52"/>'
                  '<rect x="236" y="246" width="40" height="28" rx="6" fill="#5b3a1c"/><rect x="250" y="270" width="12" height="20" fill="#3a2410"/>')
        apples = '<circle cx="116" cy="420" r="30" fill="#c62828"/><circle cx="396" cy="430" r="26" fill="#8bb04a"/><path d="M116 392q6 -12 16 -14M396 406q4 -10 14 -12" stroke="#4f6b22" stroke-width="5" fill="none"/>'
        return scene(barrel + apples, defs=lin("oak", [(0, "#8a5428"), (.5, "#c68a52"), (1, "#7a4720")], x2=1, y2=0)
                     + lin("iron", [(0, "#6b737c"), (1, "#3a4048")]))

    @staticmethod
    def network():
        """A farm windpump: a lattice tower with a spinning fan wheel and a tail vane."""
        tower = ('<path d="M226 200 170 452M286 200 342 452" stroke="#6f4520" stroke-width="10"/>'
                 + "".join(f'<path d="M{226 - k * 14} {200 + k * 63}L{286 + (k + 1) * 14} {200 + (k + 1) * 63}M{286 + k * 14} {200 + k * 63}L{226 - (k + 1) * 14} {200 + (k + 1) * 63}" stroke="#8a5428" stroke-width="5"/>' for k in range(4))
                 + '<rect x="214" y="190" width="84" height="16" fill="#5b3a1c"/>')
        blades = "".join(f'<path d="M256 150 {256 + 120 * math.cos((a - 7) * 3.14159 / 180)} {150 + 120 * math.sin((a - 7) * 3.14159 / 180)}'
                         f' {256 + 120 * math.cos((a + 7) * 3.14159 / 180)} {150 + 120 * math.sin((a + 7) * 3.14159 / 180)}Z" fill="{("#e8e0cc", "#c62828")[k % 2]}"/>'
                         for k, a in enumerate(range(0, 360, 20)))
        hub = ('<circle cx="256" cy="150" r="120" fill="none" stroke="#5b3a1c" stroke-width="5"/><circle cx="256" cy="150" r="62" fill="none" stroke="#5b3a1c" stroke-width="4"/>'
               '<path d="M270 150H420L448 112V188L420 150" fill="#c62828" stroke="#5b3a1c" stroke-width="4"/>'
               '<circle cx="256" cy="150" r="18" fill="#5b3a1c"/>')
        grass = '<path d="M80 452C120 430 150 452 190 436C230 452 270 430 310 446C350 430 390 452 432 440V456H80Z" fill="#6b8a3a"/>'
        return scene(tower + blades + hub + grass)

    @staticmethod
    def home():
        """A red gambrel barn with white trim and a hayloft."""
        barn = ('<path d="M96 448V230L148 140 256 96 364 140 416 230V448Z" fill="url(#barn)"/>'
                + "".join(f'<path d="M{x} 150V448" stroke="#8e1818" stroke-width="3" opacity=".5"/>' for x in range(120, 410, 24))
                + '<path d="M96 230L148 140 256 96 364 140 416 230" fill="none" stroke="#fff" stroke-width="12" stroke-linejoin="round"/>'
                '<rect x="196" y="300" width="120" height="148" fill="#8e1818" stroke="#fff" stroke-width="10"/>'
                '<path d="M196 300 316 448M316 300 196 448M256 300V448" stroke="#fff" stroke-width="8"/>'
                '<rect x="224" y="168" width="64" height="70" fill="#f2cf6a" stroke="#fff" stroke-width="8"/>'
                + "".join(f'<path d="M{x} 238 {x + 6} 200" stroke="#c8a03a" stroke-width="4"/>' for x in range(230, 286, 10))
                + '<path d="M232 168 256 150 280 168" fill="none" stroke="#fff" stroke-width="6"/>')
        bales = ('<rect x="56" y="398" width="72" height="52" rx="10" fill="#e2b54c"/><path d="M56 414H128M56 434H128" stroke="#b9892a" stroke-width="3"/>'
                 '<rect x="384" y="404" width="72" height="46" rx="10" fill="#e2b54c"/><path d="M384 420H456M384 436H456" stroke="#b9892a" stroke-width="3"/>')
        return scene(barn + bales, defs=lin("barn", [(0, "#d23a2a"), (1, "#9a1e16")]))

    @classmethod
    def fav(cls, place, i):
        """A mason jar of preserves with a branded label."""
        c = cls.jams[i]
        jar = (f'<path d="M150 140H362V170C400 200 404 240 404 290V410C404 440 384 456 352 456H160C128 456 108 440 108 410V290C108 240 112 200 150 170Z" fill="{c}"/>'
               '<path d="M150 140H362V170C400 200 404 240 404 290V410C404 440 384 456 352 456H160C128 456 108 440 108 410V290C108 240 112 200 150 170Z" fill="url(#glassj)"/>'
               '<path d="M134 250V400" stroke="#fff" stroke-width="14" stroke-linecap="round" opacity=".45"/>'
               '<rect x="140" y="82" width="232" height="62" rx="10" fill="url(#lidj)"/>'
               + "".join(f'<path d="M{x} 86V140" stroke="#a8741e" stroke-width="3" opacity=".6"/>' for x in range(156, 372, 14))
               + '<path d="M130 96Q256 40 382 96L372 70Q256 20 140 70Z" fill="#f4e2c4"/><path d="M130 96Q256 40 382 96" fill="none" stroke="#c62828" stroke-width="4" stroke-dasharray="10 8"/>'
               '<rect x="160" y="240" width="192" height="150" rx="14" fill="#f6ead0" stroke="#a8713a" stroke-width="4"/>')
        return scene(jar, top=sym(place, 256, 315, 112, "#4a2409", "gshadow"),
                     defs='<linearGradient id="glassj" x1="0" y1="0" x2="1" y2=".2"><stop offset="0" stop-color="#fff" stop-opacity=".3"/>'
                     '<stop offset=".35" stop-color="#fff" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".3"/></linearGradient>'
                     + lin("lidj", [(0, "#ffe08a"), (1, "#c8922a")]))


# ================================================================ Sci-Fi HUD

class SciFi:
    holo = ["#7df7ff", "#ff5fd2", "#ffc233", "#3ddc84", "#9c8cff", "#ff7a4d", "#5fb8ff"]

    @staticmethod
    def boot():
        """A reactor core: a glowing column held between steel caps."""
        core = ('<rect x="186" y="120" width="140" height="272" rx="20" fill="#06131d"/>'
                '<rect x="206" y="128" width="100" height="256" rx="50" fill="url(#plasma)" filter="url(#glow)"/>'
                + "".join(f'<ellipse cx="256" cy="{y}" rx="88" ry="16" fill="none" stroke="#45f0ff" stroke-width="4" opacity=".75"/>' for y in (170, 230, 290, 350))
                + '<path d="M150 60H362L382 120H130Z" fill="url(#cap)"/><path d="M130 392H382L362 452H150Z" fill="url(#cap)"/>'
                + "".join(f'<circle cx="{x}" cy="{y}" r="6" fill="#c6cfd8"/>' for x in (170, 256, 342) for y in (90, 422))
                + '<rect x="220" y="402" width="30" height="8" rx="4" fill="#3ddc84"/><rect x="262" y="402" width="30" height="8" rx="4" fill="#ffc233"/>'
                '<path d="M110 180H150M110 260H150M362 220H402M362 300H402" stroke="#45f0ff" stroke-width="6" stroke-linecap="round" opacity=".7"/>')
        return scene(core, defs=lin("plasma", [(0, "#e6fdff"), (.5, "#45f0ff"), (1, "#1a7fff")], x2=1, y2=0)
                     + lin("cap", [(0, "#8794a2"), (1, "#3d4651")]))

    @staticmethod
    def external():
        """A data cartridge with gold contacts and a lit status bar."""
        cart = ('<path d="M136 100 176 60H376V420L336 460H136Z" fill="url(#shell)" stroke="#1e252d" stroke-width="5"/>'
                '<path d="M166 120H346V300H166Z" fill="#06131d" stroke="#2a3540" stroke-width="4"/>'
                + "".join(f'<path d="M176 {y}H{336 - (y % 40)}" stroke="#45f0ff" stroke-width="5" stroke-linecap="round" opacity=".8"/>' for y in range(140, 290, 22))
                + '<rect x="166" y="320" width="180" height="16" rx="8" fill="#0d1a24"/><rect x="170" y="324" width="120" height="8" rx="4" fill="#3ddc84" filter="url(#softglow)"/>'
                + "".join(f'<rect x="{x}" y="380" width="14" height="60" rx="2" fill="url(#pin)"/>' for x in range(168, 340, 24))
                + "".join(f'<circle cx="{x}" cy="{y}" r="5" fill="#c6cfd8"/>' for x, y in ((156, 120), (356, 80), (356, 400), (156, 440))))
        return scene(cart, defs=lin("shell", [(0, "#8794a2"), (1, "#4b5560")], x2=1, y2=1) + lin("pin", [(0, "#ffe08a"), (1, "#c8922a")]))

    @staticmethod
    def network():
        """A satellite dish on a mount, beaming a signal."""
        dish = ('<path d="M250 330 196 452H316Z" fill="url(#mount)"/><rect x="170" y="440" width="172" height="16" rx="6" fill="#3d4651"/>'
                '<path d="M112 140C108 250 190 340 310 334Z" fill="url(#dish)" stroke="#2a323b" stroke-width="5" stroke-linejoin="round"/>'
                '<path d="M112 140 310 334" stroke="#2a323b" stroke-width="5"/>'
                '<path d="M210 236 300 150" stroke="#9aa6b2" stroke-width="8"/><circle cx="304" cy="146" r="14" fill="#45f0ff" filter="url(#glow)"/>')
        beams = ('<g fill="none" stroke="#7df7ff" stroke-width="9" stroke-linecap="round" filter="url(#softglow)">'
                 '<path d="M340 104A60 60 0 0 1 350 170"/><path d="M372 72A106 106 0 0 1 390 196"/><path d="M404 42A150 150 0 0 1 430 222"/></g>'
                 + stars([(80, 60), (150, 80), (440, 300), (420, 400), (70, 300)], "#c6f8ff", 3))
        return scene(dish, top=beams, defs=lin("dish", [(0, "#e3e9ef"), (1, "#7d8a97")], x2=1, y2=1) + lin("mount", [(0, "#8794a2"), (1, "#3d4651")]))

    @staticmethod
    def home():
        """A ring space station with a central hub and solar wings."""
        ring = ('<ellipse cx="256" cy="256" rx="190" ry="82" fill="none" stroke="url(#ring)" stroke-width="34"/>'
                + "".join(f'<rect x="{256 + 190 * math.cos(a * math.pi / 180) - 10}" y="{256 + 82 * math.sin(a * math.pi / 180) - 10}" width="20" height="20" fill="#45f0ff" opacity=".85"/>'
                          for a in range(0, 360, 30)))
        wings = "".join(f'<rect x="{x}" y="96" width="70" height="40" fill="#1a3f6e" stroke="#7df7ff" stroke-width="3"/>'
                        f'<path d="M{x + 23} 96V136M{x + 46} 96V136M{x} 116H{x + 70}" stroke="#7df7ff" stroke-width="2" opacity=".6"/>' for x in (130, 312))
        hub = ('<path d="M200 116H312" stroke="#8794a2" stroke-width="8"/><path d="M256 116V420" stroke="#8794a2" stroke-width="14"/>'
               '<circle cx="256" cy="256" r="68" fill="url(#hub)" stroke="#2a323b" stroke-width="5"/>'
               '<circle cx="256" cy="256" r="30" fill="#06131d"/><circle cx="256" cy="256" r="18" fill="#7df7ff" filter="url(#glow)"/>'
               '<rect x="236" y="400" width="40" height="40" rx="8" fill="#56616e"/>')
        front = '<path d="M66 256A190 82 0 0 0 446 256" fill="none" stroke="url(#ring)" stroke-width="34"/>'
        return scene(wings + ring + hub + front, top=stars([(60, 80), (460, 120), (420, 440), (90, 420), (190, 60)], "#c6f8ff", 3),
                     defs=lin("ring", [(0, "#c6cfd8"), (1, "#56616e")]) + rad("hub", [(0, "#c6cfd8"), (1, "#56616e")]))

    @classmethod
    def fav(cls, place, i):
        """A hexagonal hologram panel with the symbol projected in it."""
        c = cls.holo[i]
        hexagon = "M256 56 430 156V356L256 456 82 356V156Z"
        panel = (f'<path d="{hexagon}" fill="#06131d" stroke="#56616e" stroke-width="10"/>'
                 f'<path d="M256 84 406 170V342L256 428 106 342V170Z" fill="none" stroke="{c}" stroke-width="5" filter="url(#softglow)"/>'
                 + "".join(f'<path d="M120 {y}H392" stroke="{c}" stroke-width="1.5" opacity=".15"/>' for y in range(170, 350, 8))
                 + "".join(f'<circle cx="{x}" cy="{y}" r="6" fill="#c6cfd8"/>' for x, y in ((256, 70), (418, 162), (418, 350), (256, 442), (94, 350), (94, 162))))
        return scene(panel, top=sym(place, 256, 256, 150, c, "glow"))


# ================================================================ Synthwave '84

class Synthwave:
    neon = ["#ff4fd8", "#4ff0ff", "#ffcf4a", "#8a3de0", "#ff8a3d", "#5fff9a", "#ff4f6a"]

    @staticmethod
    def boot():
        """A chrome boombox with twin speakers and a sunset stripe."""
        def speaker(cx):
            return (f'<circle cx="{cx}" cy="316" r="72" fill="#15151a"/><circle cx="{cx}" cy="316" r="62" fill="url(#cone)"/>'
                    f'<circle cx="{cx}" cy="316" r="20" fill="#2c2c35"/><circle cx="{cx}" cy="316" r="72" fill="none" stroke="url(#chrome)" stroke-width="8"/>')
        box = ('<path d="M160 160V118Q160 96 182 96H330Q352 96 352 118V160" fill="none" stroke="url(#chrome)" stroke-width="16"/>'
               '<rect x="64" y="160" width="384" height="264" rx="30" fill="url(#chrome)"/>'
               '<rect x="76" y="172" width="360" height="240" rx="22" fill="#2c2c35"/>'
               + "".join(f'<rect x="76" y="{196 + k * 8}" width="360" height="8" fill="{c}"/>' for k, c in enumerate(("#ffcf4a", "#ff8a3d", "#f0478c", "#8a3de0")))
               + speaker(160) + speaker(352)
               + '<rect x="214" y="258" width="84" height="56" rx="6" fill="#fbf3e3"/><rect x="226" y="276" width="60" height="20" rx="10" fill="#15151a"/>'
               '<circle cx="240" cy="286" r="6" fill="#f4f4f6"/><circle cx="272" cy="286" r="6" fill="#f4f4f6"/>'
               + "".join(f'<rect x="{x}" y="336" width="14" height="22" rx="3" fill="#8c8c98"/>' for x in (214, 236, 258, 280))
               + '<rect x="214" y="370" width="84" height="10" rx="5" fill="#ff4fd8" filter="url(#softglow)"/>')
        return scene(box, defs=lin("chrome", [(0, "#ffffff"), (.45, "#b8bcc8"), (.55, "#7d8190"), (1, "#e0e3ea")])
                     + rad("cone", [(0, "#4a4a56"), (1, "#15151a")]))

    @staticmethod
    def external():
        """A VHS tape with a neon sunset label."""
        tape = ('<rect x="64" y="136" width="384" height="240" rx="16" fill="#1d1d24"/>'
                '<rect x="64" y="136" width="384" height="240" rx="16" fill="none" stroke="#3a3a44" stroke-width="4"/>'
                '<rect x="92" y="160" width="328" height="110" rx="6" fill="url(#sun)"/>'
                + "".join(f'<rect x="92" y="{226 + k * 9}" width="328" height="4" fill="#1d1d24"/>' for k in range(5))
                + '<circle cx="256" cy="222" r="38" fill="#ffcf4a"/>'
                + "".join(f'<rect x="210" y="{214 + k * 8}" width="92" height="3" fill="#ff4f8a"/>' for k in range(4))
                + f'<text x="256" y="196" {MONO} font-size="24" text-anchor="middle" fill="#fbf3e3" letter-spacing="6">RAD</text>'
                '<rect x="140" y="290" width="232" height="66" rx="8" fill="#0d0d12"/>'
                '<circle cx="190" cy="323" r="24" fill="#2c2c35"/><circle cx="322" cy="323" r="24" fill="#2c2c35"/>'
                '<circle cx="190" cy="323" r="9" fill="#8c8c98"/><circle cx="322" cy="323" r="9" fill="#8c8c98"/>'
                '<rect x="226" y="306" width="60" height="34" rx="4" fill="#3a3a44"/>')
        grid = ('<g stroke="#ff4fd8" stroke-width="3" opacity=".8" filter="url(#softglow)">'
                '<path d="M40 420H472M80 448H432"/>'
                + "".join(f'<path d="M256 396 {256 + k * 60} 470"/>' for k in range(-3, 4)) + '</g>')
        return scene(tape, top=grid, defs=lin("sun", [(0, "#2a1458"), (.6, "#c2185b"), (1, "#ff8a3d")]))

    @staticmethod
    def network():
        """A radio tower silhouetted against a neon sunset over a grid."""
        sun = ('<clipPath id="sc"><circle cx="256" cy="236" r="160"/></clipPath>'
               '<g clip-path="url(#sc)"><rect x="96" y="76" width="320" height="320" fill="url(#sunset)"/>'
               + "".join(f'<rect x="96" y="{250 + k * 22}" width="320" height="{4 + k * 2}" fill="#1a0b33"/>' for k in range(6)) + '</g>')
        grid = ('<g stroke="#4ff0ff" stroke-width="3" filter="url(#softglow)">'
                '<path d="M48 330H464M60 366H452M76 408H436M96 452H416"/>'
                + "".join(f'<path d="M256 330 {256 + k * 52} 456"/>' for k in range(-4, 5)) + '</g>')
        tower = ('<g stroke="#1a0b33" stroke-width="9" stroke-linecap="round"><path d="M256 70 212 330M256 70 300 330"/>'
                 '<path d="M240 160H272M228 230H284M218 290H294M236 160 284 230M276 160 228 230M228 230 294 290M284 230 218 290"/></g>'
                 '<circle cx="256" cy="66" r="10" fill="#ff4fd8" filter="url(#glow)"/>')
        waves = ('<g transform="translate(0 28)" fill="none" stroke="#ff4fd8" stroke-width="8" stroke-linecap="round" filter="url(#softglow)">'
                 '<path d="M296 40A60 60 0 0 1 296 96"/><path d="M328 20A100 100 0 0 1 328 116"/>'
                 '<path d="M216 40A60 60 0 0 0 216 96"/><path d="M184 20A100 100 0 0 0 184 116"/></g>')
        return scene(sun + grid + tower, top=waves, shadow=False,
                     defs=lin("sunset", [(0, "#ffcf4a"), (.45, "#ff8a3d"), (.75, "#f0478c"), (1, "#8a3de0")]))

    @staticmethod
    def home():
        """A pastel beach villa with a palm tree under a striped sun."""
        sun = ('<clipPath id="hs"><circle cx="300" cy="200" r="130"/></clipPath><g clip-path="url(#hs)"><rect x="170" y="70" width="260" height="260" fill="url(#sunset)"/>'
               + "".join(f'<rect x="170" y="{200 + k * 20}" width="260" height="{3 + k * 2}" fill="#2a1458"/>' for k in range(6)) + '</g>')
        villa = ('<rect x="150" y="250" width="260" height="190" fill="#ffd6f2"/>'
                 '<rect x="150" y="236" width="260" height="20" fill="#4ff0ff"/>'
                 '<rect x="250" y="200" width="160" height="40" fill="#ffd6f2"/><rect x="250" y="190" width="160" height="14" fill="#4ff0ff"/>'
                 '<rect x="180" y="290" width="70" height="60" fill="#2a1458"/><rect x="180" y="290" width="70" height="60" fill="none" stroke="#ff4fd8" stroke-width="5" filter="url(#softglow)"/>'
                 '<rect x="300" y="290" width="80" height="150" fill="#8a3de0"/><circle cx="366" cy="370" r="5" fill="#ffcf4a"/>'
                 '<rect x="180" y="380" width="70" height="40" rx="6" fill="#4ff0ff" opacity=".6"/>')
        palm = ('<path d="M120 444C112 360 118 280 146 196" fill="none" stroke="#6b3e16" stroke-width="18" stroke-linecap="round"/>'
                + "".join(f'<path d="M146 196Q{146 + dx * .5} {196 + dy - 30} {146 + dx} {196 + dy}" fill="none" stroke="#1fbf8a" stroke-width="22" stroke-linecap="round"/>'
                          f'<path d="M146 196Q{146 + dx * .5} {196 + dy - 30} {146 + dx} {196 + dy}" fill="none" stroke="#0e8a62" stroke-width="4" stroke-linecap="round"/>'
                          for dx, dy in ((96, 30), (-90, 40), (70, -50), (-70, -46), (6, -80), (110, 80), (-100, 96)))
                + '<circle cx="146" cy="200" r="14" fill="#6b3e16"/>')
        ground = '<path d="M60 444H460" stroke="#ff4fd8" stroke-width="8" stroke-linecap="round" filter="url(#softglow)"/>'
        return scene(sun + villa + palm + ground, shadow=False,
                     defs=lin("sunset", [(0, "#ffcf4a"), (.5, "#ff8a3d"), (1, "#f0478c")]))

    @classmethod
    def fav(cls, place, i):
        """A neon sign: a glowing tube frame around the symbol on a dark backing."""
        c = cls.neon[i]
        sign = ('<rect x="80" y="96" width="352" height="320" rx="40" fill="#14081f"/>'
                '<rect x="80" y="96" width="352" height="320" rx="40" fill="none" stroke="#3a1f55" stroke-width="8"/>'
                f'<rect x="108" y="124" width="296" height="264" rx="28" fill="none" stroke="{c}" stroke-width="8" filter="url(#neon)"/>'
                f'<rect x="108" y="124" width="296" height="264" rx="28" fill="none" stroke="#fff" stroke-width="2.5" opacity=".8"/>'
                '<path d="M180 96V60M332 96V60" stroke="#8c8c98" stroke-width="5"/><circle cx="180" cy="56" r="7" fill="#8c8c98"/><circle cx="332" cy="56" r="7" fill="#8c8c98"/>')
        return scene(sign, top=sym(place, 256, 256, 160, c, "neon") + sym(place, 256, 256, 160, "#fff", mid="pm2", opacity=.6))


# ================================================================ Neon Arcade

class Neon:
    tokens = [("#ffd23f", "#b8860b"), ("#d0d6de", "#7d8790"), ("#ff8a3d", "#a8501a"), ("#7df7ff", "#1a7f9f"),
              ("#ff5fd8", "#a01f88"), ("#8cff5a", "#3f9a1a"), ("#c78bff", "#6a2fb8")]

    @staticmethod
    def boot():
        """A retro game console with a cartridge slotted in and two pads."""
        console = ('<rect x="96" y="210" width="320" height="150" rx="22" fill="url(#body)"/>'
                   '<rect x="96" y="320" width="320" height="40" rx="0" fill="#2b2f45" opacity=".5"/>'
                   '<rect x="176" y="150" width="160" height="90" rx="8" fill="#3a3f58"/>'
                   '<rect x="196" y="120" width="120" height="80" rx="6" fill="#8c8c98"/><rect x="210" y="132" width="92" height="50" rx="4" fill="#ff4fd8"/>'
                   f'<text x="256" y="164" {MONO} font-size="18" text-anchor="middle" fill="#fff">GAME</text>'
                   '<rect x="120" y="276" width="70" height="20" rx="10" fill="#e23b3b"/><rect x="322" y="276" width="70" height="20" rx="10" fill="#3a3f58"/>'
                   '<path d="M110 236H402" stroke="#ff4fd8" stroke-width="5" filter="url(#softglow)"/>')
        def pad(x, rot):
            return (f'<g transform="rotate({rot} {x + 60} 420)"><rect x="{x}" y="390" width="120" height="60" rx="30" fill="#2b2f45"/>'
                    f'<path d="M{x + 24} 420H{x + 52}M{x + 38} 406V434" stroke="#8c8c98" stroke-width="9" stroke-linecap="round"/>'
                    f'<circle cx="{x + 82}" cy="414" r="8" fill="#ffd23f"/><circle cx="{x + 100}" cy="426" r="8" fill="#3ddc84"/></g>')
        cables = '<path d="M150 360C150 380 120 380 112 400M362 360C362 380 392 380 400 400" fill="none" stroke="#2b2f45" stroke-width="6"/>'
        return scene(console + cables + pad(56, -8) + pad(336, 8), defs=lin("body", [(0, "#d0d6de"), (1, "#8c94a0")]))

    @staticmethod
    def external():
        """A chunky game cartridge with a neon label."""
        cart = ('<path d="M116 60H396V400L376 452H136L116 400Z" fill="url(#cart)"/>'
                + "".join(f'<path d="M136 {y}H376" stroke="#5a6070" stroke-width="5" stroke-linecap="round" opacity=".7"/>' for y in (82, 98, 114))
                + '<rect x="146" y="140" width="220" height="200" rx="10" fill="#0b0d18"/>'
                '<rect x="146" y="140" width="220" height="200" rx="10" fill="none" stroke="#ff4fd8" stroke-width="5" filter="url(#softglow)"/>'
                '<path d="M170 300 230 220 270 270 300 240 344 300Z" fill="#4ff0ff" opacity=".9"/>'
                '<circle cx="306" cy="190" r="24" fill="#ffd23f"/>'
                f'<text x="256" y="328" {MONO} font-size="18" text-anchor="middle" fill="#ff4fd8" letter-spacing="4">LEVEL 1</text>'
                '<path d="M226 400H286L276 430H236Z" fill="#5a6070"/>')
        return scene(cart, defs=lin("cart", [(0, "#a8afbb"), (1, "#6b7280")]))

    @staticmethod
    def network():
        """An arcade joystick broadcasting neon waves."""
        stick = ('<path d="M120 360H392L420 448H92Z" fill="#232842"/><rect x="92" y="430" width="328" height="22" rx="6" fill="#151a2e"/>'
                 '<path d="M120 360H392" stroke="#ff4fd8" stroke-width="6" filter="url(#softglow)"/>'
                 '<ellipse cx="220" cy="372" rx="50" ry="14" fill="#151a2e"/><rect x="210" y="200" width="20" height="172" rx="8" fill="#c0c6d0"/>'
                 '<circle cx="220" cy="188" r="50" fill="url(#ball)"/><ellipse cx="204" cy="168" rx="16" ry="10" fill="#fff" opacity=".5"/>'
                 '<circle cx="322" cy="394" r="18" fill="#ffd23f"/><circle cx="370" cy="400" r="18" fill="#3ddc84"/>')
        waves = ('<g fill="none" stroke="#4ff0ff" stroke-width="10" stroke-linecap="round" filter="url(#neon)">'
                 '<path d="M300 140A80 80 0 0 1 300 236"/><path d="M340 100A136 136 0 0 1 340 276"/><path d="M380 62A190 190 0 0 1 380 314"/></g>')
        return scene(stick, top=waves, defs=rad("ball", [(0, "#ff7a7a"), (1, "#b31d1d")], fx=.35, fy=.3))

    @staticmethod
    def home():
        """A little arcade building with a neon marquee."""
        bldg = ('<rect x="80" y="170" width="352" height="280" fill="#232842"/>'
                '<rect x="64" y="150" width="384" height="30" fill="#151a2e"/>'
                '<rect x="110" y="70" width="292" height="80" rx="12" fill="#0b0d18"/>'
                '<rect x="110" y="70" width="292" height="80" rx="12" fill="none" stroke="#ff4fd8" stroke-width="6" filter="url(#neon)"/>'
                f'<text x="256" y="126" {MONO} font-size="44" text-anchor="middle" fill="#ffe36b" filter="url(#softglow)" letter-spacing="6">PLAY</text>'
                '<rect x="206" y="320" width="100" height="130" fill="#05060c" stroke="#4ff0ff" stroke-width="5"/><path d="M256 320V450" stroke="#4ff0ff" stroke-width="4"/>'
                + "".join(f'<rect x="{x}" y="216" width="88" height="80" rx="6" fill="#05060c" stroke="#3a3f58" stroke-width="6"/>'
                          f'<rect x="{x + 16}" y="230" width="56" height="44" fill="{c}" opacity=".85" filter="url(#softglow)"/>' for x, c in ((112, "#4ff0ff"), (312, "#ff4fd8")))
                + "".join(f'<circle cx="{x}" cy="190" r="6" fill="{c}" filter="url(#softglow)"/>' for x, c in zip(range(84, 440, 32), ["#ffd23f", "#ff4fd8", "#4ff0ff"] * 4)))
        return scene(bldg)

    @classmethod
    def fav(cls, place, i):
        """An arcade token with the symbol stamped in the middle."""
        face, edge = cls.tokens[i]
        coin = (f'<circle cx="256" cy="268" r="184" fill="{edge}"/>'
                f'<circle cx="256" cy="256" r="184" fill="url(#coin{i})"/>'
                f'<circle cx="256" cy="256" r="150" fill="none" stroke="{edge}" stroke-width="8"/>'
                + "".join(f'<rect x="252" y="80" width="8" height="18" rx="3" fill="{edge}" transform="rotate({a} 256 256)"/>' for a in range(0, 360, 15))
                + f'<text x="256" y="168" {MONO} font-size="22" text-anchor="middle" fill="{edge}" letter-spacing="6">TOKEN</text>'
                '<ellipse cx="190" cy="150" rx="50" ry="24" fill="#fff" opacity=".35" transform="rotate(-30 190 150)"/>')
        return scene(coin, top=sym(place, 256, 276, 130, edge),
                     defs=rad(f"coin{i}", [(0, "#ffffff"), (.35, face), (1, face)], fx=.35, fy=.3, r=.8))


# ================================================================ Green Phosphor CRT

class CRT:
    cards = ["#efe4c6", "#e4f0d2", "#f2e8b8", "#e6dcc8", "#dcebe0", "#efdcc0", "#e8e8d2"]

    @staticmethod
    def boot():
        """A mainframe cabinet with spinning tape reels and blinking lights."""
        cab = ('<rect x="116" y="56" width="280" height="396" rx="10" fill="url(#bz)"/>'
               '<rect x="136" y="76" width="240" height="180" rx="6" fill="#2a2a22"/>'
               + "".join(f'<circle cx="{x}" cy="166" r="56" fill="#1a1a14" stroke="#8a8a78" stroke-width="5"/>'
                         f'<circle cx="{x}" cy="166" r="14" fill="#c9c0aa"/>'
                         + "".join(f'<path d="M{x} 166 {x + 44 * math.cos(a)} {166 + 44 * math.sin(a)}" stroke="#8a8a78" stroke-width="5"/>' for a in (0, 2.1, 4.2))
                         for x in (196, 316))
               + '<path d="M196 222C230 240 282 240 316 222" fill="none" stroke="#4a4030" stroke-width="5"/>'
               '<rect x="136" y="276" width="240" height="70" rx="6" fill="#021a06"/>'
               + "".join(f'<circle cx="{x}" cy="{y}" r="6" fill="{("#35ff6a", "#1a6a2a")[(x + y) % 3 == 0]}" filter="url(#softglow)"/>' for x in range(156, 370, 24) for y in (296, 326))
               + "".join(f'<rect x="136" y="{y}" width="240" height="12" rx="3" fill="#b5ac96"/>' for y in (366, 390, 414)))
        return scene(cab, defs=lin("bz", [(0, "#e8e0cc"), (1, "#c2b89e")], x2=1, y2=0))

    @staticmethod
    def external():
        """A 5.25-inch floppy disk in its black sleeve."""
        disk = ('<rect x="76" y="76" width="360" height="360" rx="10" fill="#1d1d1a"/>'
                '<rect x="76" y="76" width="360" height="360" rx="10" fill="none" stroke="#3a3a34" stroke-width="5"/>'
                '<circle cx="256" cy="256" r="60" fill="#3a2c1a"/><circle cx="256" cy="256" r="30" fill="#1d1d1a" stroke="#8a7a5a" stroke-width="5"/>'
                '<rect x="232" y="336" width="48" height="96" rx="20" fill="#3a2c1a"/>'
                '<circle cx="190" cy="250" r="8" fill="#3a2c1a"/>'
                '<rect x="100" y="96" width="312" height="92" rx="4" fill="#efe4c6"/>'
                + "".join(f'<path d="M116 {y}H396" stroke="#b5ac96" stroke-width="2"/>' for y in (124, 148, 172))
                + f'<text x="120" y="142" {MONO} font-size="22" fill="#1a6a2a">BOOT.SYS</text>'
                '<path d="M400 96V60L436 96Z" fill="#c2b89e"/><rect x="420" y="140" width="16" height="40" fill="#efe4c6"/>')
        return scene(disk)

    @staticmethod
    def network():
        """An acoustic-coupler modem with a phone handset resting in its cups."""
        modem = ('<rect x="76" y="230" width="360" height="190" rx="18" fill="url(#bz)"/>'
                 '<rect x="96" y="380" width="320" height="24" rx="6" fill="#021a06"/>'
                 + "".join(f'<circle cx="{x}" cy="392" r="6" fill="#35ff6a" filter="url(#softglow)"/>' for x in (120, 150, 180, 210))
                 + f'<text x="380" y="398" {MONO} font-size="14" text-anchor="end" fill="#35ff6a">300 BAUD</text>'
                 + "".join(f'<circle cx="{x}" cy="290" r="54" fill="#2a2a22"/><circle cx="{x}" cy="290" r="40" fill="#141410"/>' for x in (156, 356)))
        handset = ('<path d="M100 240C100 170 150 150 200 150H312C362 150 412 170 412 240" fill="none" stroke="#2a2a22" stroke-width="44" stroke-linecap="round"/>'
                   '<path d="M108 232C110 182 150 166 200 166H312C362 166 402 182 404 232" fill="none" stroke="#4a4a3e" stroke-width="10" stroke-linecap="round"/>')
        waves = ('<g transform="translate(0 36)" fill="none" stroke="#35ff6a" stroke-width="8" stroke-linecap="round" filter="url(#glow)">'
                 '<path d="M226 104A40 40 0 0 1 286 104"/><path d="M200 74A80 80 0 0 1 312 74"/><path d="M174 44A120 120 0 0 1 338 44"/></g>')
        return scene(modem + handset, top=waves, defs=lin("bz", [(0, "#e8e0cc"), (1, "#c2b89e")]))

    @staticmethod
    def home():
        """A beige home computer with the house glowing on its screen."""
        comp = ('<rect x="112" y="76" width="288" height="236" rx="24" fill="url(#bz)"/>'
                '<rect x="136" y="98" width="240" height="176" rx="26" fill="#021a06"/>'
                '<rect x="136" y="98" width="240" height="176" rx="26" fill="url(#sl)"/>'
                '<path d="M200 312H312L324 340H188Z" fill="#c2b89e"/>'
                '<path d="M76 360H436L460 440H52Z" fill="url(#bz)"/>'
                + "".join(f'<rect x="{x}" y="{y}" width="26" height="16" rx="3" fill="#b5ac96"/>' for y in (372, 396) for x in range(88 + (y - 372) // 2, 420, 32))
                + '<rect x="150" y="418" width="212" height="14" rx="3" fill="#b5ac96"/>'
                '<circle cx="384" cy="292" r="5" fill="#35ff6a"/>')
        txt = f'<text x="160" y="258" {MONO} font-size="18" fill="#35ff6a" filter="url(#softglow)">C:\\HOME&gt;_</text>'
        return scene(comp, top=sym("house", 256, 176, 104, "#35ff6a", "glow") + txt,
                     defs=lin("bz", [(0, "#e8e0cc"), (1, "#c2b89e")])
                     + '<pattern id="sl" width="5" height="5" patternUnits="userSpaceOnUse"><rect width="5" height="2" fill="#35ff6a" opacity=".1"/></pattern>')

    @classmethod
    def fav(cls, place, i):
        """A punched card with the symbol printed on it."""
        c = cls.cards[i]
        card = (f'<path d="M106 96H436V416H76V126Z" fill="{c}" stroke="#b5ac96" stroke-width="4" transform="rotate(-6 256 256)"/>'
                f'<g transform="rotate(-6 256 256)">'
                + "".join(f'<path d="M{x} 120V400" stroke="#d8cdb0" stroke-width="1.5"/>' for x in range(110, 432, 22))
                + "".join(f'<rect x="{x}" y="{y}" width="8" height="16" fill="#1a1a14"/>' for x, y in
                          ((114, 140), (136, 180), (158, 380), (180, 140), (202, 360), (334, 150), (356, 380), (378, 170), (400, 350), (422, 140), (114, 380), (400, 140)))
                + f'<text x="128" y="118" {MONO} font-size="16" fill="#1a6a2a">0101 1100 0110 1001</text></g>')
        return scene(card, top=sym(place, 256, 262, 150, "#1a6a2a", rot=-6))


# ================================================================ 8-Bit Pixel (pixelated after rendering)

class Pixel:
    gems = [("#4fc3ff", "#1a5f9f"), ("#ff5f5f", "#9f1a1a"), ("#5fff7a", "#1a8f2a"), ("#ffd23f", "#9f7a0a"),
            ("#d07aff", "#6a2a9f"), ("#ff9a3d", "#9f4a0a"), ("#7affea", "#1a8f7a")]
    INK = "#2b1600"

    @classmethod
    def boot(cls):
        """A treasure chest bursting with gold."""
        o = f'stroke="{cls.INK}" stroke-width="14" stroke-linejoin="miter"'
        chest = (f'<rect x="96" y="232" width="320" height="200" fill="#a8622e" {o}/>'
                 f'<path d="M96 232V176Q96 112 160 112H352Q416 112 416 176V232Z" fill="#c67a3e" {o}/>'
                 f'<rect x="96" y="220" width="320" height="28" fill="#ffd23f" {o}/>'
                 f'<rect x="226" y="236" width="60" height="70" fill="#ffd23f" {o}/><rect x="248" y="262" width="16" height="24" fill="{cls.INK}"/>'
                 f'<path d="M160 112V432M352 112V432" stroke="{cls.INK}" stroke-width="10"/>'
                 '<rect x="110" y="300" width="290" height="16" fill="#8a4a1c"/>')
        coins = "".join(f'<rect x="{x}" y="{y}" width="40" height="40" fill="#ffd23f" stroke="{cls.INK}" stroke-width="10"/>' for x, y in ((60, 396), (412, 400), (420, 350)))
        shine = sparkle(256, 72, 30, "#fff6a0") + sparkle(420, 100, 20, "#fff6a0")
        return scene(chest + coins, top=shine, shadow=False)

    @classmethod
    def external(cls):
        """A potion bottle with a cork."""
        o = f'stroke="{cls.INK}" stroke-width="14"'
        bottle = (f'<rect x="216" y="64" width="80" height="60" fill="#c67a3e" {o}/>'
                  f'<path d="M206 124H306V200L384 270V420H128V270L206 200Z" fill="#e6f2ff" {o}/>'
                  '<path d="M140 290H372V408H140Z" fill="#ff4fd8"/>'
                  '<rect x="140" y="290" width="232" height="24" fill="#ff9ae8"/>'
                  '<rect x="170" y="330" width="28" height="28" fill="#fff"/><rect x="310" y="350" width="20" height="20" fill="#fff"/>'
                  '<rect x="160" y="224" width="24" height="48" fill="#fff"/>')
        return scene(bottle, shadow=False)

    @classmethod
    def network(cls):
        """A swirling portal ring."""
        portal = (f'<ellipse cx="256" cy="256" rx="170" ry="196" fill="#5a1f9f" stroke="{cls.INK}" stroke-width="16"/>'
                  '<ellipse cx="256" cy="256" rx="130" ry="152" fill="#8a3de0"/>'
                  '<ellipse cx="256" cy="256" rx="90" ry="108" fill="#c78bff"/>'
                  '<ellipse cx="256" cy="256" rx="50" ry="62" fill="#f0d8ff"/>'
                  + "".join(f'<rect x="{x}" y="{y}" width="24" height="24" fill="#fff"/>' for x, y in ((64, 96), (420, 140), (430, 380), (70, 400), (250, 40)))
                  + "".join(f'<rect x="{256 + 150 * math.cos(a)}" y="{256 + 172 * math.sin(a)}" width="20" height="20" fill="#4ff0ff"/>' for a in (0.4, 1.6, 2.8, 4.0, 5.2)))
        return scene(portal, shadow=False)

    @classmethod
    def home(cls):
        """A little castle with crenellations and a flag."""
        o = f'stroke="{cls.INK}" stroke-width="14"'
        castle = (f'<path d="M80 448V200H120V170H160V200H200V170H240V200H272V170H312V200H352V170H392V200H432V448Z" fill="#b8bcc8" {o}/>'
                  f'<path d="M196 448V340Q196 290 256 290Q316 290 316 340V448Z" fill="#6b3e16" {o}/>'
                  f'<rect x="120" y="250" width="44" height="56" fill="{cls.INK}"/><rect x="348" y="250" width="44" height="56" fill="{cls.INK}"/>'
                  + "".join(f'<rect x="{x}" y="{y}" width="40" height="20" fill="#8c90a0"/>' for x, y in ((100, 360), (360, 390), (130, 410), (370, 330)))
                  + f'<path d="M256 170V60" stroke="{cls.INK}" stroke-width="10"/><path d="M262 64H350L326 92 350 120H262Z" fill="#e23b3b" {o}/>'
                  '<rect x="236" y="380" width="14" height="14" fill="#ffd23f"/>')
        return scene(castle, shadow=False)

    @classmethod
    def fav(cls, place, i):
        """A cut gem with the symbol on its face."""
        light, dark = cls.gems[i]
        gem = (f'<path d="M150 80H362L456 196 256 448 56 196Z" fill="{dark}" stroke="{cls.INK}" stroke-width="14" stroke-linejoin="round"/>'
               f'<path d="M150 80H362L400 196H112Z" fill="{light}"/>'
               f'<path d="M112 196H400L256 420Z" fill="{light}" opacity=".7"/>'
               '<rect x="160" y="100" width="40" height="30" fill="#fff"/>')
        return scene(gem, top=sym(place, 256, 250, 150, cls.INK), shadow=False)


# ================================================================ Platinum Classic

class Platinum:
    stripes = ["#5a5ac8", "#c85a5a", "#5aa85a", "#c8a03a", "#8a5ac8", "#3a9ab8", "#c87a3a"]
    LINE = 'stroke="#15152b" stroke-width="4"'

    @classmethod
    def bevel(cls, x, y, w, h, fill="#dcdcdc"):
        return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" {cls.LINE}/>'
                f'<path d="M{x + 4} {y + h - 4}V{y + 4}H{x + w - 4}" fill="none" stroke="#fff" stroke-width="5"/>'
                f'<path d="M{x + w - 4} {y + 6}V{y + h - 4}H{x + 6}" fill="none" stroke="#8e8e9e" stroke-width="5"/>')

    @classmethod
    def boot(cls):
        """A bevelled internal hard disk, seen from the front."""
        disk = (cls.bevel(76, 176, 360, 170)
                + '<rect x="100" y="200" width="200" height="22" fill="#b4b4c0" stroke="#15152b" stroke-width="2"/>'
                + "".join(f'<path d="M{x} 260V320" stroke="#8e8e9e" stroke-width="5"/>' for x in range(104, 300, 14))
                + '<rect x="360" y="296" width="44" height="18" fill="#3ddc84" stroke="#15152b" stroke-width="3"/>'
                + cls.bevel(96, 346, 320, 40, "#c4c4cc")
                + "".join(f'<rect x="{x}" y="356" width="12" height="20" fill="#a8a8b4"/>' for x in range(120, 400, 24)))
        return scene(disk, shadow=False)

    @classmethod
    def external(cls):
        """A removable cartridge disk with a sliding shutter."""
        cart = (f'<path d="M96 96H396L416 116V416H96Z" fill="#4a5adc" {cls.LINE}/>'
                '<path d="M100 412V100H392" fill="none" stroke="#8a9aff" stroke-width="5"/>'
                + cls.bevel(166, 96, 180, 120, "#c4c4cc")
                + '<rect x="230" y="116" width="52" height="80" fill="#4a4a58"/>'
                + cls.bevel(136, 260, 240, 130, "#f4f4f4")
                + "".join(f'<path d="M156 {y}H356" stroke="#b4b4c0" stroke-width="3"/>' for y in (300, 330, 360)))
        return scene(cart, shadow=False)

    @classmethod
    def network(cls):
        """A globe on a bevelled stand, with a network cable."""
        stand = cls.bevel(166, 400, 180, 40, "#c4c4cc") + '<rect x="240" y="350" width="32" height="52" fill="#a8a8b4" stroke="#15152b" stroke-width="4"/>'
        globe = ('<circle cx="256" cy="210" r="150" fill="#6a8aff" stroke="#15152b" stroke-width="5"/>'
                 '<g fill="none" stroke="#15152b" stroke-width="4"><ellipse cx="256" cy="210" rx="64" ry="150"/><path d="M106 210H406M126 140H386M126 280H386"/></g>'
                 '<path d="M180 120 220 110 240 150 206 186 220 230 180 250 160 200Z" fill="#7acb7a" stroke="#15152b" stroke-width="3"/>'
                 '<path d="M290 160 350 150 370 200 330 260 300 230Z" fill="#7acb7a" stroke="#15152b" stroke-width="3"/>'
                 '<path d="M150 150A110 110 0 0 1 220 90" fill="none" stroke="#fff" stroke-width="8" stroke-linecap="round" opacity=".7"/>')
        cable = ('<path d="M346 420C400 420 420 380 440 330" fill="none" stroke="#15152b" stroke-width="12"/>'
                 '<rect x="424" y="292" width="34" height="44" fill="#dcdcdc" stroke="#15152b" stroke-width="4"/>')
        return scene(stand + globe + cable, shadow=False)

    @classmethod
    def home(cls):
        """A little desktop computer on a desk."""
        desk = cls.bevel(56, 400, 400, 30, "#c8a878") + '<path d="M80 430V460M432 430V460" stroke="#15152b" stroke-width="10"/>'
        comp = (cls.bevel(136, 96, 240, 216)
                + '<rect x="164" y="120" width="184" height="140" fill="#24244f" stroke="#15152b" stroke-width="3"/>'
                '<rect x="176" y="130" width="160" height="120" fill="#7a8ad8"/>'
                + cls.bevel(116, 312, 280, 70, "#d0d0d8")
                + '<rect x="146" y="336" width="120" height="10" fill="#8e8e9e"/><rect x="330" y="334" width="40" height="14" fill="#3ddc84" stroke="#15152b" stroke-width="2"/>')
        return scene(desk + comp, top=sym("house", 256, 190, 88, "#fff"), shadow=False)

    @classmethod
    def fav(cls, place, i):
        """A bevelled round button with a coloured ring."""
        c = cls.stripes[i]
        btn = ('<circle cx="256" cy="256" r="190" fill="#c4c4cc" stroke="#15152b" stroke-width="5"/>'
               '<path d="M122 390A190 190 0 0 1 390 122" fill="none" stroke="#fff" stroke-width="8"/>'
               '<path d="M390 122A190 190 0 0 1 122 390" fill="none" stroke="#8e8e9e" stroke-width="8"/>'
               f'<circle cx="256" cy="256" r="150" fill="#dcdcdc" stroke="{c}" stroke-width="14"/>'
               '<circle cx="256" cy="256" r="142" fill="none" stroke="#15152b" stroke-width="3"/>')
        return scene(btn, top=sym(place, 256, 256, 150, "#24244f"), shadow=False)


# ================================================================ Nineties Desktop

class Nineties:
    labels = ["#00a0a0", "#c00000", "#008000", "#000080", "#808000", "#800080", "#c06000"]

    @staticmethod
    def boot():
        """A beige tower PC with drive bays and a power button."""
        tower = ('<rect x="160" y="56" width="200" height="400" fill="#000" opacity=".35" transform="translate(16 12)"/>'
                 '<rect x="160" y="56" width="200" height="400" fill="#d4ccb4" stroke="#000" stroke-width="4"/>'
                 '<path d="M164 452V60H356" fill="none" stroke="#fff" stroke-width="4"/>'
                 + "".join(f'<rect x="184" y="{y}" width="152" height="40" fill="#c0b8a0" stroke="#000" stroke-width="3"/>'
                           f'<rect x="200" y="{y + 16}" width="100" height="8" fill="#000"/>' for y in (86, 136))
                 + '<rect x="184" y="196" width="152" height="40" fill="#c0b8a0" stroke="#000" stroke-width="3"/><rect x="230" y="212" width="60" height="8" fill="#000"/>'
                 '<circle cx="216" cy="300" r="20" fill="#c0b8a0" stroke="#000" stroke-width="4"/><path d="M216 290V302" stroke="#000" stroke-width="4"/>'
                 '<rect x="270" y="294" width="16" height="10" fill="#00e000"/><rect x="300" y="294" width="16" height="10" fill="#e0a000"/>'
                 + "".join(f'<path d="M184 {y}H336" stroke="#a8a088" stroke-width="4"/>' for y in range(350, 440, 14)))
        return scene(tower, shadow=False)

    @classmethod
    def external(cls):
        """A 3.5-inch floppy disk."""
        disk = ('<path d="M92 76H396L436 116V436H92Z" fill="#000" opacity=".35" transform="translate(14 12)"/>'
                '<path d="M92 76H396L436 116V436H92Z" fill="#303038" stroke="#000" stroke-width="4"/>'
                '<rect x="168" y="76" width="176" height="120" fill="#c0c0c8" stroke="#000" stroke-width="3"/>'
                '<rect x="282" y="92" width="40" height="88" fill="#303038"/>'
                '<rect x="132" y="250" width="264" height="186" fill="#f4f4f4" stroke="#000" stroke-width="3"/>'
                '<rect x="132" y="250" width="264" height="30" fill="#00a0a0"/>'
                + "".join(f'<path d="M150 {y}H378" stroke="#b0b0b8" stroke-width="3"/>' for y in (316, 350, 384, 418))
                + '<rect x="108" y="404" width="16" height="20" fill="#000"/>')
        return scene(disk, shadow=False)

    @staticmethod
    def network():
        """A globe with a phone cord: going online over dial-up."""
        globe = ('<circle cx="270" cy="232" r="150" fill="#000" opacity=".35" transform="translate(12 12)"/>'
                 '<circle cx="256" cy="220" r="150" fill="#0080c0" stroke="#000" stroke-width="4"/>'
                 '<g fill="none" stroke="#000" stroke-width="3"><ellipse cx="256" cy="220" rx="60" ry="150"/><path d="M106 220H406M126 150H386M126 290H386"/></g>'
                 '<path d="M176 120 230 110 246 160 206 196 226 250 176 260 156 200Z" fill="#00c000" stroke="#000" stroke-width="3"/>'
                 '<path d="M296 170 350 160 372 220 330 280 300 240Z" fill="#00c000" stroke="#000" stroke-width="3"/>')
        phone = ('<path d="M120 420C150 380 180 450 220 410C250 380 280 440 310 400" fill="none" stroke="#000" stroke-width="6"/>'
                 '<rect x="300" y="370" width="150" height="70" rx="10" fill="#d4ccb4" stroke="#000" stroke-width="4"/>'
                 '<rect x="316" y="386" width="60" height="14" fill="#000"/>'
                 + "".join(f'<rect x="{x}" y="414" width="12" height="12" fill="#00e000"/>' for x in (390, 410, 430))
                 + '<path d="M72 400C72 380 92 370 112 380L130 410C120 430 92 440 72 420Z" fill="#303038" stroke="#000" stroke-width="3"/>')
        return scene(globe + phone, shadow=False)

    @staticmethod
    def home():
        """A beige desktop PC showing a teal desktop."""
        pc = ('<rect x="112" y="60" width="288" height="236" fill="#000" opacity=".35" transform="translate(14 12)"/>'
              '<rect x="112" y="60" width="288" height="236" fill="#d4ccb4" stroke="#000" stroke-width="4"/>'
              '<rect x="140" y="84" width="232" height="168" fill="#008080" stroke="#000" stroke-width="4"/>'
              '<rect x="140" y="232" width="232" height="20" fill="#c0c0c0" stroke="#000" stroke-width="2"/><rect x="144" y="236" width="44" height="12" fill="#d4d4d4" stroke="#000" stroke-width="1.5"/>'
              '<path d="M220 296H292V320H220Z" fill="#c0b8a0" stroke="#000" stroke-width="3"/>'
              '<rect x="80" y="330" width="352" height="62" fill="#000" opacity=".35" transform="translate(10 10)"/>'
              '<rect x="80" y="330" width="352" height="62" fill="#d4ccb4" stroke="#000" stroke-width="4"/>'
              + "".join(f'<rect x="{x}" y="{y}" width="20" height="14" fill="#c0b8a0" stroke="#000" stroke-width="1.5"/>' for y in (340, 362) for x in range(92, 420, 26))
              + '<rect x="378" y="268" width="10" height="10" fill="#00e000"/>'
              '<rect x="420" y="400" width="44" height="60" rx="20" fill="#d4ccb4" stroke="#000" stroke-width="4"/>')
        return scene(pc, top=sym("house", 256, 160, 90, "#fff"), shadow=False)

    @classmethod
    def fav(cls, place, i):
        """A shiny CD-ROM with the symbol on its printed label."""
        c = cls.labels[i]
        cd = ('<circle cx="270" cy="270" r="196" fill="#000" opacity=".35"/>'
              '<circle cx="256" cy="256" r="196" fill="url(#rainbow)" stroke="#000" stroke-width="4"/>'
              f'<path d="M256 106A150 150 0 1 1 255.9 106Z" fill="{c}" stroke="#000" stroke-width="3"/>'
              '<path d="M106 256A150 150 0 0 1 406 256H300A44 44 0 0 0 212 256Z" fill="#fff" opacity=".92"/>'
              '<path d="M150 214H230M282 214H362M168 186H344" stroke="#000" stroke-width="5" opacity=".55"/>'
              '<circle cx="256" cy="256" r="40" fill="#d8d8e0" stroke="#000" stroke-width="3"/><circle cx="256" cy="256" r="18" fill="#fff" stroke="#000" stroke-width="3"/>')
        return scene(cd, top=sym(place, 256, 346, 104, "#fff"),
                     shadow=False,
                     defs='<linearGradient id="rainbow" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#e8e8f0"/><stop offset=".3" stop-color="#ffd0f0"/>'
                     '<stop offset=".45" stop-color="#d0f0ff"/><stop offset=".6" stop-color="#fff6c0"/><stop offset="1" stop-color="#b8b8c8"/></linearGradient>')


# ================================================================ Aqua Gloss

class Aqua:
    orbs = ["#2f8ff0", "#8a96a8", "#58c23a", "#9a4ad8", "#ff8a1c", "#e8405a", "#1fb8b8"]

    @staticmethod
    def gloss(cx, cy, rx, ry):
        return f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="url(#shine)"/>'

    @classmethod
    def boot(cls):
        """A glossy aluminium-and-glass drive."""
        drive = ('<rect x="76" y="150" width="360" height="230" rx="40" fill="url(#alu)" stroke="#7d8a9a" stroke-width="3"/>'
                 '<rect x="96" y="170" width="320" height="140" rx="28" fill="url(#glassb)"/>'
                 + cls.gloss(256, 196, 140, 26)
                 + '<rect x="96" y="326" width="200" height="10" rx="5" fill="#9aa6b4"/>'
                 '<circle cx="376" cy="340" r="12" fill="#5fd0ff" filter="url(#softglow)"/>'
                 '<path d="M96 380H416" stroke="#5c6878" stroke-width="6" stroke-linecap="round"/>')
        return scene(drive, defs=lin("alu", [(0, "#f4f7fa"), (1, "#a8b4c2")]) + lin("glassb", [(0, "#8ec8ff"), (1, "#1f6fd1")])
                     + SHINE)

    @classmethod
    def external(cls):
        """A translucent gel thumb drive."""
        stick = ('<g transform="rotate(-30 256 256)">'
                 '<rect x="200" y="48" width="112" height="100" rx="6" fill="url(#metal)" stroke="#7d8a9a" stroke-width="3"/>'
                 '<rect x="224" y="74" width="22" height="22" fill="#5c6878"/><rect x="266" y="74" width="22" height="22" fill="#5c6878"/>'
                 '<rect x="168" y="140" width="176" height="300" rx="60" fill="url(#gelb)" stroke="#1a5aa8" stroke-width="3"/>'
                 '<rect x="190" y="160" width="132" height="80" rx="40" fill="#fff" opacity=".6"/>'
                 '<rect x="214" y="270" width="84" height="120" rx="10" fill="#0e3f7a" opacity=".45"/>'
                 '<circle cx="256" cy="410" r="14" fill="none" stroke="#fff" stroke-width="5" opacity=".7"/></g>')
        return scene(stick, defs=lin("metal", [(0, "#f4f7fa"), (1, "#9aa6b4")], x2=1, y2=0) + lin("gelb", [(0, "#8ec8ff"), (1, "#1f6fd1")], x2=1, y2=0))

    @classmethod
    def network(cls):
        """A glossy glass globe."""
        globe = ('<circle cx="256" cy="256" r="196" fill="url(#sea)"/>'
                 '<g fill="none" stroke="#fff" stroke-width="5" opacity=".45"><ellipse cx="256" cy="256" rx="80" ry="196"/><path d="M60 256H452M80 170H432M80 342H432"/></g>'
                 '<path d="M170 140 230 128 250 190 206 230 230 300 170 314 140 236Z" fill="#7cd46a" opacity=".9"/>'
                 '<path d="M300 200 370 186 396 260 340 340 310 290Z" fill="#7cd46a" opacity=".9"/>'
                 + cls.gloss(256, 140, 150, 80))
        return scene(globe, defs=rad("sea", [(0, "#a8e0ff"), (.6, "#2f8ff0"), (1, "#0a3f8a")], cy=.65, r=.6)
                     + SHINE)

    @classmethod
    def home(cls):
        """A house in glossy blue glass."""
        house = ('<path d="M256 56 456 236H408V440H104V236H56Z" fill="url(#gelh)" stroke="#1a5aa8" stroke-width="4" stroke-linejoin="round"/>'
                 '<path d="M256 84 412 224H100Z" fill="url(#shine)"/>'
                 '<rect x="212" y="320" width="88" height="120" rx="12" fill="#fff" opacity=".85"/>'
                 '<circle cx="284" cy="384" r="6" fill="#1f6fd1"/>'
                 '<rect x="134" y="268" width="56" height="56" rx="10" fill="#fff" opacity=".7"/><rect x="322" y="268" width="56" height="56" rx="10" fill="#fff" opacity=".7"/>')
        return scene(house, defs=lin("gelh", [(0, "#8ec8ff"), (1, "#1f6fd1")])
                     + SHINE)

    @classmethod
    def fav(cls, place, i):
        """A glossy gel orb with a white symbol."""
        c = cls.orbs[i]
        orb = (f'<circle cx="256" cy="256" r="196" fill="url(#orb{i})"/>'
               + cls.gloss(256, 150, 140, 80)
               + f'<circle cx="256" cy="256" r="196" fill="none" stroke="#000" stroke-opacity=".15" stroke-width="3"/>')
        return scene(orb, top=sym(place, 256, 276, 160, "#fff", "gshadow"),
                     defs=rad(f"orb{i}", [(0, "#ffffff"), (.35, c), (1, c)], cy=.8, r=.8)
                     + SHINE)


# ================================================================ registry

THEME_PLACES = {
    "halloween": Halloween, "winter-holiday": Winter, "thanksgiving": Thanksgiving, "valentine": Valentine,
    "harvest": Harvest, "scifi-hud": SciFi, "synthwave-84": Synthwave, "neon-arcade": Neon,
    "green-phosphor": CRT, "8-bit-pixel": Pixel, "platinum-classic": Platinum, "nineties-desktop": Nineties,
    "aqua-gloss": Aqua,
}


def build(theme_id, place):
    t = THEME_PLACES[theme_id]
    if place == "home":
        return t.home()
    if place == "boot-disk":
        return t.boot()
    if place == "external-disk":
        return t.external()
    if place == "network-disk":
        return t.network()
    return t.fav(place, FAVORITES.index(place))
