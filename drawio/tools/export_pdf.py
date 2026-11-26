#!/usr/bin/env python3
"""Export a generated .drawio to a print PDF at A0 actual size.

    python3 export_pdf.py IN.drawio OUT.pdf [PNG_PREVIEW]

Why the extra steps:
  * draw.io units are CSS px at 96 dpi; the generator writes an A0 page
    (4494 x 3179 px) with a full-page background cell, so the export bounding
    box is exactly the page.
  * The draw.io desktop CLI (Electron printToPDF) maps 1 px to 0.72 pt and
    ignores --scale for PDF, so a plain export comes out at 96 % of A0.
    --width 4681 (= 4494 / 0.96) brings it to A0 within ~0.4 mm.
  * pypdf then scales the page uniformly to the exact A0 width and sets the
    MediaBox to exactly 1189 x 841 mm (3370.39 x 2383.94 pt), centring any
    sub-millimetre slack.
Requires: draw.io desktop (>= 24), xvfb-run (headless), pypdf, pdftoppm (preview).
"""
import os, subprocess, sys, tempfile
from pypdf import PdfReader, PdfWriter, Transformation

A0_W, A0_H = 1189 / 25.4 * 72, 841 / 25.4 * 72   # landscape, pt
DRAWIO = os.environ.get('DRAWIO', 'drawio')

def main(src, dst, png=None):
    with tempfile.TemporaryDirectory() as td:
        raw = os.path.join(td, 'raw.pdf')
        cmd = ['xvfb-run', '-a', DRAWIO, '--no-sandbox', '--disable-gpu', '-x', '-f', 'pdf',
               '--width', '4681', '--timeout', '600', '-o', raw, src]
        # A stale/unresponsive session D-Bus (e.g. right after a WSL restart)
        # makes Electron hang forever before opening its window; draw.io does
        # not need D-Bus for export, so disable it.
        env = dict(os.environ, DBUS_SESSION_BUS_ADDRESS='disabled:')
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=env)
        r = PdfReader(raw)
        if len(r.pages) != 1:
            sys.exit(f'expected 1 page, got {len(r.pages)}')
        pg = r.pages[0]
        w, h = float(pg.mediabox.width), float(pg.mediabox.height)
        k = min(A0_W / w, A0_H / h)
        pg.add_transformation(Transformation().scale(k, k).translate((A0_W - w * k) / 2, (A0_H - h * k) / 2))
        pg.mediabox.lower_left = (0, 0); pg.mediabox.upper_right = (A0_W, A0_H)
        pg.cropbox.lower_left = (0, 0); pg.cropbox.upper_right = (A0_W, A0_H)
        out = PdfWriter(); out.add_page(pg)
        out.add_metadata({'/Title': os.path.splitext(os.path.basename(src))[0]})
        with open(dst, 'wb') as f: out.write(f)
        print(f'{src} -> {dst}: raw {w:.2f}x{h:.2f} pt, scaled x{k:.5f} -> {A0_W:.2f}x{A0_H:.2f} pt (A0 landscape)')
    if png:
        base = os.path.splitext(png)[0]
        subprocess.run(['pdftoppm', '-r', '30', '-png', '-singlefile', dst, base], check=True)

if __name__ == '__main__':
    main(*sys.argv[1:])
