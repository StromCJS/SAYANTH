# -*- coding: utf-8 -*-
"""Font plumbing for the profile SVGs.

Two different jobs:

* Sora and JetBrains Mono are SIL OFL, so they may be subset and reshaped.
  They ride along inside each SVG as a variable-weight WOFF2 in a base64
  @font-face - which is the only thing that works once GitHub serves the
  file through <img>, where no external request is allowed.
* Clash Display is under the ITF Free Font License, which forbids subsetting
  and format conversion. So none of it is embedded: the few strings set in
  it are converted to plain vector outlines instead, which the licence
  treats as artwork rather than as font software.
"""
import io, os, base64, functools

# fontTools stamps head.modified with the current time unless this is set,
# which would make every rebuild produce a different file
os.environ.setdefault("SOURCE_DATE_EPOCH", "1609459200")
from fontTools.ttLib import TTFont
from fontTools import subset
from fontTools.varLib import instancer
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.misc.transform import Transform

F = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
if not os.path.isdir(F):
    raise SystemExit("font files missing - run tools/fetch-fonts.sh first")
MONO_TTF = os.path.join(F, "JetBrainsMono-Var.ttf")      # OFL 1.1
SANS_TTF = os.path.join(F, "Sora.ttf")                   # OFL 1.1
DISP_TTF = os.path.join(F, "ClashDisplay-Variable.ttf")  # ITF FFL - outlines only


def _num(v):
    return f"{v:.1f}".rstrip("0").rstrip(".") or "0"


def subset_b64(path, chars, wmin=300, wmax=800):
    """Variable-weight WOFF2 holding just `chars`, as base64."""
    font = TTFont(path)
    opt = subset.Options()
    opt.layout_features = ["kern", "liga", "calt", "ccmp", "locl", "rvrn"]
    opt.name_IDs = ["*"]          # keep copyright + licence strings in the file
    opt.name_legacy = True
    opt.notdef_outline = True
    opt.drop_tables += ["DSIG"]
    s = subset.Subsetter(options=opt)
    s.populate(text="".join(sorted(set(chars))))
    s.subset(font)
    # narrow the weight axis only after subsetting - the other order trips over
    # glyphs that have no gvar entry
    font = instancer.instantiateVariableFont(
        font, {"wght": (wmin, min(max(400, wmin), wmax), wmax)}, inplace=False)
    font.flavor = "woff2"
    buf = io.BytesIO()
    font.save(buf)
    return base64.b64encode(buf.getvalue()).decode("ascii"), len(buf.getvalue())


@functools.lru_cache(maxsize=None)
def _inst(path, wght):
    f = TTFont(path)
    if "fvar" in f:
        f = instancer.instantiateVariableFont(f, {"wght": wght}, inplace=False)
    return f


def advance(path, text, size, wght=400, track=0.0):
    """Natural width of `text` at `size` px, in user units."""
    f = _inst(path, wght)
    upem = f["head"].unitsPerEm
    cmap, hmtx = f.getBestCmap(), f["hmtx"]
    w = 0.0
    for ch in text:
        gn = cmap.get(ord(ch))
        w += (hmtx[gn][0] if gn else upem * 0.5) + track * upem
    return w * size / upem


def outline(path, text, wght=700, track=0.0, per_letter=False, em=100.0):
    """Vector outlines for `text`, baseline at y=0, left edge at x=0."""
    f = _inst(path, wght)
    upem = f["head"].unitsPerEm
    cmap, gs, hmtx = f.getBestCmap(), f.getGlyphSet(), f["hmtx"]
    s = em / upem
    x, items, ys, ds = 0.0, [], [], []
    for ch in text:
        gn = cmap.get(ord(ch))
        if gn is None:
            x += upem * 0.5 + track * upem
            continue
        if ch != " ":
            t = Transform(s, 0, 0, -s, x * s, 0)
            pen = SVGPathPen(gs, ntos=_num)
            gs[gn].draw(TransformPen(pen, t))
            d = pen.getCommands()
            bp = BoundsPen(gs)
            gs[gn].draw(bp)
            if d and bp.bounds:
                x0, y0, x1, y1 = bp.bounds
                ds.append(d)
                ys += [-y1 * s, -y0 * s]
                items.append({"ch": ch, "d": d,
                              "cx": round((x + (x0 + x1) / 2) * s, 2),
                              "cy": round(-(y0 + y1) / 2 * s, 2)})
        x += hmtx[gn][0] + track * upem
    out = {"w": round((x - track * upem) * s, 2),
           "top": round(min(ys), 2) if ys else 0.0,
           "bottom": round(max(ys), 2) if ys else 0.0}
    out["items" if per_letter else "d"] = items if per_letter else "".join(ds)
    return out
