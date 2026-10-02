# -*- coding: utf-8 -*-
"""Builds assets.json: the banner character (cut out) and the ID-card portrait
used as the lanyard avatar."""
import base64, io, json
from PIL import Image, ImageDraw

import os
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
ID_SRC = os.path.join(ROOT, "ID-CARD.png")


def png_b64(img, colors):
    q = img.convert("RGBA").quantize(colors=colors, method=Image.FASTOCTREE)
    buf = io.BytesIO()
    q.save(buf, format="PNG", optimize=True)
    raw = buf.getvalue()
    return base64.b64encode(raw).decode("ascii"), len(raw)


# 1) full character for the banner ---------------------------------------
im = Image.open(os.path.join(HERE, "cut.png")).convert("RGBA")
W = 560
H = round(im.size[1] * W / im.size[0])
cb64, csz = png_b64(im.resize((W, H), Image.LANCZOS), 192)
print(f"char  {W}x{H}  png {csz:,}  b64 {len(cb64):,}")

# 2) ID-card portrait for the lanyard avatar ------------------------------
card = Image.open(ID_SRC).convert("RGB")
face = card.crop((185, 207, 1005, 1027)).resize((300, 300), Image.LANCZOS)
fb64, fsz = png_b64(face, 160)
print(f"face  300x300  png {fsz:,}  b64 {len(fb64):,}")

# visual check: the same crop behind a circular mask
chk = face.copy().convert("RGBA")
m = Image.new("L", (300, 300), 0)
ImageDraw.Draw(m).ellipse([0, 0, 299, 299], fill=255)
chk.putalpha(m)
out = Image.new("RGBA", (340, 340), (12, 12, 14, 255))
out.alpha_composite(chk, (20, 20))
out.convert("RGB").save(os.path.join(HERE, "face_check.png"))

json.dump({"char": {"w": W, "h": H, "b64": cb64},
           "face": {"w": 300, "h": 300, "b64": fb64}},
          open(os.path.join(HERE, "assets.json"), "w"))
print("assets.json written")
