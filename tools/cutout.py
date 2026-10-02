# -*- coding: utf-8 -*-
"""Background cut, v3.

Pass 1-2  flood-fill the white studio background from the frame border.
Pass 3    a looser fill that eats the warm-grey floor, fenced off from the
          white sneakers by an explicit barrier.
Pass 4    deletes the leftover blobs the fill cannot reach because they are
          walled in by the chair legs, the table legs or the plant. Each one
          is picked by a seed pixel, so the shoes, the notepad, the cushion
          and the coffee cup are never touched.
"""
import os
import numpy as np
from PIL import Image, ImageFilter, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, "banner-source.webp")
OUT = HERE

im = Image.open(SRC).convert("RGB")
a = np.asarray(im).astype(np.int16)
h, w, _ = a.shape
mn = a.min(axis=2)
sat = a.max(axis=2) - mn

cand = (mn >= 228) & (sat <= 16)
cand2 = cand | ((mn >= 196) & (sat <= 40))
# the looser floor rule is confined to the band below the knees, otherwise the
# fill walks straight into the white hoodie
yy = np.arange(h)[:, None]
cand3 = cand2 | ((yy >= 1040) & (mn >= 152) & (sat <= 58))


def reconstruct(marker, mask, max_passes=40):
    cur = marker & mask
    for _ in range(max_passes):
        prev = cur.copy()
        for down in (True, False):
            rng = range(h) if down else range(h - 1, -1, -1)
            step = 1 if down else -1
            for y in rng:
                ny = y - step
                if 0 <= ny < h:
                    cur[y] |= cur[ny]
                cur[y] &= mask[y]
                m, s = mask[y], cur[y]
                if not s.any():
                    cur[y] = False
                    continue
                starts = m & ~np.concatenate(([False], m[:-1]))
                ids = np.cumsum(starts) - 1
                hit = np.zeros(int(ids[m].max()) + 1, dtype=bool)
                np.logical_or.at(hit, ids[s], True)
                cur[y] = m & hit[ids]
        if np.array_equal(prev, cur):
            break
    return cur


def label(mask):
    """4-connected component labels, via run-length union-find."""
    parent = []

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x, y):
        rx, ry = find(x), find(y)
        if rx != ry:
            parent[max(rx, ry)] = min(rx, ry)

    lab = np.zeros(mask.shape, np.int32)
    prev = []
    for y in range(mask.shape[0]):
        idx = np.flatnonzero(mask[y])
        if idx.size == 0:
            prev = []
            continue
        brk = np.flatnonzero(np.diff(idx) > 1)
        cur = []
        for s, t in zip(np.concatenate(([idx[0]], idx[brk + 1])),
                        np.concatenate((idx[brk], [idx[-1]]))):
            parent.append(len(parent))
            me = len(parent) - 1
            for ps, pt, pl in prev:
                if ps <= t and s <= pt:
                    union(me, pl)
            lab[y, s:t + 1] = me
            cur.append((s, t, me))
        prev = cur
    flat = np.zeros(len(parent) + 1, np.int32)
    flat[1:] = np.array([find(i) for i in range(len(parent))], np.int32) + 1
    return np.where(mask, flat[np.where(mask, lab + 1, 0)], 0)


seed = np.zeros((h, w), dtype=bool)
seed[0, :] = seed[-1, :] = True
seed[:, 0] = seed[:, -1] = True
bg = reconstruct(seed & cand, cand)
bg = reconstruct(bg, cand2)
print("pass2 bg:", bg.sum())

# fence: the loose floor mask must not climb into the two white sneakers
bar = Image.new("L", (w, h), 0)
d = ImageDraw.Draw(bar)
d.polygon([(336, 1055), (352, 1000), (470, 1052), (520, 1090), (515, 1160),
           (436, 1228), (360, 1212), (336, 1140)], fill=255)      # raised shoe
d.polygon([(8, 1318), (62, 1262), (238, 1252), (268, 1330), (250, 1420),
           (150, 1452), (30, 1440)], fill=255)                     # left shoe
mask3 = (cand3 & ~(np.asarray(bar) > 0)) | bg
bg = reconstruct(bg, mask3)
print("pass3 bg:", bg.sum())

# walled-in leftovers, each named by one pixel inside it (source coordinates)
SEEDS = [(954, 1373),   # floor under / right of the glass table
         (790, 1368),   # floor on the table's lower shelf
         (717, 1193),   # floor between the two near table legs
         (143, 963),    # background trapped between the crossed chair legs
         (316, 1182),   # grey shadow smear beside the raised shoe
         (796, 1191),   # floor between the far table legs
         (1003, 864)]   # background beside the plant
leftover = (~bg) & (yy >= 820) & (mn >= 182) & (sat <= 52)
lab = label(leftover)
killed = 0
for x, y in SEEDS:
    cid = lab[y, x]
    if cid == 0:
        print(f"  !! seed ({x},{y}) is not on a leftover blob")
        continue
    m = lab == cid
    killed += int(m.sum())
    bg |= m
print("pass4 removed:", killed, "-> bg:", bg.sum(),
      "=", round(100 * bg.sum() / (h * w), 1), "%")

alpha = np.where(bg, 0, 255).astype(np.uint8)
al = Image.fromarray(alpha).filter(ImageFilter.GaussianBlur(0.9))
alf = np.asarray(al).astype(np.float32) / 255.0
alf = np.clip((alf - 0.18) / 0.64, 0, 1)

rgb = a.astype(np.float32)
soft = (alf > 0.02) & (alf < 0.995)
den = np.where(alf < 0.02, 1.0, alf)[..., None]
dec = (rgb - (1.0 - alf)[..., None] * 255.0) / den
rgb = np.where(soft[..., None], np.clip(dec, 0, 255), rgb)

full = Image.fromarray(np.dstack([rgb, alf * 255.0]).astype(np.uint8), "RGBA")
full = full.crop(full.getbbox())
print("cropped:", full.size)
full.save(os.path.join(OUT, "cut.png"))

prev = full.copy()
prev.thumbnail((760, 760))
for name, col in (("preview-dark.png", (8, 8, 10, 255)),
                  ("preview-light.png", (255, 255, 255, 255))):
    c = Image.new("RGBA", prev.size, col)
    c.alpha_composite(prev)
    c.convert("RGB").save(os.path.join(OUT, name))
print("previews written")
