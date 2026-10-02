# -*- coding: utf-8 -*-
"""Generates every animated SVG for the StromCJS GitHub profile.
SMIL + CSS only (GitHub strips <script>)."""
import json, os
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape
import fontkit as FK

HERE = os.path.dirname(os.path.abspath(__file__))
OUT  = os.path.dirname(HERE)          # repository root
A = json.load(open(os.path.join(HERE, "assets.json")))
G = None  # built on demand from Clash Display

NAME   = "SAYANTH V"
ROLE   = "WEB DEVELOPER"
HANDLE = "@StromCJS"

def e(s):            return escape(str(s))
def f(x, nd=1):      # compact number
    s = f"{x:.{nd}f}".rstrip("0").rstrip(".")
    return s if s not in ("", "-") else "0"

# ---------------------------------------------------------------- palettes
DARK = dict(
    id="d",
    bg0="#0b0b0d", bg1="#1a160c", bg2="#0e0c08", bg3="#000000",
    orbA="#f5c542", orbB="#b8860b", orbC="#ffe9a8",
    pink="#ffd76a", pink2="#ffe9a8", purple="#d4a62c", purple2="#a87c14",
    cyan="#ffe9a8", lime="#e3c87a",
    text="#f8f2e3", textDim="#cdc0a1", textFaint="#90846a",
    surf="rgba(245,197,66,.055)", surfSolid="#191509",
    stroke="rgba(245,197,66,.34)", strokeSoft="rgba(255,236,179,.12)",
    grid="rgba(245,197,66,.055)",
    cardBg="#0c0b08", cardBg2="#16130b",
    scan="#ffd76a", holo="#f7c948",
    heart="#e8bf52", spark="#fff3cf",
    shadow="rgba(0,0,0,.72)",
    neon="#ffc837", neonGlow="#ffe9a8", orbAlpha=(.44, .36, .24),
    vig="rgba(0,0,0,.62)", coreTxt="#fff8e2",
    codeKey="#ffd76a", codeTag="#e8a53a", codeAttr="#fff3cf",
    codeStr="#d9bd77", codePunc="#9b8c68", codeCom="#6e6450",
)
LIGHT = dict(
    id="l",
    bg0="#ffffff", bg1="#fdf8ec", bg2="#faf4e4", bg3="#ffffff",
    orbA="#e8b530", orbB="#c08a10", orbC="#efd89a",
    pink="#8f6805", pink2="#b8860b", purple="#1d1a12", purple2="#6b4c03",
    cyan="#8a6407", lime="#6b5a10",
    text="#15130d", textDim="#4b442f", textFaint="#7d7357",
    surf="rgba(160,120,20,.07)", surfSolid="#fdf7e8",
    stroke="rgba(150,110,15,.32)", strokeSoft="rgba(60,45,10,.14)",
    grid="rgba(150,115,25,.08)",
    cardBg="#fffdf5", cardBg2="#faf3e0",
    scan="#b8860b", holo="#a8780a",
    heart="#cfa136", spark="#bf951b",
    shadow="rgba(70,52,10,.22)",
    neon="#8a6407", neonGlow="#c99a1a", orbAlpha=(.22, .18, .14),
    vig="rgba(120,90,20,.10)", coreTxt="#5e430a",
    codeKey="#8a5a06", codeTag="#201c10", codeAttr="#6b4f0a",
    codeStr="#4d5a12", codePunc="#6b6246", codeCom="#8e8468",
)

# ------------------------------------------------------- typing helpers
def tw_values(width, n, base=0.0):
    """Discrete step values for a left-to-right typewriter reveal."""
    vals = [f(base + width * k / n) for k in range(n + 1)]
    kts  = [f(k / n, 4) for k in range(n + 1)]
    return ";".join(vals), ";".join(kts)

def tw_cycle(total, start, tdur, hold, edur, width, n, base=0.0):
    """Discrete steps for type -> hold -> backspace inside a looping cycle."""
    pts = [(0.0, base)]
    if start > 0:
        pts.append((start, base))
    for k in range(1, n + 1):
        pts.append((start + tdur * k / n, base + width * k / n))
    pts.append((start + tdur + hold, base + width))
    for k in range(n - 1, -1, -1):
        pts.append((start + tdur + hold + edur * (n - k) / n, base + width * k / n))
    pts.append((total, base))
    out, last = [], -1.0
    for t, v in pts:
        t = min(max(t, 0.0), total)
        if t < last:
            continue
        last = t
        out.append((t / total, v))
    vals = ";".join(f(v) for _, v in out)
    kts  = ";".join(f(t, 4) for t, _ in out)
    return vals, kts

# ================================================================= BANNER
BW, BH = 1280, 740
LX, LW = 56, 744                 # left column
MONO = ("'JetBrains Mono',ui-monospace,SFMono-Regular,Menlo,Consolas,"
        "DejaVu Sans Mono,Courier New,monospace")
SANS = ("Sora,'Segoe UI',-apple-system,BlinkMacSystemFont,Roboto,"
        "Helvetica Neue,Noto Sans,Arial,sans-serif")
FF = "@@FF@@"                      # @font-face block, filled in by main()


def mw(t, size, w=400):            # natural JetBrains Mono width
    return FK.advance(FK.MONO_TTF, t, size, w)


def sw(t, size, w=400):            # natural Sora width
    return FK.advance(FK.SANS_TTF, t, size, w)


def disp(txt, size, x, y, fill, wght=700, track=0.0, anchor="start", extra=""):
    """Clash Display as vector outlines - its licence rules out embedding."""
    o = FK.outline(FK.DISP_TTF, txt, wght, track)
    sc = size / 100.0
    w = o["w"] * sc
    dx = x - (w / 2 if anchor == "middle" else w if anchor == "end" else 0)
    g = (f'<g transform="translate({f(dx,2)},{f(y,2)}) scale({f(sc,5)})">'
         f'<path d="{o["d"]}" fill="{fill}"{extra}/></g>')
    return g, w

NAME_BASE = 148                  # baseline of the script name
ROLE_BASE = 206
QBOX_Y    = 220
PILL_Y    = 286
ABOUT_Y   = 412
STAT_Y    = 492
CODE_Y    = 566
CHAR_X, CHAR_Y, CHAR_H = 846, 136, 604
CHAR_W    = round(CHAR_H * A["char"]["w"] / A["char"]["h"], 1)

def banner_defs(P):
    i = P["id"]
    orbs = "".join(
        f'<radialGradient id="{i}orb{k}"><stop offset="0" stop-color="{c}" stop-opacity="{o}"/>'
        f'<stop offset="100%" stop-color="{c}" stop-opacity="0"/></radialGradient>'
        for k, (c, o) in enumerate(zip([P["orbA"], P["orbB"], P["orbC"]], P["orbAlpha"])))
    return f'''<defs>
<linearGradient id="{i}bg" x1="0" y1="0" x2="1" y2="1">
  <stop offset="0" stop-color="{P['bg0']}"/><stop offset=".45" stop-color="{P['bg1']}"/>
  <stop offset="1" stop-color="{P['bg2']}"/></linearGradient>
{orbs}
<linearGradient id="{i}name" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="648" y2="0">
  <stop offset="0" stop-color="{P['pink2']}">
    <animate attributeName="stop-color" dur="7s" repeatCount="indefinite"
      values="{P['pink2']};{P['purple2']};{P['purple']};{P['pink2']}"/></stop>
  <stop offset=".5" stop-color="{P['pink']}">
    <animate attributeName="stop-color" dur="7s" repeatCount="indefinite"
      values="{P['pink']};{P['purple2']};{P['purple']};{P['pink']}"/></stop>
  <stop offset="1" stop-color="{P['purple']}">
    <animate attributeName="stop-color" dur="7s" repeatCount="indefinite"
      values="{P['purple']};{P['pink']};{P['purple2']};{P['purple']}"/></stop>
</linearGradient>
<linearGradient id="{i}acc" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="{P['pink2']}"/><stop offset="1" stop-color="{P['purple']}"/></linearGradient>
<linearGradient id="{i}bar" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="{P['pink2']}"/><stop offset=".5" stop-color="{P['purple']}"/>
  <stop offset="1" stop-color="{P['cyan']}"/></linearGradient>
<linearGradient id="{i}card" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="{P['cardBg2']}"/><stop offset="1" stop-color="{P['cardBg']}"/></linearGradient>
<linearGradient id="{i}scan" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="{P['scan']}" stop-opacity="0"/>
  <stop offset=".42" stop-color="{P['scan']}" stop-opacity=".16"/>
  <stop offset=".5"  stop-color="{P['scan']}" stop-opacity=".40"/>
  <stop offset=".58" stop-color="{P['scan']}" stop-opacity=".16"/>
  <stop offset="1"  stop-color="{P['scan']}" stop-opacity="0"/></linearGradient>
<linearGradient id="{i}edge" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="{P['scan']}" stop-opacity="0"/>
  <stop offset=".25" stop-color="{P['scan']}" stop-opacity=".85"/>
  <stop offset=".5" stop-color="{P['holo']}" stop-opacity="1"/>
  <stop offset=".75" stop-color="{P['scan']}" stop-opacity=".85"/>
  <stop offset="1" stop-color="{P['scan']}" stop-opacity="0"/></linearGradient>
<linearGradient id="{i}vig" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="{P['vig']}"/><stop offset=".3" stop-color="{P['vig']}" stop-opacity="0"/>
  <stop offset=".75" stop-color="{P['vig']}" stop-opacity="0"/><stop offset="1" stop-color="{P['vig']}"/></linearGradient>
<pattern id="{i}grid" width="46" height="46" patternUnits="userSpaceOnUse">
  <path d="M46 0H0V46" fill="none" stroke="{P['grid']}" stroke-width="1"/></pattern>
<pattern id="{i}lines" width="4" height="4" patternUnits="userSpaceOnUse">
  <rect width="4" height="2" fill="{P['holo']}" opacity=".5"/></pattern>
<filter id="{i}glow" x="-45%" y="-45%" width="190%" height="190%">
  <feGaussianBlur stdDeviation="7" result="b"/>
  <feMerge><feMergeNode in="b"/><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<filter id="{i}nglow" x="-40%" y="-40%" width="180%" height="180%">
  <feGaussianBlur stdDeviation="5" result="b"/>
  <feComponentTransfer in="b" result="b2"><feFuncA type="linear" slope=".75"/></feComponentTransfer>
  <feMerge><feMergeNode in="b2"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<filter id="{i}soft" x="-60%" y="-60%" width="220%" height="220%">
  <feGaussianBlur stdDeviation="3.2" result="b"/>
  <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<filter id="{i}neon" x="-70%" y="-70%" width="240%" height="240%">
  <feGaussianBlur stdDeviation="1.6" result="b1"/><feGaussianBlur stdDeviation="7" result="b2"/>
  <feMerge><feMergeNode in="b2"/><feMergeNode in="b1"/>
  <feMergeNode in="SourceGraphic"/></feMerge></filter>
<filter id="{i}blur" x="-60%" y="-60%" width="220%" height="220%">
  <feGaussianBlur stdDeviation="9"/></filter>
<filter id="{i}drop" x="-25%" y="-25%" width="150%" height="160%">
  <feDropShadow dx="0" dy="14" stdDeviation="18" flood-color="{P['shadow']}" flood-opacity=".9"/></filter>
<clipPath id="{i}cardclip"><rect width="{BW}" height="{BH}" rx="26"/></clipPath>
<clipPath id="{i}charclip"><rect x="{CHAR_X}" y="{CHAR_Y}" width="{CHAR_W}" height="{CHAR_H}"/></clipPath>
<radialGradient id="{i}fade">
  <stop offset="0" stop-color="#fff"/><stop offset=".55" stop-color="#fff" stop-opacity=".8"/>
  <stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>
<mask id="{i}sbox"><rect x="{CHAR_X}" y="{CHAR_Y}" width="{CHAR_W}" height="{CHAR_H}"
  fill="url(#{i}fade)"/></mask>
<mask id="{i}holo">
  <rect x="{CHAR_X-10}" y="{CHAR_Y}" width="{CHAR_W+20}" height="0" fill="#fff">
    <animate attributeName="height" from="0" to="{CHAR_H}" begin=".45s" dur="1.9s"
             calcMode="spline" keySplines=".25 .1 .25 1" fill="freeze"/></rect></mask>
</defs>'''

def banner_css(P):
    return f'''<style>
  {FF}
  .mono{{font-family:{MONO}}}
  .sans{{font-family:{SANS}}}
  @keyframes blink{{0%,48%{{opacity:1}}49%,100%{{opacity:0}}}}
  .cur{{animation:blink 1.06s steps(1) infinite}}
  @keyframes orbp{{0%,100%{{transform:translate(0,0) scale(1);opacity:.75}}
                   50%{{transform:translate(18px,-22px) scale(1.18);opacity:1}}}}
  .orb{{animation:orbp 11s ease-in-out infinite}}
  @keyframes rise{{0%{{transform:translateY(0);opacity:0}}12%{{opacity:.85}}
                   88%{{opacity:.5}}100%{{transform:translateY(-340px);opacity:0}}}}
  .pt{{animation:rise 9s linear infinite}}
  @keyframes twk{{0%,100%{{transform:scale(.25) rotate(0deg);opacity:0}}
                  45%{{transform:scale(1) rotate(42deg);opacity:1}}
                  70%{{transform:scale(.6) rotate(78deg);opacity:.45}}}}
  .sp{{animation:twk 4.4s ease-in-out infinite}}
  @keyframes hrt{{0%{{transform:translateY(0) rotate(-8deg) scale(.7);opacity:0}}
                  15%{{opacity:.9}}50%{{transform:translateY(-120px) rotate(10deg) scale(1)}}
                  85%{{opacity:.55}}100%{{transform:translateY(-250px) rotate(-6deg) scale(.75);opacity:0}}}}
  .ht{{animation:hrt 8.5s ease-in-out infinite}}
  @keyframes bob{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-3.5px)}}}}
  .pill .fl{{animation:bob 4.2s ease-in-out infinite}}
  .pill .pb{{transition:fill .25s ease,stroke .25s ease}}
  .pill:hover .pb{{fill:{P['pink2']};stroke:{P['pink']};fill-opacity:.95}}
  .pill:hover .pt2{{fill:#141008}}
  .pill:hover .fl{{animation-play-state:paused;transform:translateY(-5px)}}
  @keyframes flick{{0%,4%{{opacity:0}}6%{{opacity:1}}8%{{opacity:.15}}11%{{opacity:1}}
                    13%{{opacity:.2}}15%{{opacity:.9}}17%{{opacity:.25}}20%{{opacity:1}}
                    62%{{opacity:1}}64%{{opacity:.55}}66%{{opacity:1}}100%{{opacity:1}}}}
  .neon{{animation:flick 6.5s ease-in-out infinite}}
  @keyframes hum{{0%,100%{{opacity:.5}}50%{{opacity:.95}}}}
  .hum{{animation:hum 2.6s ease-in-out infinite}}
  @keyframes shine{{0%{{transform:translateX(-340px)}}100%{{transform:translateX(900px)}}}}
  .shine{{animation:shine 5.5s cubic-bezier(.5,0,.3,1) infinite}}
  @media (prefers-reduced-motion:reduce){{
    .pt,.sp,.ht,.orb,.shine,.neon{{animation:none}} }}
</style>'''

def banner_ambient(P):
    i = P["id"]
    o = [f'<g class="orb" style="animation-delay:{d}s">'
         f'<circle cx="{x}" cy="{y}" r="{r}" fill="url(#{i}orb{k})"/></g>'
         for x, y, r, k in
         [(205, 150, 250, 0), (1075, 605, 275, 1), (660, 690, 230, 2),
          (1180, 115, 185, 0), (30, 560, 210, 1)]
         for d in [round((x + y) % 7 * .9, 1)]]
    pts = []
    for n, (x, r, dur, dly, col) in enumerate([
            (92, 2.2, 9.0, 0.0, P['pink']),    (168, 1.5, 11.5, 2.4, P['purple']),
            (255, 2.6, 8.2, 4.1, P['cyan']),   (342, 1.8, 12.4, 1.2, P['pink']),
            (430, 2.1, 9.8, 5.6, P['purple']), (515, 1.4, 10.6, 3.0, P['cyan']),
            (604, 2.4, 8.8, 6.4, P['pink']),   (690, 1.7, 12.0, 0.7, P['purple']),
            (778, 2.0, 9.4, 4.8, P['cyan']),   (862, 1.5, 11.2, 2.0, P['pink']),
            (948, 2.3, 8.6, 5.2, P['purple']), (1032, 1.6, 12.8, 1.6, P['cyan']),
            (1118, 2.2, 9.9, 3.6, P['pink']),  (1202, 1.8, 10.9, 6.0, P['purple']),
            (1252, 2.0, 8.4, 2.8, P['cyan']),  (48, 1.9, 11.8, 5.0, P['pink'])]):
        y = 720 - (n * 17) % 120
        pts.append(f'<circle class="pt" cx="{x}" cy="{y}" r="{r}" fill="{col}" opacity="0" '
                   f'style="animation-duration:{dur}s;animation-delay:{dly}s"/>')
    star = "M0-9 2.1-2.1 9 0 2.1 2.1 0 9-2.1 2.1-9 0-2.1-2.1Z"
    sps = [f'<g transform="translate({x},{y}) scale({s})">'
           f'<path class="sp" d="{star}" fill="{P["spark"]}" opacity="0" '
           f'style="animation-duration:{du}s;animation-delay:{dl}s"/></g>'
           for x, y, s, du, dl in [
               (742, 92, .9, 4.2, .3), (1246, 268, .7, 5.1, 1.7), (804, 404, .8, 4.6, 3.1),
               (34, 318, .65, 5.4, 2.2), (1262, 512, .85, 4.0, 4.4), (818, 196, .55, 6.0, .9),
               (420, 724, .7, 4.8, 3.8), (1150, 712, .75, 5.6, 1.1), (16, 92, .6, 4.4, 5.0),
               (1266, 46, .8, 5.2, 2.6)]]
    heart = ("M0 5.2C-6.4 .4-9.5-2.6-9.5-6.2c0-2.7 2.1-4.8 4.8-4.8 "
             "1.9 0 3.6 1 4.7 2.6 1.1-1.6 2.8-2.6 4.7-2.6 2.7 0 4.8 2.1 4.8 4.8 "
             "0 3.6-3.1 6.6-9.5 11.4Z")
    hs = [f'<g transform="translate({x},{y}) scale({s})">'
          f'<path class="ht" d="{heart}" fill="{P["heart"]}" opacity="0" '
          f'style="animation-duration:{du}s;animation-delay:{dl}s"/></g>'
          for x, y, s, du, dl in [
              (128, 690, 1.1, 8.5, .4), (486, 726, .85, 9.8, 3.2), (766, 700, 1.0, 8.0, 5.6),
              (1010, 734, 1.2, 10.4, 1.8), (1230, 706, .9, 9.2, 4.6),
              (300, 716, .75, 11.0, 6.8), (900, 720, .95, 8.8, 2.5)]]
    return (f'<rect width="{BW}" height="{BH}" fill="url(#{i}bg)"/>'
            f'<g filter="url(#{i}blur)">{"".join(o)}</g>'
            f'<rect width="{BW}" height="{BH}" fill="url(#{i}grid)"/>'
            + "".join(pts) + "".join(sps) + "".join(hs))

def win(total, start, dur, hold, erase):
    """Discrete 0/1 opacity window inside a looping cycle."""
    on, off = start / total, (start + dur + hold + erase + .05) / total
    return "0;1;0", f"0;{f(on,4)};{f(off,4)}"

# ---- 1. terminal prompt -------------------------------------------------
def banner_terminal(P):
    i, txt = P["id"], "cat README.md"
    n, x0, fw = len(txt), 82, 171.0
    v, k = tw_values(fw, n)
    vc, kc = tw_values(fw, n, base=x0 + 2)
    return f'''<g>
<path d="M57 29l11 8-11 8" fill="none" stroke="{P['lime']}" stroke-width="2.6"
      stroke-linecap="round" stroke-linejoin="round" opacity=".95"/>
<clipPath id="{i}cT"><rect x="{x0}" y="4" width="0" height="68">
  <animate attributeName="width" values="{v}" keyTimes="{k}" calcMode="discrete"
           begin=".15s" dur="1.05s" fill="freeze"/></rect></clipPath>
<g clip-path="url(#{i}cT)"><text class="mono" x="{x0}" y="45" font-size="21"
   fill="{P['textDim']}" textLength="{f(fw)}" lengthAdjust="spacingAndGlyphs"
   letter-spacing="0">{e(txt)}</text></g>
<rect class="cur" x="{x0+2}" y="27" width="10" height="22" fill="{P['pink']}" opacity=".9">
  <animate attributeName="x" values="{vc}" keyTimes="{kc}" calcMode="discrete"
           begin=".15s" dur="1.05s" fill="freeze"/></rect></g>'''

# ---- 2. name in vector outlines ----------------------------------------
NAME_W = 598.0
NAME_TRACK = 0.022


def name_glyphs():
    probe = FK.outline(FK.DISP_TTF, NAME, 700, NAME_TRACK)
    return FK.outline(FK.DISP_TTF, NAME, 700, NAME_TRACK, per_letter=True,
                      em=100.0 * NAME_W / probe["w"])


def banner_name(P):
    i, out = P["id"], []
    for k, g in enumerate(name_glyphs()["items"]):
        b = f"{1.15 + k * .125:.3f}s"
        out.append(
            f'<g opacity="0"><animate attributeName="opacity" values="0;1" dur=".3s" '
            f'begin="{b}" fill="freeze"/>'
            f'<g transform="translate({g["cx"]},{g["cy"]})">'
            f'<animateTransform attributeName="transform" type="scale" additive="sum" '
            f'values=".28;1.16;.97;1" keyTimes="0;.55;.8;1" dur=".62s" begin="{b}" '
            f'calcMode="spline" keySplines=".2 .9 .3 1;.4 0 .6 1;.4 0 .6 1" fill="freeze"/>'
            f'<animateTransform attributeName="transform" type="translate" additive="sum" '
            f'values="0,-30;0,0" dur=".62s" begin="{b}" calcMode="spline" '
            f'keySplines=".15 .85 .3 1" fill="freeze"/>'
            f'<g transform="translate({-g["cx"]},{-g["cy"]})">'
            f'<path d="{g["d"]}" fill="url(#{i}name)"/></g></g></g>')
    swash = ('<path d="M1 34C120 22 330 20 450 26 520 29 570 34 596 42" fill="none" '
             f'stroke="url(#{i}name)" stroke-width="3.4" stroke-linecap="round" '
             'pathLength="100" stroke-dasharray="100" stroke-dashoffset="100" opacity=".85">'
             '<animate attributeName="stroke-dashoffset" from="100" to="0" begin="2.25s" '
             'dur="1.1s" calcMode="spline" keySplines=".3 .1 .2 1" fill="freeze"/></path>')
    return (f'<g transform="translate({LX},{NAME_BASE})" filter="url(#{i}nglow)">'
            + "".join(out) + f'</g><g transform="translate({LX},{NAME_BASE})">{swash}</g>')

# ---- 3. cycling role titles --------------------------------------------
def banner_roles(P):
    i = P["id"]
    roles = ["Web Developer", "MERN Stack Developer",
             "React.js Developer", "UI / UX Enthusiast"]
    CW, TOT, SLOT = 11.4, 14.0, 3.5
    TD, HD, ED = .85, 1.95, .55
    out = [f'<path d="M58 194l9 7-9 7" fill="none" stroke="{P["pink"]}" stroke-width="2.4" '
           'stroke-linecap="round" stroke-linejoin="round" opacity=".9"/>']
    for r, txt in enumerate(roles):
        n, w, st = len(txt), len(txt) * CW, r * SLOT
        v, k = tw_cycle(TOT, st, TD, HD, ED, w, n)
        cv, ck = tw_cycle(TOT, st, TD, HD, ED, w, n, base=80)
        ov, ok = win(TOT, st, TD, HD, ED)
        out.append(f'''<clipPath id="{i}cR{r}"><rect x="78" y="170" width="0" height="62">
  <animate attributeName="width" values="{v}" keyTimes="{k}" calcMode="discrete"
           dur="{TOT}s" repeatCount="indefinite"/></rect></clipPath>
<g clip-path="url(#{i}cR{r})"><text class="mono" x="78" y="{ROLE_BASE}" font-size="19"
   font-weight="600" fill="{P['cyan']}" textLength="{f(w)}"
   lengthAdjust="spacingAndGlyphs">{e(txt)}</text></g>
<g opacity="0"><animate attributeName="opacity" values="{ov}" keyTimes="{ok}"
      calcMode="discrete" dur="{TOT}s" repeatCount="indefinite"/>
  <rect class="cur" x="80" y="190" width="9" height="20" fill="{P['pink']}">
    <animate attributeName="x" values="{cv}" keyTimes="{ck}" calcMode="discrete"
             dur="{TOT}s" repeatCount="indefinite"/></rect></g>''')
    return "".join(out)

# ---- 4. typed quote box -------------------------------------------------
def banner_quote(P):
    i = P["id"]
    s1, s2 = "Turning", "into Code & Ideas into Reality."
    FS = 17.0
    w1, w2 = sw(s1, FS), sw(s2, FS)
    x1 = 98
    xc = x1 + w1 + 10                     # coffee cup glyph (vector, not emoji)
    x2 = xc + 20 + 10
    end = x2 + w2
    total, n = end - x1 + 26, len(s1) + 1 + len(s2)
    v, k = tw_values(total, n)
    base = QBOX_Y + 33
    cup = f'''<g transform="translate({f(xc)},{base})">
  <path d="M4-15.4c-1.2 1.5.9 2.3-.3 3.8M8-16.4c-1.2 1.5.9 2.3-.3 3.8M12-15.4c-1.2 1.5.9 2.3-.3 3.8"
        fill="none" stroke="{P['textFaint']}" stroke-width="1.25" stroke-linecap="round" opacity=".85"/>
  <path d="M1-11h13v6.6A6.5 6.5 0 0 1 1-4.4Z" fill="{P['pink']}"/>
  <path d="M14.4-9.2h2.1a3.3 3.3 0 0 1 0 6.6h-2.1" fill="none" stroke="{P['pink']}"
        stroke-width="1.7"/>
  <rect x="-1.4" y="1.1" width="18" height="2.2" rx="1.1" fill="{P['purple']}"/></g>'''
    return f'''<g opacity="0"><animate attributeName="opacity" values="0;1" dur=".5s"
     begin="2.4s" fill="freeze"/>
<rect x="{LX}" y="{QBOX_Y}" width="476" height="54" rx="13" fill="{P['surf']}"
      stroke="{P['strokeSoft']}"/>
<rect x="{LX}" y="{QBOX_Y+9}" width="4" height="36" rx="2" fill="url(#{i}acc)"/>
<text class="sans" x="74" y="{base+5}" font-size="30" fill="{P['pink']}"
      opacity=".55">&#8220;</text>
<clipPath id="{i}cQ"><rect x="{x1}" y="{QBOX_Y-6}" width="0" height="70">
  <animate attributeName="width" values="{v}" keyTimes="{k}" calcMode="discrete"
           begin="2.75s" dur="2.3s" fill="freeze"/></rect></clipPath>
<g clip-path="url(#{i}cQ)">
  <text class="sans" x="{x1}" y="{base}" font-size="{FS}" font-style="italic"
        fill="{P['text']}" textLength="{f(w1)}" lengthAdjust="spacingAndGlyphs">{e(s1)}</text>
  {cup}
  <text class="sans" x="{f(x2)}" y="{base}" font-size="{FS}" font-style="italic"
        fill="{P['text']}" textLength="{f(w2)}" lengthAdjust="spacingAndGlyphs">{e(s2)}</text>
  <text class="sans" x="{f(end+4)}" y="{base+5}" font-size="30" fill="{P['purple']}"
        opacity=".55">&#8221;</text></g></g>'''

# ---- 5. tech-stack pills ------------------------------------------------
PILLS = ["HTML5", "CSS3", "JavaScript", "React.js", "React Router", "Tailwind CSS",
         "Node.js", "Express.js", "MongoDB", "Mongoose", "REST APIs", "Firebase",
         "Git", "GitHub", "Postman", "npm", "VS Code", "AWS", "Amazon S3", "Azure",
         "Google Cloud", "UI/UX", "Power BI", "Testing"]

def banner_pills(P):
    PAD, GAP, HGT, RG = 24.0, 8.0, 27.0, 35.0
    tw_ = {t: sw(t, 12.5, 600) for t in PILLS}
    rows, cur, w = [], [], 0.0
    for t in PILLS:
        pw = tw_[t] + PAD
        if cur and w + pw > LW:
            rows.append(cur); cur, w = [], 0.0
        cur.append((t, pw)); w += pw + GAP
    rows.append(cur)
    out, idx = [], 0
    for r, row in enumerate(rows):
        x, y = float(LX), PILL_Y + r * RG
        for t, pw in row:
            b = f"{2.7 + idx * .045:.3f}s"
            out.append(f'''<g class="pill" transform="translate({f(x)},{f(y)})" opacity="0">
  <animate attributeName="opacity" values="0;1" dur=".42s" begin="{b}" fill="freeze"/>
  <g class="fl" style="animation-delay:{idx*.19:.2f}s">
    <rect class="pb" width="{f(pw)}" height="{HGT}" rx="{HGT/2}" fill="{P['surf']}"
          stroke="{P['stroke']}" stroke-width="1"/>
    <text class="pt2 sans" x="{f(pw/2)}" y="{HGT/2+4.4}" font-size="12.5" font-weight="600"
          text-anchor="middle" fill="{P['textDim']}" textLength="{f(tw_[t],2)}"
          lengthAdjust="spacingAndGlyphs">{e(t)}</text></g></g>''')
            x += pw + GAP; idx += 1
    return "".join(out)

# ---- 6. about me --------------------------------------------------------
ABOUT = ["Full-stack web developer who builds clean, responsive MERN applications.",
         "At home across React, Node, Express, MongoDB, Firebase and the cloud.",
         "Currently exploring cloud computing, Power BI and basic machine learning."]

def banner_about(P):
    out = [f'<text class="mono" x="{LX}" y="{ABOUT_Y-4}" font-size="13" font-weight="700"'
           f' letter-spacing="2.4" fill="{P["pink"]}" opacity="0">'
           f'<animate attributeName="opacity" values="0;1" dur=".45s" begin="3.0s" fill="freeze"/>'
           f'// ABOUT ME</text>']
    for k, line in enumerate(ABOUT):
        y = ABOUT_Y + 22 + k * 22
        b = f"{3.15 + k * .16:.2f}s"
        out.append(f'''<g opacity="0">
  <animate attributeName="opacity" values="0;1" dur=".5s" begin="{b}" fill="freeze"/>
  <animateTransform attributeName="transform" type="translate" values="-26,0;0,0"
      dur=".62s" begin="{b}" calcMode="spline" keySplines=".2 .8 .3 1" fill="freeze"/>
  <path d="M{LX+4} {y-5}l4.6-4.6 4.6 4.6-4.6 4.6Z" fill="{P['purple']}"/>
  <text class="sans" x="{LX+22}" y="{y-1}" font-size="14.5"
        fill="{P['textDim']}">{e(line)}</text></g>''')
    return "".join(out)

# ---- 7. animated stats bar ---------------------------------------------
STATS = [("17", "PUBLIC REPOS"), ("11", "REPOS WITH CODE"),
         ("4", "LANGUAGES USED"), ("2024", "CODING SINCE")]

def banner_stats(P):
    i = P["id"]
    out = [f'''<rect x="{LX}" y="{STAT_Y}" width="{LW}" height="5" rx="2.5"
       fill="{P['surf']}" stroke="{P['strokeSoft']}" stroke-width=".6"/>
<rect x="{LX}" y="{STAT_Y}" width="0" height="5" rx="2.5" fill="url(#{i}bar)">
  <animate attributeName="width" values="0;{LW}" dur="1.5s" begin="3.3s"
           calcMode="spline" keySplines=".2 .8 .25 1" fill="freeze"/></rect>''']
    tw, gap = (LW - 3 * 8) / 4, 8
    for k, (num, lab) in enumerate(STATS):
        x = LX + k * (tw + gap)
        b = f"{3.5 + k * .14:.2f}s"
        out.append(f'''<g opacity="0">
  <animate attributeName="opacity" values="0;1" dur=".45s" begin="{b}" fill="freeze"/>
  <animateTransform attributeName="transform" type="translate" values="0,16;0,0"
      dur=".6s" begin="{b}" calcMode="spline" keySplines=".2 .8 .3 1" fill="freeze"/>
  <rect x="{f(x)}" y="{STAT_Y+12}" width="{f(tw)}" height="52" rx="12"
        fill="{P['surf']}" stroke="{P['strokeSoft']}"/>
  <text class="mono" x="{f(x+15)}" y="{STAT_Y+40}" font-size="24" font-weight="700"
        fill="{P['pink']}">{e(num)}</text>
  <text class="sans" x="{f(x+15)}" y="{STAT_Y+56}" font-size="9.5" letter-spacing="1.3"
        fill="{P['textFaint']}">{e(lab)}</text>
  <rect x="{f(x+tw-5)}" y="{STAT_Y+22}" width="3" height="0" rx="1.5" fill="url(#{i}acc)">
    <animate attributeName="height" values="0;32" dur=".7s" begin="{b}" fill="freeze"/></rect>
</g>''')
    return "".join(out)

# ---- 8. code editor card -----------------------------------------------
CODE = [
 [("const ", "codeKey"), ("buildDreams", "codeAttr"), (" = () => (", "codePunc")],
 [("  <", "codePunc"), ("Dev", "codeTag"), (" name", "codeAttr"), ("=", "codePunc"),
  ('"Sayanth V"', "codeStr"), (" role", "codeAttr"), ("=", "codePunc"),
  ('"Web Developer"', "codeStr"), (">", "codePunc")],
 [("    <", "codePunc"), ("Stack", "codeTag"), (" use", "codeAttr"), ("={[", "codePunc"),
  ('"React"', "codeStr"), (", ", "codePunc"), ('"Node"', "codeStr"), (", ", "codePunc"),
  ('"MongoDB"', "codeStr"), ("]} />", "codePunc")],
 [("    <", "codePunc"), ("Coffee", "codeTag"), (" cups", "codeAttr"), ("={", "codePunc"),
  ("Infinity", "codeStr"), ("} refill />", "codePunc")],
 [("    <", "codePunc"), ("Ship", "codeTag"), (" daily />", "codePunc"),
  ("   // keep growing", "codeCom")],
 [("  </", "codePunc"), ("Dev", "codeTag"), (">  );", "codePunc")],
]

def banner_code(P):
    i, CW, FS, LH = P["id"], 8.42, 14.0, 20.0
    H, TB = 160, 28
    top = CODE_Y
    dots = "".join(f'<circle cx="{76+k*18}" cy="{top+14}" r="5" fill="{c}" opacity=".9"/>'
                   for k, c in enumerate(["#ff5f57", "#febc2e", "#28c840"]))
    body, t = [], 3.8
    for k, segs in enumerate(CODE):
        txt = "".join(s for s, _ in segs)
        n = len(txt); w = n * CW
        y = top + TB + 22 + k * LH
        dur = max(.45, n * .022)
        v, kt = tw_values(w, n)
        tsp = "".join(f'<tspan fill="{P[c]}" xml:space="preserve">{e(s)}</tspan>'
                      for s, c in segs)
        body.append(f'''<clipPath id="{i}cC{k}"><rect x="76" y="{f(y-30)}" width="0" height="44">
  <animate attributeName="width" values="{v}" keyTimes="{kt}" calcMode="discrete"
           begin="{t:.2f}s" dur="{dur:.2f}s" fill="freeze"/></rect></clipPath>
<g clip-path="url(#{i}cC{k})"><text class="mono" x="76" y="{f(y)}" font-size="{FS}"
   fill="{P['codePunc']}" textLength="{f(w)}" lengthAdjust="spacingAndGlyphs"
   xml:space="preserve">{tsp}</text></g>''')
        t += dur + .1
        if k == len(CODE) - 1:
            body.append(f'''<g opacity="0"><animate attributeName="opacity" values="0;1"
   dur=".2s" begin="{t:.2f}s" fill="freeze"/>
 <rect class="cur" x="{f(76+w+3)}" y="{f(y-13)}" width="8" height="17"
       fill="{P['pink']}"/></g>''')
    return f'''<g opacity="0">
  <animate attributeName="opacity" values="0;1" dur=".55s" begin="3.6s" fill="freeze"/>
  <animateTransform attributeName="transform" type="translate" values="0,18;0,0" dur=".7s"
      begin="3.6s" calcMode="spline" keySplines=".2 .8 .3 1" fill="freeze"/>
  <rect x="{LX}" y="{top}" width="{LW}" height="{H}" rx="14" fill="url(#{i}card)"
        stroke="{P['stroke']}"/>
  <path d="M{LX} {top+TB}H{LX+LW}" stroke="{P['strokeSoft']}" stroke-width="1"/>
  {dots}
  <text class="mono" x="136" y="{top+18}" font-size="12"
        fill="{P['textFaint']}">buildDreams.jsx</text>
  <rect x="{LX+LW-62}" y="{top+6}" width="46" height="17" rx="8.5" fill="{P['surf']}"
        stroke="{P['strokeSoft']}"/>
  <text class="mono" x="{LX+LW-39}" y="{top+18}" font-size="9.5" text-anchor="middle"
        letter-spacing="1" fill="{P['purple']}">JSX</text>
  {"".join(body)}</g>'''

# ---- 9. neon sign -------------------------------------------------------
def banner_neon(P):
    cx = CHAR_X + CHAR_W / 2
    def tube(txt, y, size, tl):
        sc = size / 100.0
        edge, _ = disp(txt, size, cx, y, "none", track=.1, anchor="middle",
                       extra=f' stroke="{P["neon"]}" stroke-width="{f(2.1/sc,1)}"'
                             f' stroke-linejoin="round"')
        core, _ = disp(txt, size, cx, y, P["coreTxt"], track=.1, anchor="middle",
                       extra=' opacity=".95"')
        return edge + core
    return f'''<g opacity="0"><animate attributeName="opacity" values="0;1" dur=".1s"
     begin="2.1s" fill="freeze"/>
  <rect x="{f(cx-172)}" y="30" width="344" height="86" rx="16" fill="none"
        stroke="{P['strokeSoft']}" stroke-dasharray="5 7" opacity=".8"/>
  <path d="M{f(cx-132)} 30v-12M{f(cx+132)} 30v-12" stroke="{P['textFaint']}"
        stroke-width="2" opacity=".6"/>
  <circle class="hum" cx="{f(cx-132)}" cy="17" r="3" fill="{P['neon']}"/>
  <circle class="hum" cx="{f(cx+132)}" cy="17" r="3" fill="{P['neon']}"
          style="animation-delay:1.1s"/>
  <g class="neon" filter="url(#{P['id']}neon)">{tube("KEEP CODING", 70, 26, 0)}
    {tube("KEEP GROWING", 103, 26, 0)}</g></g>'''

# ---- 10. character: one-time hologram formation -------------------------
def banner_char(P):
    i = P["id"]
    hc = P["holo"]
    r, g, b = int(hc[1:3], 16) / 255, int(hc[3:5], 16) / 255, int(hc[5:7], 16) / 255
    return f'''<defs>
<image id="{i}img" x="{CHAR_X}" y="{CHAR_Y}" width="{f(CHAR_W)}" height="{CHAR_H}"
  preserveAspectRatio="xMidYMid meet"
  href="data:image/png;base64,{A['char']['b64']}"/>
<filter id="{i}tint" x="-5%" y="-5%" width="110%" height="110%" color-interpolation-filters="sRGB">
  <feColorMatrix type="matrix"
    values="0 0 0 0 {f(r,3)}  0 0 0 0 {f(g,3)}  0 0 0 0 {f(b,3)}  0 0 0 1 0"/></filter>
</defs>
<g clip-path="url(#{i}charclip)">
  <ellipse cx="{f(CHAR_X+CHAR_W/2)}" cy="{BH-26}" rx="{f(CHAR_W*.40)}" ry="22"
           fill="{P['holo']}" opacity="0" filter="url(#{i}blur)">
    <animate attributeName="opacity" values="0;.30" begin="1.6s" dur="1.2s" fill="freeze"/></ellipse>
  <g mask="url(#{i}holo)">
    <use href="#{i}img" filter="url(#{i}drop)"/>
    <g opacity=".92"><animate attributeName="opacity" values=".92;0" begin=".6s" dur="2.6s"
         calcMode="spline" keySplines=".4 0 .4 1" fill="freeze"/>
      <use href="#{i}img" filter="url(#{i}tint)"/></g>
    <g mask="url(#{i}sbox)">
      <rect x="{CHAR_X}" y="{CHAR_Y}" width="{f(CHAR_W)}" height="{CHAR_H}"
            fill="url(#{i}lines)" opacity=".40">
        <animate attributeName="opacity" values=".40;0" begin="1.4s" dur="1.6s" fill="freeze"/>
      </rect></g>
  </g>
  <rect x="{CHAR_X-14}" y="{CHAR_Y}" width="{f(CHAR_W+28)}" height="3.4"
        fill="url(#{i}edge)" filter="url(#{i}soft)">
    <animate attributeName="y" from="{CHAR_Y}" to="{CHAR_Y+CHAR_H}" begin=".45s" dur="1.9s"
             calcMode="spline" keySplines=".25 .1 .25 1" fill="freeze"/>
    <animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.06;.84;1" begin=".45s"
             dur="2.2s" fill="freeze"/></rect></g>'''

# ---- 11. continuous full-width scanner ---------------------------------
def banner_scanner(P):
    i = P["id"]
    return f'''<g clip-path="url(#{i}cardclip)"><g>
  <animateTransform attributeName="transform" type="translate" from="0 -132" to="0 {BH}"
      dur="3.5s" repeatCount="indefinite"/>
  <rect x="0" y="0" width="{BW}" height="132" fill="url(#{i}scan)"/>
  <rect x="0" y="65" width="{BW}" height="1.5" fill="url(#{i}edge)" opacity=".7"/>
</g></g>'''

# ---- assemble -----------------------------------------------------------
def banner(P):
    i = P["id"]
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {BW} {BH}"
 width="{BW}" height="{BH}" fill="none" role="img"
 aria-label="{e(NAME)} - {e(ROLE)} - animated profile banner">
<title>{e(NAME)} &#183; {e(ROLE)} &#183; {e(HANDLE)}</title>
{banner_defs(P)}{banner_css(P)}
<g clip-path="url(#{i}cardclip)">
{banner_ambient(P)}
{banner_neon(P)}
{banner_char(P)}
{banner_terminal(P)}
{banner_name(P)}
{banner_roles(P)}
{banner_quote(P)}
{banner_pills(P)}
{banner_about(P)}
{banner_stats(P)}
{banner_code(P)}
<rect width="{BW}" height="{BH}" fill="url(#{i}vig)" pointer-events="none"/>
{banner_scanner(P)}
</g>
<rect x=".75" y=".75" width="{BW-1.5}" height="{BH-1.5}" rx="25.5" fill="none"
      stroke="{P['stroke']}" stroke-width="1.5"/>
</svg>'''

# ================================================================ LANYARD
def lanyard():
    P = DARK
    AX, AY = 150, 4
    strap = "M121 0H179L162 152H138Z"
    print_txt = (NAME + "  \u2022  STROMCJS  \u2022  ") * 3
    # damped pendulum -> then an endless gentle sway
    swing = ["0", "17", "-12.5", "9", "-6.4", "4.4", "-3", "2", "-1.3", ".85", "-.5", "0"]
    sv = ";".join(f"{a} {AX} {AY}" for a in swing)
    sk = ";".join("0 .42 .58 1" for _ in range(len(swing) - 1))
    sway = ";".join(f"{a} {AX} {AY}" for a in ["0", "2.3", "0", "-2.3", "0"])
    bars, bx = [], 64.0
    widths = [1.4, 2.8, 1.4, 1.4, 3.6, 1.4, 2.1, 1.4, 1.4, 2.8, 3.6, 1.4, 2.1, 1.4,
              1.4, 3.6, 1.4, 2.8, 1.4, 2.1, 1.4, 1.4, 3.6, 2.1, 1.4, 1.4, 2.8, 1.4,
              2.1, 3.6, 1.4, 1.4, 2.1, 1.4, 2.8, 1.4]
    for k, bw in enumerate(widths):
        if bx + bw > 236:
            break
        bars.append(f'<rect x="{f(bx)}" y="376" width="{f(bw)}" height="27" fill="#ffe9a8" '
                    f'opacity="{.55 if k % 3 else .9}"/>')
        bx += bw + 1.6
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 440" width="300"
 height="440" fill="none" role="img" aria-label="{e(NAME)} swinging ID badge">
<title>{e(NAME)} &#183; {e(ROLE)} &#183; {e(HANDLE)}</title>
<defs>
<linearGradient id="Lstrap" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="#8a6a16"/><stop offset=".3" stop-color="#f5c542"/>
  <stop offset=".62" stop-color="#ffd76a"/><stop offset="1" stop-color="#a07a14"/></linearGradient>
<linearGradient id="Lmetal" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="#7a5c10"/><stop offset=".22" stop-color="#ffeab0"/>
  <stop offset=".5" stop-color="#c8921f"/><stop offset=".78" stop-color="#fff2cf"/>
  <stop offset="1" stop-color="#8a6a16"/></linearGradient>
<linearGradient id="Lcard" x1="0" y1="0" x2=".4" y2="1">
  <stop offset="0" stop-color="#16140d"/><stop offset=".55" stop-color="#0a0907"/>
  <stop offset="1" stop-color="#17130a"/></linearGradient>
<linearGradient id="Lring" x1="0" y1="0" x2="1" y2="1">
  <stop offset="0" stop-color="#ffd76a"/><stop offset=".5" stop-color="#c8921f"/>
  <stop offset="1" stop-color="#fff3cf"/></linearGradient>
<linearGradient id="Lshine" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="#fff" stop-opacity="0"/>
  <stop offset=".35" stop-color="#ffe9a8" stop-opacity=".16"/>
  <stop offset=".5" stop-color="#fff" stop-opacity=".40"/>
  <stop offset=".65" stop-color="#ffd76a" stop-opacity=".16"/>
  <stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
<filter id="Lsh" x="-40%" y="-20%" width="180%" height="150%">
  <feDropShadow dx="0" dy="10" stdDeviation="12" flood-color="#000" flood-opacity=".55"/></filter>
<filter id="Lglow" x="-60%" y="-60%" width="220%" height="220%">
  <feGaussianBlur stdDeviation="4" result="b"/>
  <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<clipPath id="Lstrapc"><path d="{strap}"/></clipPath>
<clipPath id="Lcardc"><rect x="40" y="190" width="220" height="235" rx="16"/></clipPath>
<clipPath id="Lface"><circle cx="150" cy="249" r="39"/></clipPath>
<style>
  {FF}
  .lf{{font-family:{SANS}}}
  @keyframes lsh{{0%{{transform:translateX(-230px)}}55%,100%{{transform:translateX(250px)}}}}
  .lshine{{animation:lsh 4.4s cubic-bezier(.55,0,.3,1) infinite}}
  @media (prefers-reduced-motion:reduce){{.lshine{{animation:none}}}}
</style></defs>
<g>
<animateTransform attributeName="transform" type="translate" values="0,-480;0,0"
   dur=".95s" calcMode="spline" keySplines=".3 .05 .25 1" fill="freeze"/>
<g>
<animateTransform id="Lsw" attributeName="transform" type="rotate" values="{sv}"
   keyTimes="0;.09;.19;.30;.41;.52;.63;.73;.82;.90;.96;1" dur="4.4s" begin=".55s"
   calcMode="spline" keySplines="{sk}" fill="freeze"/>
<animateTransform attributeName="transform" type="rotate" values="{sway}" dur="5.2s"
   begin="Lsw.end" repeatCount="indefinite" calcMode="spline"
   keySplines=".45 0 .55 1;.45 0 .55 1;.45 0 .55 1;.45 0 .55 1"/>
<path d="{strap}" fill="url(#Lstrap)"/>
<g clip-path="url(#Lstrapc)">
  <path d="M121 0H179L162 152H138Z" fill="none" stroke="#000000" stroke-opacity=".20"/>
  <text class="lf" transform="translate(156,6) rotate(90)" font-size="9.2" font-weight="700"
        letter-spacing="2.4" fill="#1a1405" fill-opacity=".78">{e(print_txt)}</text>
</g>
<rect x="131" y="150" width="38" height="20" rx="4" fill="url(#Lmetal)"/>
<rect x="136" y="155" width="28" height="4" rx="2" fill="#4a3a0c" opacity=".55"/>
<path d="M150 170v6" stroke="url(#Lmetal)" stroke-width="5"/>
<ellipse cx="150" cy="184" rx="11" ry="12" fill="none" stroke="url(#Lmetal)" stroke-width="4"/>
<g filter="url(#Lsh)">
  <rect x="40" y="190" width="220" height="235" rx="16" fill="url(#Lcard)"
        stroke="#f5c542" stroke-opacity=".45"/></g>
<g clip-path="url(#Lcardc)">
  <rect x="40" y="190" width="220" height="56" fill="#ffd76a" opacity=".10"/>
  <circle cx="150" cy="249" r="47" fill="none" stroke="url(#Lring)"
          stroke-width="1.4" stroke-dasharray="14 9" opacity=".75">
    <animateTransform attributeName="transform" type="rotate" from="0 150 249"
        to="360 150 249" dur="9s" repeatCount="indefinite"/></circle>
  <circle cx="150" cy="249" r="43" fill="none" stroke="url(#Lring)" stroke-width="2.6"
          filter="url(#Lglow)"/>
  <circle cx="150" cy="249" r="39.5" fill="#0a0906"/>
  <g clip-path="url(#Lface)">
    <image x="98" y="191" width="104" height="104"
      href="data:image/png;base64,{A['face']['b64']}"/></g>
  {disp(NAME, 18, 150, 321, "#fff8e6", track=.012, anchor="middle")[0]}
  {disp(ROLE, 10, 150, 339, "#f5c542", track=.26, anchor="middle")[0]}
  <text class="lf" x="150" y="356" font-size="10" text-anchor="middle"
        fill="#b5a582">{e(HANDLE)}</text>
  <path d="M62 366h176" stroke="#ffffff" stroke-opacity=".13"/>
  {"".join(bars)}
  <text class="lf" x="150" y="416" font-size="7.4" text-anchor="middle" letter-spacing="2.2"
        fill="#9b8c68">FULL&#160;STACK&#160;&#183;&#160;SINCE&#160;2024</text>
  <g class="lshine"><rect x="-10" y="180" width="54" height="256" fill="url(#Lshine)"
     transform="skewX(-22)"/></g>
</g></g></g></svg>'''

# =========================================================== STAT CARDS
# verified 2026-10-02 from api.github.com (bytes across the 11 repos with source)
LANG_BYTES = [("TypeScript", 942444, "#ffe9a8"), ("CSS", 189501, "#f5c542"),
              ("JavaScript", 133062, "#c8921f"), ("HTML", 55942, "#8a6a16")]

CARD_CSS = f'''<style>
  {FF}
  .cf{{font-family:{SANS}}} .cm{{font-family:{MONO}}}
  @keyframes csh{{0%{{transform:translateX(-260px)}}60%,100%{{transform:translateX(900px)}}}}
  .csh{{animation:csh 5s cubic-bezier(.5,0,.3,1) infinite}}
  @media (prefers-reduced-motion:reduce){{.csh{{animation:none}}}}
</style>'''

def card_defs(w, h, extra=""):
    return f'''<defs>
<linearGradient id="Cbg" x1="0" y1="0" x2=".7" y2="1">
  <stop offset="0" stop-color="#141209"/><stop offset=".55" stop-color="#0b0a07"/>
  <stop offset="1" stop-color="#1a160c"/></linearGradient>
<linearGradient id="Cacc" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="#ffd76a"/><stop offset=".5" stop-color="#c8921f"/>
  <stop offset="1" stop-color="#fff3cf"/></linearGradient>
<linearGradient id="Cshine" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="#fff" stop-opacity="0"/>
  <stop offset=".5" stop-color="#fff" stop-opacity=".13"/>
  <stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
<filter id="Cglow" x="-70%" y="-70%" width="240%" height="240%">
  <feGaussianBlur stdDeviation="3.4" result="b"/>
  <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<clipPath id="Cclip"><rect width="{w}" height="{h}" rx="16"/></clipPath>{extra}
</defs>{CARD_CSS}'''

def card_shell(w, h, title, sub):
    return f'''<rect width="{w}" height="{h}" rx="16" fill="url(#Cbg)"
      stroke="#f5c542" stroke-opacity=".30"/>
<rect x="18" y="22" width="4" height="18" rx="2" fill="url(#Cacc)"/>
{disp(title, 17, 32, 35, "#f8f2e3", track=.012)[0]}
<text class="cf" x="32" y="50" font-size="10" fill="#9b8c68">{e(sub)}</text>'''

def stats_card():
    W, H = 460, 210
    rows = [("Public repositories", "17"), ("Repos with source", "11"),
            ("Stars earned", "1"), ("Languages in use", "4"),
            ("Member since", "Oct 2024")]
    out = []
    for k, (lab, val) in enumerate(rows):
        y = 78 + k * 25
        b = f"{.35 + k * .11:.2f}s"
        out.append(f'''<g opacity="0">
  <animate attributeName="opacity" values="0;1" dur=".45s" begin="{b}" fill="freeze"/>
  <animateTransform attributeName="transform" type="translate" values="-30,0;0,0"
      dur=".6s" begin="{b}" calcMode="spline" keySplines=".2 .8 .3 1" fill="freeze"/>
  <path d="M30 {y-4}l4.4-4.4 4.4 4.4-4.4 4.4Z" fill="#c8921f"/>
  <text class="cf" x="46" y="{y}" font-size="12.5" fill="#cdc0a1">{e(lab)}</text>
  <text class="cm" x="286" y="{y}" font-size="13.5" font-weight="700" text-anchor="end"
        fill="#f5c542">{e(val)}</text></g>''')
    cx, cy, r = 372, 118, 42
    sub = HANDLE + " · local card, no rate limits"
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}"
 height="{H}" fill="none" role="img" aria-label="{e(NAME)} GitHub snapshot">
<title>{e(NAME)} &#183; GitHub snapshot</title>
{card_defs(W, H)}<g clip-path="url(#Cclip)">
{card_shell(W, H, "GitHub Snapshot", sub)}
<path d="M300 66v116" stroke="#ffffff" stroke-opacity=".10"/>
{"".join(out)}
<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#ffffff" stroke-opacity=".10"
        stroke-width="8"/>
<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="url(#Cacc)" stroke-width="8"
        stroke-linecap="round" pathLength="100" stroke-dasharray="100"
        stroke-dashoffset="100" filter="url(#Cglow)" transform="rotate(-90 {cx} {cy})">
  <animate attributeName="stroke-dashoffset" values="100;35" dur="1.5s" begin=".5s"
           calcMode="spline" keySplines=".2 .8 .25 1" fill="freeze"/></circle>
<g opacity="0"><animate attributeName="opacity" values="0;1" dur=".5s" begin="1.1s" fill="freeze"/>
  <text class="cm" x="{cx}" y="{cy+4}" font-size="27" font-weight="800" text-anchor="middle"
        fill="#f8f2e3">17</text>
  <text class="cf" x="{cx}" y="{cy+20}" font-size="8.5" letter-spacing="1.8"
        text-anchor="middle" fill="#9b8c68">REPOS</text></g>
<text class="cf" x="{cx}" y="{cy+r+22}" font-size="9.5" text-anchor="middle"
      fill="#cdc0a1">65% hold source</text>
<g class="csh"><rect x="-60" y="0" width="90" height="{H}" fill="url(#Cshine)"
   transform="skewX(-20)"/></g>
</g></svg>'''

def langs_card():
    W, H = 460, 210
    tot = sum(b for _, b, _ in LANG_BYTES)
    segs, rows, x = [], [], 24.0
    BARW = 412.0
    for k, (nm, by, col) in enumerate(LANG_BYTES):
        pct = by / tot * 100
        sw = BARW * pct / 100
        b = f"{.35 + k * .13:.2f}s"
        segs.append(f'''<rect x="{f(x)}" y="62" width="0" height="14" fill="{col}">
  <animate attributeName="width" values="0;{f(sw)}" dur="1.1s" begin="{b}"
           calcMode="spline" keySplines=".2 .8 .25 1" fill="freeze"/></rect>''')
        x += sw
        y = 104 + k * 26
        rows.append(f'''<g opacity="0">
  <animate attributeName="opacity" values="0;1" dur=".45s" begin="{b}" fill="freeze"/>
  <circle cx="30" cy="{y-4}" r="5" fill="{col}"/>
  <text class="cf" x="44" y="{y}" font-size="12.5" fill="#cdc0a1">{e(nm)}</text>
  <text class="cm" x="436" y="{y}" font-size="12" font-weight="700" text-anchor="end"
        fill="#f8f2e3">{pct:.1f}%</text>
  <rect x="150" y="{y-9}" width="240" height="6" rx="3" fill="#ffffff" fill-opacity=".08"/>
  <rect x="150" y="{y-9}" width="0" height="6" rx="3" fill="{col}">
    <animate attributeName="width" values="0;{f(240*pct/100)}" dur="1.1s" begin="{b}"
             calcMode="spline" keySplines=".2 .8 .25 1" fill="freeze"/></rect></g>''')
    bar_clip = '<clipPath id="Cbar"><rect x="24" y="62" width="412" height="14" rx="7"/></clipPath>'
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}"
 height="{H}" fill="none" role="img" aria-label="Most used languages">
<title>{e(NAME)} &#183; most used languages</title>
{card_defs(W, H, bar_clip)}<g clip-path="url(#Cclip)">
{card_shell(W, H, "Most Used Languages", "by bytes · 11 public repos with source")}
<g clip-path="url(#Cbar)"><rect x="24" y="62" width="412" height="14" fill="#ffffff"
   fill-opacity=".08"/>{"".join(segs)}</g>
{"".join(rows)}
<g class="csh"><rect x="-60" y="0" width="90" height="{H}" fill="url(#Cshine)"
   transform="skewX(-20)"/></g>
</g></svg>'''

TROPHIES = [("B", "Repositories", "17 public", "#f5c542"),
            ("C", "Stars", "1 earned", "#b8860b"),
            ("B", "Languages", "4 in use", "#f5c542"),
            ("B", "Experience", "since 2024", "#f5c542"),
            ("A", "MERN Stack", "end to end", "#ffe9a8"),
            ("A", "Cloud", "AWS/Azure/GCP", "#ffe9a8")]

def trophies_card():
    W, H = 780, 196
    CELLW, GAP = 118.0, 10.0
    x0 = (W - (len(TROPHIES) * CELLW + (len(TROPHIES) - 1) * GAP)) / 2
    cup = "M-8-13H8v6.5A8 8 0 0 1-8-6.5Z M-2 1.2h4v4.2h-4Z M-7.5 5.4h15v3.4h-15Z"
    handles = "M-8.4-11.6h-3.6a4.6 4.6 0 0 0 4.6 7.6M8.4-11.6h3.6a4.6 4.6 0 0 1-4.6 7.6"
    cells = []
    for k, (rank, title, val, col) in enumerate(TROPHIES):
        x = x0 + k * (CELLW + GAP)
        b = f"{.3 + k * .12:.2f}s"
        cells.append(f'''<g opacity="0" transform="translate({f(x+CELLW/2)},110)">
  <animate attributeName="opacity" values="0;1" dur=".4s" begin="{b}" fill="freeze"/>
  <animateTransform attributeName="transform" type="scale" additive="sum"
      values=".55;1.12;.97;1" keyTimes="0;.55;.8;1" dur=".6s" begin="{b}"
      calcMode="spline" keySplines=".2 .9 .3 1;.4 0 .6 1;.4 0 .6 1" fill="freeze"/>
  <g transform="translate({f(-CELLW/2)},-110)">
    <rect x="0" y="52" width="{f(CELLW)}" height="124" rx="13" fill="#ffffff"
          fill-opacity=".045" stroke="{col}" stroke-opacity=".38"/>
    <g transform="translate({f(CELLW/2)},96)" fill="{col}">
      <path d="{cup}"/>
      <path d="{handles}" fill="none" stroke="{col}" stroke-width="2.4"/></g>
    <text class="cm" x="{f(CELLW/2)}" y="134" font-size="21" font-weight="800"
          text-anchor="middle" fill="{col}" filter="url(#Cglow)">{e(rank)}</text>
    <text class="cf" x="{f(CELLW/2)}" y="152" font-size="10.5" font-weight="700"
          text-anchor="middle" fill="#f2ead7">{e(title)}</text>
    <text class="cf" x="{f(CELLW/2)}" y="166" font-size="8.8" text-anchor="middle"
          fill="#9b8c68">{e(val)}</text></g></g>''')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}"
 height="{H}" fill="none" role="img" aria-label="{e(NAME)} profile trophies">
<title>{e(NAME)} &#183; trophies</title>
{card_defs(W, H)}<g clip-path="url(#Cclip)">
{card_shell(W, H, "Trophies", "a local, rate-limit-free trophy shelf")}
{"".join(cells)}
<g class="csh"><rect x="-80" y="0" width="120" height="{H}" fill="url(#Cshine)"
   transform="skewX(-20)"/></g>
</g></svg>'''

# ====================================================== CONTRIBUTION ACTIVITY
# Replaces github-readme-activity-graph.vercel.app, whose deployment is dead
# (HTTP 402 DEPLOYMENT_DISABLED) - the whole point of these cards is that
# nothing here can be switched off by a third party.
ACT = json.load(open(os.path.join(HERE, "activity.json")))
LEVELS = ["#1a1710", "#5c4408", "#a87c14", "#d4a62c", "#ffd76a"]
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def _nice(iso):
    y, m, d = (int(v) for v in iso.split("-"))
    return f"{d} {MONTHS[m - 1]} {y}"


def activity_card():
    W, H = 780, 208
    CELL, PITCH = 10.0, 12.6
    GX, GY = 54.0, 84.0
    days = ACT["days"]
    cols = (len(days) + 6) // 7

    grid, labels, seen = [], [], None
    for c in range(cols):
        cells = []
        for r in range(7):
            i = c * 7 + r
            if i >= len(days):
                break
            date, lvl, n = days[i]
            x, y = GX + c * PITCH, GY + r * PITCH
            glow = ' filter="url(#Cglow)"' if lvl >= 4 else ""
            cells.append(f'<rect x="{f(x)}" y="{f(y)}" width="{CELL}" height="{CELL}"'
                         f' rx="2.4" fill="{LEVELS[lvl]}"{glow}>'
                         f'<title>{n} on {e(_nice(date))}</title></rect>')
            if r == 0:
                mo = date[5:7]
                if mo != seen:
                    seen = mo
                    labels.append((c, x, int(mo)))
        b = f"{.25 + c * .016:.3f}s"
        grid.append(f'<g opacity="0"><animate attributeName="opacity" values="0;1"'
                    f' dur=".4s" begin="{b}" fill="freeze"/>'
                    f'<animateTransform attributeName="transform" type="translate"'
                    f' values="0,7;0,0" dur=".45s" begin="{b}" calcMode="spline"'
                    f' keySplines=".2 .8 .3 1" fill="freeze"/>{"".join(cells)}</g>')

    # a month that only spans a column or two has nowhere to put its name
    # without colliding with the next one, so it goes unlabelled
    labels.append((cols, 0.0, 0))
    labels = "".join(
        f'<text class="cf" x="{f(x)}" y="76" font-size="9" fill="#9b8c68">'
        f'{MONTHS[m - 1]}</text>'
        for (c, x, m), (nxt, _, _) in zip(labels, labels[1:]) if nxt - c >= 3)

    dayname = "".join(
        f'<text class="cf" x="46" y="{f(GY + r * PITCH + 8)}" font-size="8"'
        f' text-anchor="end" fill="#6e6450">{nm}</text>'
        for r, nm in ((1, "Mon"), (3, "Wed"), (5, "Fri")))

    lx = 560.0
    legend = [f'<text class="cf" x="{f(lx)}" y="192" font-size="8.5"'
              f' fill="#6e6450">Less</text>']
    for k, col in enumerate(LEVELS):
        legend.append(f'<rect x="{f(lx + 26 + k * 13)}" y="184" width="9.5" height="9.5"'
                      f' rx="2.2" fill="{col}"/>')
    legend.append(f'<text class="cf" x="{f(lx + 26 + 5 * 13 + 4)}" y="192" font-size="8.5"'
                  f' fill="#6e6450">More</text>')

    head = f'''<g opacity="0"><animate attributeName="opacity" values="0;1" dur=".5s"
     begin=".2s" fill="freeze"/>
  <text class="cm" x="748" y="38" font-size="19" font-weight="700" text-anchor="end"
        fill="#ffd76a">{ACT["total"]}</text>
  <text class="cf" x="748" y="52" font-size="9.5" text-anchor="end"
        fill="#9b8c68">contributions &#183; {ACT["active"]} active days &#183;
        best day {ACT["best"]}</text></g>'''

    sub = f'{_nice(ACT["from"])} &#8594; {_nice(ACT["to"])} &#183; public contributions'
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}"
 height="{H}" fill="none" role="img"
 aria-label="{e(NAME)} contribution activity: {ACT['total']} contributions over the last year">
<title>{e(NAME)} &#183; {ACT['total']} contributions, {ACT['active']} active days</title>
{card_defs(W, H)}<g clip-path="url(#Cclip)">
{card_shell(W, H, "Contribution Activity", "")}
<text class="cf" x="32" y="50" font-size="10" fill="#9b8c68">{sub}</text>
{head}
{labels}
{dayname}
{"".join(grid)}
{"".join(legend)}
<g class="csh"><rect x="-80" y="0" width="120" height="{H}" fill="url(#Cshine)"
   transform="skewX(-20)"/></g>
</g></svg>'''

# ------------------------------------------------------------------ write
NOTICE = """<!--
  Sayanth V - animated GitHub profile assets.

  Type: Clash Display (headings, drawn here as vector outlines - the ITF Free
  Font License does not allow the font itself to be subset or re-packaged),
  Sora and JetBrains Mono (everything else, embedded below as subsetted
  variable WOFF2 under the SIL Open Font License 1.1).

  Copyright 2019 The Sora Project Authors - https://github.com/sora-xor/sora-font
  Copyright 2020 The JetBrains Mono Project Authors - https://github.com/JetBrains/JetBrainsMono
  SIL Open Font License 1.1 - https://openfontlicense.org
  Clash Display (c) Indian Type Foundry - https://www.fontshare.com/fonts/clash-display
-->
"""

BASE_CHARS = " 0123456789.,:;/-"


def _charsets(svg):
    """Which characters each family actually has to carry, per file."""
    root = ET.fromstring(svg)
    mono, sans = set(BASE_CHARS), set(BASE_CHARS)
    for el in root.iter():
        if el.tag.split("}")[-1] != "text":
            continue
        cls = (el.get("class") or "").split()
        bucket = mono if ("mono" in cls or "cm" in cls) else sans
        bucket.update("".join(el.itertext()))
    return mono, sans


def _fontface(mono, sans):
    out, tot = [], 0
    for fam, path, chars in (("JetBrains Mono", FK.MONO_TTF, mono),
                             ("Sora", FK.SANS_TTF, sans)):
        b64, raw = FK.subset_b64(path, chars)
        tot += len(b64)
        out.append(f"@font-face{{font-family:'{fam}';font-style:normal;"
                   f"font-weight:300 800;font-display:block;"
                   f"src:url(data:font/woff2;base64,{b64}) format('woff2')}}")
    return "".join(out), tot


def main():
    files = {"banner.svg": banner(DARK), "banner-light.svg": banner(LIGHT),
             "lanyard.svg": lanyard(), "stats.svg": stats_card(),
             "langs.svg": langs_card(), "trophies.svg": trophies_card(),
             "activity.svg": activity_card()}
    os.makedirs(OUT, exist_ok=True)
    for n, s in files.items():
        face, emb = _fontface(*_charsets(s))
        s = NOTICE + s.replace(FF, face)
        p = os.path.join(OUT, n)
        open(p, "w", encoding="utf-8", newline=chr(10)).write(s)
        print(f"{n:<20} {os.path.getsize(p):>9,} bytes   fonts {emb:>8,}")


if __name__ == "__main__":
    main()
