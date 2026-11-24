"""Category glyphs for HyperIcon themes.

Each glyph is SVG markup in a 100x100 box, authored as a *mask*:
white (#fff) areas are painted in the theme's glyph colour, black (#000) areas are cut out.
All artwork here is original and deliberately generic (no vendor logos).
"""

W = 'fill="#fff"'
K = 'fill="#000"'
SW = 'fill="none" stroke="#fff" stroke-linecap="round" stroke-linejoin="round"'
SK = 'fill="none" stroke="#000" stroke-linecap="round" stroke-linejoin="round"'
TXT = 'font-family="Inter, Helvetica, Arial, sans-serif" font-weight="900" text-anchor="middle"'

PAGE = f'<path {W} d="M22 8H62L80 26V92H22Z"/><path {SK} stroke-width="4" d="M62 8V26H80"/>'


def _gear(teeth=8, r=30, tooth=12):
    out = [f'<circle {W} cx="50" cy="50" r="{r}"/>']
    for i in range(teeth):
        a = i * 360 / teeth
        out.append(f'<rect {W} x="{50 - tooth / 2}" y="{50 - r - 9}" width="{tooth}" height="16" rx="2" '
                   f'transform="rotate({a} 50 50)"/>')
    return "".join(out)


def _wheel():
    out = [f'<circle {SW} stroke-width="8" cx="50" cy="50" r="29"/>', f'<circle {W} cx="50" cy="50" r="9"/>']
    for i in range(8):
        out.append(f'<path {SW} stroke-width="6" d="M50 42V7" transform="rotate({i * 45} 50 50)"/>')
    return "".join(out)


GLYPHS = {
    "folder": "",
    "git": (
        f'<g {SW} stroke-width="9"><path d="M30 24V76"/><path d="M70 30c0 24-40 14-40 36"/></g>'
        f'<circle {W} cx="30" cy="20" r="12"/><circle {W} cx="30" cy="80" r="12"/><circle {W} cx="70" cy="26" r="12"/>'
        f'<circle {K} cx="30" cy="20" r="5"/><circle {K} cx="30" cy="80" r="5"/><circle {K} cx="70" cy="26" r="5"/>'
    ),
    "xcode": (
        f'<g transform="rotate(-45 50 50)"><rect {W} x="44" y="30" width="12" height="64" rx="5"/>'
        f'<path {W} d="M24 10H70Q78 10 78 18V30H24Q30 20 24 10Z"/></g>'
    ),
    "node": (
        f'<path {W} d="M50 6 88 28V72L50 94 12 72V28Z"/>'
        f'<text {TXT} {K} x="50" y="63" font-size="36">JS</text>'
    ),
    "python": (
        f'<path {SW} stroke-width="13" d="M22 80H58a14 14 0 0 0 0-28H42a14 14 0 0 1 0-28H66"/>'
        f'<circle {W} cx="72" cy="24" r="11"/><circle {K} cx="75" cy="21" r="3"/>'
    ),
    "rust": _gear() + f'<text {TXT} {K} x="50" y="63" font-size="36">R</text>',
    "go": (
        f'<text {TXT} {W} x="62" y="66" font-size="44" font-style="italic">GO</text>'
        f'<rect {W} x="4" y="36" width="18" height="6" rx="3"/><rect {W} x="0" y="48" width="18" height="6" rx="3"/>'
        f'<rect {W} x="6" y="60" width="14" height="6" rx="3"/>'
    ),
    "java": (
        f'<path {W} d="M18 46H70V64a24 24 0 0 1-24 24H42a24 24 0 0 1-24-24Z"/>'
        f'<path {SW} stroke-width="7" d="M70 52h6a10 10 0 0 1 0 20h-8"/>'
        f'<path {SW} stroke-width="6" d="M34 36c-7-8 7-12 0-22M54 36c-7-8 7-12 0-22"/>'
    ),
    "dotnet": (
        f'<rect {W} x="8" y="22" width="84" height="56" rx="14"/>'
        f'<text {TXT} {K} x="50" y="60" font-size="27">.NET</text>'
    ),
    "docker": (
        f'<path {W} d="M4 64H96L84 88H16Z"/>'
        + "".join(f'<rect {W} x="{x}" y="{y}" width="22" height="14" rx="2"/>' for y in (26, 44) for x in (15, 40, 65))
    ),
    "kubernetes": _wheel(),
    "terraform": (
        f'<path {W} d="M50 8 90 28 50 48 10 28Z"/>'
        f'<path {SW} stroke-width="8" d="M10 49 50 69 90 49M10 69 50 89 90 69"/>'
    ),
    "ci": (
        f'<path {SW} stroke-width="10" d="M17 46A34 34 0 0 1 74 26M83 54A34 34 0 0 1 26 74"/>'
        f'<path {W} d="M88 12 86 42 62 30Z"/><path {W} d="M12 88 14 58 38 70Z"/>'
    ),
    "documents": PAGE + "".join(f'<rect {K} x="32" y="{y}" width="{w}" height="6" rx="3"/>'
                                for y, w in ((42, 38), (56, 38), (70, 24))),
    "spreadsheets": (
        f'<rect {W} x="8" y="16" width="84" height="68" rx="7"/>'
        f'<path {SK} stroke-width="5" stroke-linecap="butt" d="M8 37H92M8 53H92M8 68H92M36 37V84M64 37V84"/>'
    ),
    "presentations": (
        f'<rect {W} x="8" y="10" width="84" height="56" rx="6"/>'
        f'<rect {K} x="25" y="44" width="11" height="12"/><rect {K} x="44.5" y="33" width="11" height="23"/>'
        f'<rect {K} x="64" y="22" width="11" height="34"/>'
        f'<path {SW} stroke-width="7" d="M50 66V78M30 93 50 78 70 93"/>'
    ),
    "pdf": PAGE + f'<text {TXT} {K} x="51" y="72" font-size="23">PDF</text>',
    "images": (
        f'<rect {W} x="6" y="16" width="88" height="68" rx="8"/>'
        f'<circle {K} cx="29" cy="37" r="8"/><path {K} d="M14 76 38 47 52 63 64 51 86 76Z"/>'
    ),
    "music": (
        f'<ellipse {W} cx="28" cy="76" rx="14" ry="11"/><ellipse {W} cx="70" cy="68" rx="14" ry="11"/>'
        f'<rect {W} x="35" y="22" width="7" height="54"/><rect {W} x="77" y="14" width="7" height="54"/>'
        f'<path {W} d="M35 20 84 12V28L35 36Z"/>'
    ),
    "video": (
        f'<rect {W} x="6" y="18" width="88" height="64" rx="8"/>'
        f'<path {K} d="M41 37V63L65 50Z"/>'
        + "".join(f'<rect {K} x="{x}" y="{y}" width="8" height="6" rx="1"/>' for y in (23, 71) for x in (14, 30, 46, 62, 78))
    ),
    "code": f'<path {SW} stroke-width="10" d="M32 28 10 50 32 72M68 28 90 50 68 72M58 18 42 82"/>',
    "archives": (
        f'<rect {W} x="6" y="12" width="88" height="22" rx="5"/><rect {W} x="13" y="38" width="74" height="52" rx="5"/>'
        f'<rect {K} x="36" y="50" width="28" height="10" rx="5"/>'
    ),
    "fonts": f'<text {TXT} {W} x="50" y="74" font-size="66">Aa</text>',
    "books": (
        f'<rect {W} x="10" y="14" width="20" height="76" rx="3"/><rect {W} x="35" y="24" width="20" height="66" rx="3"/>'
        f'<rect {W} x="62" y="18" width="20" height="74" rx="3" transform="rotate(12 72 55)"/>'
        f'<rect {K} x="10" y="26" width="20" height="5"/><rect {K} x="35" y="36" width="20" height="5"/>'
        f'<rect {K} x="35" y="74" width="20" height="5"/><rect {K} x="62" y="30" width="20" height="5" transform="rotate(12 72 55)"/>'
    ),
    "design": (
        f'<path {W} d="M50 6 88 26 50 46 12 26Z"/><path {W} d="M12 35 46 53V95L12 77Z"/>'
        f'<path {W} d="M54 53 88 35V77L54 95Z"/>'
    ),
    "data": (
        f'<path {W} d="M14 22V78A36 12 0 0 0 86 78V22A36 12 0 0 0 14 22Z"/>'
        f'<path {SK} stroke-width="4" d="M14 26A36 12 0 0 0 86 26M14 45A36 12 0 0 0 86 45M14 63A36 12 0 0 0 86 63"/>'
    ),
    "web": (
        f'<g {SW} stroke-width="7"><circle cx="50" cy="50" r="40"/><ellipse cx="50" cy="50" rx="17" ry="40"/>'
        f'<path d="M10 50H90M17 30H83M17 70H83"/></g>'
    ),
}

CATEGORIES = list(GLYPHS.keys())

LABELS = {
    "folder": "Generic folder", "git": "Git repository", "xcode": "Xcode / Swift project", "node": "Node.js project",
    "python": "Python project", "rust": "Rust project", "go": "Go project", "java": "Java / JVM project",
    "dotnet": ".NET project", "docker": "Docker / containers", "kubernetes": "Kubernetes / Helm",
    "terraform": "Terraform / infrastructure", "ci": "CI/CD pipeline", "documents": "Documents",
    "spreadsheets": "Spreadsheets", "presentations": "Presentations", "pdf": "PDFs", "images": "Images",
    "music": "Music", "video": "Video", "code": "Source code", "archives": "Archives", "fonts": "Fonts",
    "books": "Books", "design": "Design / 3D", "data": "Data", "web": "Web",
}

# Glyphs for places (favorite folders). Pictures, music and movies reuse the category glyphs above.
PLACE_GLYPHS = {
    "desktop": (
        f'<rect {W} x="6" y="12" width="88" height="60" rx="7"/><rect {K} x="14" y="20" width="72" height="44" rx="2"/>'
        f'<path {W} d="M20 56 38 38 50 50 62 40 80 56Z"/>'
        f'<path {W} d="M40 72H60L64 84H36Z"/><rect {W} x="24" y="84" width="52" height="9" rx="4.5"/>'
    ),
    "documents": GLYPHS["documents"],
    "downloads": (
        f'<path {W} d="M38 6H62V40H80L50 70 20 40H38Z"/>'
        f'<path {SW} stroke-width="10" d="M12 64V86H88V64"/>'
    ),
    "applications": "".join(
        f'<rect {W} x="{x}" y="{y}" width="24" height="24" rx="7"/>' for y in (8, 38, 68) for x in (8, 38, 68)
    ),
    "pictures": GLYPHS["images"],
    "music": GLYPHS["music"],
    "movies": GLYPHS["video"],
    "house": f'<path {W} d="M50 8 94 46H82V92H60V64H40V92H18V46H6Z"/>',
}

FAVORITES = ["desktop", "documents", "downloads", "applications", "pictures", "music", "movies"]
DISKS = ["boot-disk", "external-disk", "network-disk"]
PLACES = ["home"] + FAVORITES + DISKS
PLACE_LABELS = {
    "home": "Home folder", "desktop": "Desktop", "documents": "Documents", "downloads": "Downloads",
    "applications": "Applications", "pictures": "Pictures", "music": "Music", "movies": "Movies",
    "boot-disk": "Startup disk (Macintosh HD)", "external-disk": "External and USB drives", "network-disk": "Network shares",
}
