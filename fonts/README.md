# Type

Three families, each doing one job:

| Family | Used for | How it ships |
| :--- | :--- | :--- |
| **Clash Display** | the big name, the neon sign, the card and badge titles | **vector outlines** — no font file anywhere |
| **Sora** | body copy, pills, labels, badge details | subsetted variable WOFF2, base64 `@font-face` inside each SVG |
| **JetBrains Mono** | terminal line, role cycler, code card, every number | subsetted variable WOFF2, base64 `@font-face` inside each SVG |

## Why they are embedded this way

GitHub serves a README image through its camo proxy and renders it inside an
`<img>` tag. That puts the SVG in the browser's *secure static mode*: no
scripts, and **no external requests of any kind** — so a Google Fonts `@import`
or a `<link>` silently does nothing and every label falls back to whatever the
reader's machine happens to have. A `data:` URI is not an external request, so
a base64 `@font-face` is the only thing that actually works there. Each SVG
carries only the characters it actually prints, which is why the subsets are
15–30 KB rather than the full 300 KB families.

Clash Display is handled differently on purpose. Its licence (below) forbids
subsetting and format conversion, so none of it is embedded — the handful of
strings set in it were converted to plain `<path>` outlines instead, which the
same licence treats as artwork rather than as font software.

## Licences

**Sora** — Copyright 2019 The Sora Project Authors,
<https://github.com/sora-xor/sora-font>
**JetBrains Mono** — Copyright 2020 The JetBrains Mono Project Authors,
<https://github.com/JetBrains/JetBrainsMono>

Both are licensed under the SIL Open Font License 1.1, reproduced in full in
[`OFL.txt`](./OFL.txt). Neither declares a Reserved Font Name, so the subsets
keep their original family names; each subset also keeps the copyright and
licence strings in its own `name` table.

**Clash Display** — © Indian Type Foundry, <https://www.fontshare.com/fonts/clash-display>,
ITF Free Font License. Used here only as outlined artwork.

## Rebuilding

The SVGs are generated, not hand-edited. If you change a string, the subset has
to be regenerated so the new characters are present — otherwise they render as
blank boxes. See [`tools/README.md`](../tools/README.md), then bump `?v=` in the
root `README.md` so GitHub's image cache lets the new file through.
