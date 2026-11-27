# New ERA diagram — draw.io v7 notes

Generated 2026-11-26 by `gen-drawio-v7.py` (derived from `gen-drawio-v6.py`).
Master file: `new-era-diagram-drawio-v7.drawio` (660 cells, 741,274 bytes).
Exports: `new-era-diagram-drawio-v7.pdf` (409,973 bytes) /
`new-era-diagram-drawio-v7.svg` (6,977,100 bytes), produced with the
draw.io desktop CLI (AppImage in `~/.cache/drawio-cli/`, run as
`dbus-run-session -- xvfb-run -a …/AppRun --no-sandbox -x -f pdf|svg`,
the route recorded in the v1 notes; the `/opt/drawio` .deb path used in
the v5/v6 notes does not exist on this VM).
Previews: `../preview/new-era-drawio-v7.jpg` (110 dpi render of the PDF)
and `../preview/new-era-v7-print.jpg` (110 dpi render of the print PDF).

v7 = v6 (zones, routing, node layout, styling, poster bands — all
unchanged) plus one defect fix and the Draft labels:

1. **Zone tab chip widths** (below).
2. "Draft v6" → "Draft v7" labels (title block, right panel).

## 1. The defect and the fix

Known item since v5: the SBA COMMON tab's last letter ("N") overflowed
its 30.0mm chip and rendered invisible (white on white). Root cause:
the chip-width formula inherited from gen-v5r3,

    w = FS(pt) * 0.62 * len(label) + pad      (pad 9mm outer / 7mm sub)

assumes a flat 0.62 em per character. Measured against the real font
(DejaVu Sans Bold, system TTF), the tab labels actually average
0.61–0.83 em/char depending on the letter mix, so wide-letter labels
overflow once the 3mm `spacingLeft` is also paid out of the chip:

| label | text width | old chip | slack after 3mm left spacing |
|---|---|---|---|
| SBA COMMON (10.5pt) | 29.14mm | 29.97mm | **−2.17mm** |
| PUBLIC WARNING (10.5pt) | 36.72mm | 39.15mm | −0.56mm |
| CORE — CONTROL (10.5pt) | 37.39mm | 39.15mm | −1.24mm |
| NON-3GPP ACCESS (13pt) | 48.77mm | 51.65mm | −0.12mm |

In the v6 CLI export the SBA COMMON text span ends 2.44mm *beyond* the
chip's right edge (measured with PyMuPDF, export-scale mm); a 300 dpi
crop shows the tab reading "SBA COMMOM" with the N outside the grey.

**Fix (in `gen-drawio-v7.py`)**: chip width is now computed from the
real glyph advances. `TAB_ADV` embeds the DejaVu Sans Bold advance
widths (em) measured from
`/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf`, and

    tab_width_mm(label, pt) = 3.0 + FS(pt) * sum(advances) * 1.02 + 2.5

i.e. the 3mm left spacing + the true text width (×1.02 safety) +
2.5mm right padding. Applied in all three tab makers (`zone_tab` 13pt,
`zone_tab_sub` 10.5pt, `zone_tab_above` 10.5pt). Resulting chip widths
for the labels that were short: SBA COMMON 29.97 → 35.20mm,
PUBLIC WARNING 39.15 → 42.94mm, CORE — CONTROL 39.15 → 43.63mm,
NON-3GPP ACCESS 51.65 → 55.25mm. Narrow-letter labels (e.g. SLICE)
come out slightly narrower than before; no frame geometry changed.

## 2. Verification (verify-drawio-v7.py) — ALL PASSED

- Routing: nodes 69, edges 125, stubs 16. Penetrations 0, endpoint
  incursions 0; the 3 NG-RAN container-internal crossings are by
  design, as in v2–v6. "Non-orthogonal segments: 201" is the known
  0.1px rounding artifact.
- Text diff: v7 − v6 = exactly the two "Draft v7" strings (and v6 − v7
  the two "Draft v6" strings). No NF name, reference-point label, zone
  tab or note differs.
- Zone audit: frames extracted from the .drawio equal the canonical
  gen-v5r3 rects (outer 12/12, sub 31/31); all 69 NF boxes in their
  assigned frames, PARTIAL 0; sub frames nested 31/31; frame edge ×
  box crossings 0; **tab × box overlaps 0** (the wider chips hit
  nothing).
- Poster band audit: 4 embedded image cells; badge, © line, credit
  lines, QR URL, "Powered by" and the three meaning-note texts all
  present.
- **Tab fit audit (new in v7)**: all 43 tab chips re-measured against
  the glyph-advance requirement (3mm left + text × 1.02 + ≥2.0mm
  right). Tightest slack +0.49mm — ALL PASSED.
- Export check (PyMuPDF, on `new-era-diagram-drawio-v7.pdf`): the
  SBA COMMON span sits fully inside its chip — left margin 3.25mm,
  **right margin +2.59mm** (v6: −2.44mm), export-scale mm. A 300 dpi
  crop of the tab area was eyeballed against the v6 crop: "SBA COMMON"
  now reads complete inside the grey chip.

## 3. Print PDFs (make_print_pdfs_v7.py — same construction as v6)

Source = the CLI export (1141.56×807.55mm), embedded as a Form XObject
and scaled ×1.041421, so everything stays vector:

- `new-era-diagram-v7-print-a0.pdf` — page **1189.000×841.000mm**
  exactly (measured), design placed 1188.845×841.000mm at offset
  (0.078, 0)mm.
- `new-era-diagram-v7-print-gelato.pdf` — page **1197×849mm**,
  TrimBox = central 1189×841mm (offset 4mm), BleedBox = full page.

`final/new-era-a0/` now holds the v7 set (drawio / print-a0 /
print-gelato / print preview); `MATERIALS-INDEX.md` and
`final/README.md` were updated. The v6 files remain in this folder,
untouched.

## 4. Known items (carried over)

- CLI export scale quirk (unchanged): the exported PDF page is
  1141.56×807.55mm (0.960× A0); print files compensate as above.
- The SBA COMMON chip still covers the tail of the pre-existing
  "for Roaming" stub note — the overlap exists in the canonical
  geometry since v5; the chip is 5.2mm wider now, so it covers
  slightly more of the note's tail. No box or label is affected.
- The gen-v5r3 SVG line still has both the SCP draw-order occlusion
  and the same chip-width flaw. Not fixed: that line is reference
  material only; fix at gen-v5r3 if it is ever promoted back to a
  master.

## 5. Files

- `gen-drawio-v7.py` — generator (tab-width fix + Draft labels are the
  only deltas vs v6)
- `verify-drawio-v7.py` — routing checks + two-level zone audit +
  band audit + tab fit audit
- `new-era-diagram-drawio-v7.drawio` — master, 660 cells
- `new-era-diagram-drawio-v7.pdf` / `.svg` — CLI exports
- `make_print_pdfs_v7.py` — print-PDF builder (v6 script, re-pointed)
- `new-era-diagram-v7-print-a0.pdf` / `new-era-diagram-v7-print-gelato.pdf`
- `../preview/new-era-drawio-v7.jpg`, `../preview/new-era-v7-print.jpg`
