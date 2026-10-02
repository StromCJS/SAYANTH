# -*- coding: utf-8 -*-
"""Reads the public contribution calendar for the profile and stores it as
activity.json, which build.py turns into activity.svg.

No token needed: this is the same calendar fragment GitHub serves to a logged
out visitor, so what lands in the card is exactly what a visitor to the profile
sees. Re-run it whenever you want the card refreshed.
"""
import json, os, re, sys, urllib.request

USER = "StromCJS"
HERE = os.path.dirname(os.path.abspath(__file__))
URL = f"https://github.com/users/{USER}/contributions"

req = urllib.request.Request(URL, headers={
    "Accept": "text/html",
    "User-Agent": f"{USER}-profile-card/1.0 (+https://github.com/{USER})"})
html = urllib.request.urlopen(req, timeout=45).read().decode("utf-8", "replace")

cells = {}
for m in re.finditer(
        r'data-date="(\d{4}-\d{2}-\d{2})"\s+id="([^"]+)"\s+data-level="(\d+)"', html):
    cells[m.group(2)] = {"date": m.group(1), "level": int(m.group(3)), "count": 0}

for cid, txt in re.findall(
        r'<tool-tip[^>]*for="(contribution-day-component-[^"]+)"[^>]*>(.*?)</tool-tip>',
        html, re.S):
    if cid in cells:
        m = re.match(r"\s*(\d+)\s+contribution", txt)
        cells[cid]["count"] = int(m.group(1)) if m else 0

days = sorted(cells.values(), key=lambda d: d["date"])
if not days:
    sys.exit("could not parse the calendar - GitHub may have changed the markup")

total = sum(d["count"] for d in days)
active = sum(1 for d in days if d["count"])
best = max(days, key=lambda d: d["count"])

streak = longest = 0
for d in days:
    streak = streak + 1 if d["count"] else 0
    longest = max(longest, streak)
cur = 0
for d in reversed(days):
    if not d["count"]:
        break
    cur += 1

out = {"user": USER, "from": days[0]["date"], "to": days[-1]["date"],
       "total": total, "active": active, "best": best["count"],
       "best_date": best["date"], "longest": longest, "current": cur,
       "days": [[d["date"], d["level"], d["count"]] for d in days]}
json.dump(out, open(os.path.join(HERE, "activity.json"), "w"), indent=0)
print(f"{out['from']} -> {out['to']}  {len(days)} days")
print(f"total {total}  active {active}  best {best['count']} on {best['date']}  "
      f"longest streak {longest}  current {cur}")
