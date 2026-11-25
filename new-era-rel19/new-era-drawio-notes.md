# New ERA diagram — draw.io v6 notes

Generated 2026-11-25 by `gen-drawio-v6.py` (derived from `gen-drawio-v5.py`).
Master file: `new-era-diagram-drawio-v6.drawio` (660 cells, 741,255 bytes).
Exports: `new-era-diagram-drawio-v6.pdf` (409,952 bytes) /
`new-era-diagram-drawio-v6.svg` (6,978,887 bytes), produced on the WSL with
draw.io desktop v32.7.4 CLI under
`dbus-run-session -- xvfb-run -a /opt/drawio/drawio --export …`.
Preview: `../preview/new-era-drawio-v6.jpg` (110 dpi render of the PDF).

v6 = v5 (zones, routing, node layout, styling, poster bands — all
unchanged) plus the "SA Only" wording, per the user decision of
2026-11-25 19:21 (New ERA = the standalone era, phrased "SA Only"):

1. **Badge**: "New ERA · Release-19" → **"New ERA · SA Only · Release-19"**.
2. **Meaning note** on the poster (short version from
   `../explainer/new-era-meaning.md`).
3. "Draft v5" → "Draft v6" labels (title block, right panel).

## 1. Badge (final form)

- Text: **New ERA · SA Only · Release-19** (white bold, black chip).
- Chip geometry changed: (1061, 9, 118×26) → **(1055, 9, 124×26)**;
  font 22pt → **17pt**, so the 30-char text stays on one line.
  Calibration: the v5 badge text measured 95.4mm wide at 22pt in the
  exported PDF (PyMuPDF span bbox), i.e. 30 chars would need ~143mm at
  22pt but only ~110mm at 17pt. In the v6 export the text spans
  x = 1063.0–1169.7mm inside the 1055–1179mm chip (≈8mm margins).
- The 3GPP logo (968, 5, 79.1×46mm) is untouched — same size and place
  as v5 (user direction: logo stays large).

## 2. Meaning note (final form and placement)

Final text (verbatim from `new-era-meaning.md`, short version (a)):

> **New ERA — The Standalone Era**
> 5G built on the 5G Core and NR alone, with no legacy anchor.
> A standalone-only view of the 5G-Advanced era (Release 18 onwards), drawn from Release 19.

- **Language decision: English.** The poster body is entirely English
  (title, panels, notes, credit band), so the note follows the poster;
  the Japanese version of the same text lives in
  `../explainer/new-era-meaning.md` and, in its long form, now also in
  `../explainer/3gpp-explainer-v0.md` (see §4 below).
- **Placement: the open centre of the credit band**, centred at x=475 —
  between the © block (texts end ≈x=230) and the QR code (x=650.5).
  This is the one area that competes with nothing: the title band's
  underside has only ~8mm before the zone tabs start (y≈57.7), and the
  strip above the left panel is too narrow for 3 lines. Baselines align
  with the credit block's rhythm: heading (12pt bold) at 813, body lines
  (9.5pt grey) at 823.5 / 832.5 — the same baselines as the © line and
  the two credit lines. Measured in the export: heading spans
  x = 437.3–512.3, body lines 423.2–526.4 and 395.1–554.5 (all mm,
  nominal page coordinates); the "38.300 Overall · 38.401 Architecture"
  caption (baseline 806, centred x=384) stays clear above the heading.

## 3. Text diff (verify-drawio-v6.py) — fully accounted

Totals: v6 = 572 texts; v5 = 569; v1 baseline = 518.
v6 − v5 = **+6 / −3**, exactly the intended delta:

- +1 badge "New ERA · SA Only · Release-19" (−1 old badge),
- +3 meaning note (heading + 2 body lines),
- +2 "Draft v6" strings (title third line, right-panel note;
  −2 "Draft v5" strings).

No NF name, reference-point label, zone tab or note from v5 is missing;
v6 − v1 shows only the accumulated v4/v5/v6 deltas.

## 4. Explainer updated

`../explainer/3gpp-explainer-v0.md`, section 5: a new subsection
「「New ERA」という名前について」 was added right after the New ERA
Edition paragraph, carrying the long (paragraph) version of the meaning
text from `new-era-meaning.md` §3(b), verbatim (4 paragraphs: the name
is RE-X's, not a 3GPP term — the official name is 5G-Advanced; SA /
Option 2 vs NSA / EN-DC; what disappears from the diagram; the caveat
that real networks keep EPC interworking during migration).

## 5. Verification (verify-drawio-v6.py, on the .drawio) — ALL PASSED

- Zone audit: frames extracted from the .drawio equal the canonical
  gen-v5r3 rects (outer 12/12, sub 31/31); all 69 NF boxes inside their
  assigned outer frame, the 43 CORE boxes inside exactly one assigned
  subcategory frame, 26 non-CORE boxes inside none; PARTIAL 0;
  sub frames nested 31/31; frame edge × box crossings 0; tab × box
  overlaps 0. Membership counts identical to v5.
- Routing: nodes 69, edges 125, stubs 16. Penetrations 0 (edges,
  stubs), endpoint incursions 0. The 3 NG-RAN container-internal
  crossings (F1-C / F1-U / E1) are by design, as in v2–v5.
  "Non-orthogonal segments: 201" is the known 0.1px rounding artifact,
  same as v4/v5.
- Poster band audit: 4 embedded image cells (3GPP logo ×2, QR, RE-X
  logo); badge, © line, credit lines, QR URL, "Powered by" and the
  three meaning-note texts all present.

## 6. Known items (carried over from v5, unchanged)

- SBA COMMON tab: last letter overflows its chip (gen-v5r3 chip-width
  formula); canonical geometry kept.
- CLI export scale quirk: the exported PDF page is 1141.6×807.6mm
  (0.960× A0); print-scale handling still to be settled before
  production.
- The gen-v5r3 SVG still hides the SBA COMMON frame behind the SCP
  deployment frame (draw order); the draw.io line has it fixed since
  v5. Fix at the source if the SVG line is kept.

## 7. Files

- `gen-drawio-v6.py` — generator (badge + meaning note + Draft labels
  are the only deltas vs v5)
- `verify-drawio-v6.py` — routing checks + two-level zone audit +
  band audit (incl. meaning-note presence)
- `new-era-diagram-drawio-v6.drawio` — master, 660 cells
- `new-era-diagram-drawio-v6.pdf` / `.svg` — CLI exports
- `../preview/new-era-drawio-v6.jpg` — full preview (110 dpi)
- `../explainer/3gpp-explainer-v0.md` — §5 gained the
  「New ERA」という名前について subsection
