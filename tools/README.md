# Generator

The six SVGs in the repository root are **generated**, not hand-written. Each
one carries its own subsetted copy of Sora and JetBrains Mono, holding exactly
the characters that file prints — so editing a string by hand will leave you
with blank boxes wherever you used a character the subset doesn't have. Change
the source here and rebuild instead.

## Setup

```bash
pip install fonttools brotli pillow numpy
./fetch-fonts.sh
```

`fetch-fonts.sh` pulls JetBrains Mono, Sora and Clash Display into
`tools/fonts/`. They are not committed — Clash Display's licence does not allow
redistributing the font file, so all three are fetched the same way.

## Build

```bash
python fetch-activity.py   # refresh the contribution calendar (optional)
python build.py            # writes the seven SVGs to the repository root
python check.py            # XML, duplicate ids, dangling refs, README ?v= markers
```

Then bump `?v=` in the root `README.md`, or GitHub's image proxy will keep
serving the previous version.

## The other scripts

| Script | What it does |
| :--- | :--- |
| `cutout.py` | cuts `banner-source.webp` out of its white studio background and writes `cut.png` plus two preview composites |
| `assets.py` | resizes `cut.png` and crops the face out of `ID-CARD.png`, then writes both into `assets.json` as base64 PNG |
| `fetch-activity.py` | reads the public contribution calendar into `activity.json` — no token, same data a logged-out visitor sees |
| `fontkit.py` | font subsetting (WOFF2, variable weight axis preserved) and Clash Display → vector outlines |
| `build.py` | the SVGs themselves — palette, layout, SMIL |

`assets.json` and `activity.json` are committed, so a plain `python build.py`
works without re-running the image or network steps.

Nothing in the README depends on a third-party card service. That is deliberate:
the activity graph used to come from `github-readme-activity-graph.vercel.app`,
which has since been switched off and now answers every request with HTTP 402,
so the image was broken for everyone.

## Changing the colours

Every colour comes from the `DARK` and `LIGHT` dicts near the top of
`build.py`, plus the small `MAP` of hard-coded values in the lanyard and card
sections. Nothing else holds a hex value.

## A note on the animation

SMIL (`<animate>`, `<animateTransform>`) and CSS keyframes only — GitHub strips
`<script>` from rendered SVGs. CSS `:hover` is in the file and works if you open
an SVG directly, but it will never fire in the README, where the image sits
inside an `<img>` and receives no pointer events.
