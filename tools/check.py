# -*- coding: utf-8 -*-
"""Structural QA for the six shipped SVGs."""
import os, re, sys
import xml.etree.ElementTree as ET

OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILES = ["banner.svg", "banner-light.svg", "lanyard.svg",
         "stats.svg", "langs.svg", "trophies.svg", "activity.svg"]
bad = 0

for fn in FILES:
    p = os.path.join(OUT, fn)
    src = open(p, encoding="utf-8").read()
    try:
        root = ET.fromstring(src)
    except ET.ParseError as ex:
        print(f"{fn}: XML ERROR {ex}")
        bad += 1
        continue

    ids, dup = set(), set()
    anim_ids = set()
    for el in root.iter():
        i = el.get("id")
        if i:
            (dup.add(i) if i in ids else ids.add(i))
            if el.tag.split('}')[-1].startswith("animate"):
                anim_ids.add(i)
    refs = set(re.findall(r"url\(#([^)]+)\)", src)) | set(re.findall(r'href="#([^"]+)"', src))
    missing = refs - ids
    begins = set(re.findall(r'begin="([A-Za-z_][\w.-]*)\.(?:end|begin)', src))
    bad_begin = begins - anim_ids

    # SMIL values / keyTimes must agree in length
    len_err = []
    for el in root.iter():
        v, k = el.get("values"), el.get("keyTimes")
        if v and k and len(v.split(";")) != len(k.split(";")):
            len_err.append(f'{el.get("attributeName") or el.tag.split("}")[-1]}'
                           f' {len(v.split(";"))}v/{len(k.split(";"))}k')

    ok = not (dup or missing or bad_begin or len_err)
    bad += 0 if ok else 1
    print(f"{fn:<18} {os.path.getsize(p):>9,}B  ids={len(ids):<4} refs={len(refs):<4} "
          f"{'OK' if ok else 'FAIL'}")
    for name, s in (("duplicate ids", dup), ("missing refs", missing),
                    ("unknown begin targets", bad_begin), ("values/keyTimes", len_err)):
        if s:
            print(f"    {name}: {sorted(s)[:6]}")

# README: every local image must be cache-busted
rd = open(os.path.join(OUT, "README.md"), encoding="utf-8").read()
local = re.findall(r'(?:src|srcset)="(\./[^"]+)"', rd)
print(f"\nlocal image refs: {len(local)}")
for u in local:
    mark = "ok " if "?v=" in u else "NO VERSION"
    if "?v=" not in u:
        bad += 1
    print(f"  {mark} {u}")
print("\n" + ("ALL CHECKS PASSED" if not bad else f"{bad} PROBLEM(S)"))
sys.exit(1 if bad else 0)
