#!/usr/bin/env python3
"""Extract all shapes from the original pptx slide1 into shapes_full.json.

Flattens group transforms, captures geometry preset, fill, line, text runs
(font size/bold/color per paragraph), rotation/flips, and connector
connection references (stCxn/endCxn -> shape id + site index).
"""
import zipfile, json, math, os
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
# Defaults follow the repository layout (drawio/tools/ -> ../../diagram/*.pptx).
PPTX = os.environ.get('PPTX', os.path.join(HERE, '..', '..', 'diagram',
                      '3GPP_Overall_Architecture_and_Specifications.pptx'))
BUILD = os.environ.get('BUILD_DIR', os.path.join(HERE, '..', 'build'))
OUT = os.path.join(BUILD, 'shapes_full.json')
A = 'http://schemas.openxmlformats.org/drawingml/2006/main'
P = 'http://schemas.openxmlformats.org/presentationml/2006/main'
NS = {'a': A, 'p': P}
EMU_MM = 914400.0 / 25.4  # EMU per mm

def q(ns, tag): return '{%s}%s' % (ns, tag)

def get_xfrm(el):
    """Return dict with off/ext/chOff/chExt/rot/flip or None."""
    xf = el.find('.//a:xfrm', NS)
    if xf is None: xf = el.find('p:xfrm', NS)   # graphicFrame (tables)
    if xf is None: return None
    def pt(tag):
        e = xf.find('a:' + tag, NS)
        if e is None: return None
        return (int(e.get('x')) / EMU_MM, int(e.get('y')) / EMU_MM) if tag in ('off', 'chOff') \
            else (int(e.get('cx')) / EMU_MM, int(e.get('cy')) / EMU_MM)
    return {
        'off': pt('off'), 'ext': pt('ext'), 'chOff': pt('chOff'), 'chExt': pt('chExt'),
        'rot': float(xf.get('rot', 0)) / 60000.0,
        'flipH': xf.get('flipH') == '1', 'flipV': xf.get('flipV') == '1',
    }

THEME = {
    'dk1': '000000', 'lt1': 'FFFFFF', 'dk2': '44546A', 'lt2': 'E7E6E6',
    'tx1': '000000', 'bg1': 'FFFFFF', 'tx2': '44546A', 'bg2': 'E7E6E6',
    'accent1': '4472C4', 'accent2': 'ED7D31', 'accent3': 'A5A5A5',
    'accent4': 'FFC000', 'accent5': '5B9BD5', 'accent6': '70AD47',
    'hlink': '0563C1', 'folHlink': '954F72',
}
PRST = {'black': '000000', 'white': 'FFFFFF'}

def _apply_lum(hexcol, mods):
    """Apply DrawingML lumMod/lumOff/tint/shade to an RRGGBB hex color."""
    r, g, b = (int(hexcol[i:i + 2], 16) / 255.0 for i in (0, 2, 4))
    mx, mn = max(r, g, b), min(r, g, b)
    lum = (mx + mn) / 2.0
    if mx == mn:
        hue = sat = 0.0
    else:
        d = mx - mn
        sat = d / (2.0 - mx - mn) if lum > 0.5 else d / (mx + mn)
        if mx == r: hue = ((g - b) / d + (6 if g < b else 0)) / 6.0
        elif mx == g: hue = ((b - r) / d + 2) / 6.0
        else: hue = ((r - g) / d + 4) / 6.0
    for name, val in mods:
        v = val / 100000.0
        if name == 'lumMod': lum = lum * v
        elif name == 'lumOff': lum = lum + v
        elif name == 'tint': r, g, b = (c + (1 - c) * v for c in (r, g, b)); return '%02X%02X%02X' % tuple(int(round(c * 255)) for c in (r, g, b))
        elif name == 'shade': r, g, b = (c * v for c in (r, g, b)); return '%02X%02X%02X' % tuple(int(round(c * 255)) for c in (r, g, b))
    lum = min(1.0, max(0.0, lum))
    if sat == 0:
        v = int(round(lum * 255)); return '%02X%02X%02X' % (v, v, v)
    q = lum * (1 + sat) if lum < 0.5 else lum + sat - lum * sat
    p = 2 * lum - q
    def hue2rgb(p, q, t):
        if t < 0: t += 1
        if t > 1: t -= 1
        if t < 1 / 6: return p + (q - p) * 6 * t
        if t < 1 / 2: return q
        if t < 2 / 3: return p + (q - p) * (2 / 3 - t) * 6
        return p
    r = hue2rgb(p, q, hue + 1 / 3); g = hue2rgb(p, q, hue); b = hue2rgb(p, q, hue - 1 / 3)
    return '%02X%02X%02X' % tuple(int(round(c * 255)) for c in (r, g, b))

def resolve_color(fill_el):
    """Resolve an a:solidFill element to RRGGBB or None."""
    if fill_el is None: return None
    for child in fill_el:
        tag = child.tag.split('}')[1]
        mods = [(c.tag.split('}')[1], int(c.get('val'))) for c in child
                if c.tag.split('}')[1] in ('lumMod', 'lumOff', 'tint', 'shade')]
        if tag == 'srgbClr': return _apply_lum(child.get('val'), mods)
        if tag == 'schemeClr': return _apply_lum(THEME.get(child.get('val'), '000000'), mods)
        if tag == 'prstClr': return _apply_lum(PRST.get(child.get('val'), '000000'), mods)
        if tag == 'sysClr': return _apply_lum(child.get('lastClr', '000000'), mods)
    return None

def spPr_of(el):
    return el.find('p:spPr', NS)

def line_info(el):
    spPr = spPr_of(el)
    if spPr is None: return None
    ln = spPr.find('a:ln', NS)
    if ln is None: return None
    info = {}
    if ln.find('a:noFill', NS) is not None:
        info['color'] = 'none'
    else:
        col = resolve_color(ln.find('a:solidFill', NS))
        if col: info['color'] = col
    if ln.get('w'): info['w_pt'] = int(ln.get('w')) / 12700.0
    d = ln.find('a:prstDash', NS)
    if d is not None: info['dash'] = d.get('val')
    for end, tag in (('head', 'a:headEnd'), ('tail', 'a:tailEnd')):
        e = ln.find(tag, NS)
        if e is not None and e.get('type') not in (None, 'none'):
            info[end] = e.get('type')
    return info

def fill_info(el):
    spPr = spPr_of(el)
    if spPr is None: return None
    if spPr.find('a:noFill', NS) is not None: return 'none'
    return resolve_color(spPr.find('a:solidFill', NS))

def paragraphs(el):
    paras = []
    txBody = el.find('.//p:txBody', NS)
    if txBody is None: txBody = el.find('.//a:txBody', NS)
    if txBody is None: return paras
    # body properties: anchor, insets
    bp = txBody.find('a:bodyPr', NS)
    anchor = bp.get('anchor') if bp is not None else None
    # paragraph alignment default: the shape's own lstStyle (lvl1pPr algn),
    # otherwise None (= presentation defaultTextStyle, algn="l")
    l1 = txBody.find('a:lstStyle/a:lvl1pPr', NS)
    def_algn = l1.get('algn') if l1 is not None else None
    for p in txBody.findall('a:p', NS):
        runs = []
        for r in p.findall('a:r', NS):
            t = r.find('a:t', NS)
            txt = t.text if t is not None else ''
            rPr = r.find('a:rPr', NS)
            run = {'t': txt}
            if rPr is not None:
                if rPr.get('sz'): run['sz'] = int(rPr.get('sz')) / 100.0
                if rPr.get('b') == '1': run['b'] = True
                if rPr.get('i') == '1': run['i'] = True
                c = resolve_color(rPr.find('a:solidFill', NS))
                if c: run['color'] = c
                latin = rPr.find('a:latin', NS)
                if latin is not None: run['font'] = latin.get('typeface')
            runs.append(run)
        # endParaRPr default size
        epr = p.find('a:endParaRPr', NS)
        dsz = int(epr.get('sz')) / 100.0 if epr is not None and epr.get('sz') else None
        pPr = p.find('a:pPr', NS)
        algn = (pPr.get('algn') if pPr is not None else None) or def_algn
        paras.append({'runs': runs, 'defsz': dsz, 'algn': algn})
    return paras

def body_info(el):
    """Text body properties: wrap mode, insets (mm) and vertical anchor.
    Defaults follow DrawingML (wrap=square, l/r 2.54mm, t/b 1.27mm, anchor t)."""
    txBody = el.find('p:txBody', NS)
    if txBody is None: txBody = el.find('a:txBody', NS)
    if txBody is None: return None
    bp = txBody.find('a:bodyPr', NS)
    g = (lambda k, d: d if bp is None or bp.get(k) is None else bp.get(k))
    emu = lambda k, d: int(g(k, d)) / EMU_MM
    return {'wrap': g('wrap', 'square'), 'anchor': g('anchor', 't'),
            'lIns': emu('lIns', 91440), 'rIns': emu('rIns', 91440),
            'tIns': emu('tIns', 45720), 'bIns': emu('bIns', 45720)}

def border(tcPr, tag):
    if tcPr is None: return None
    ln = tcPr.find('a:' + tag, NS)
    if ln is None or ln.find('a:noFill', NS) is not None: return None
    col = resolve_color(ln.find('a:solidFill', NS))
    if col is None: return None
    return {'color': col, 'w_pt': int(ln.get('w', 12700)) / 12700.0}

def table_info(el):
    """a:tbl inside a graphicFrame -> column widths, row heights (mm, local)
    and cells with text, fill, borders, margins and anchor."""
    tbl = el.find('.//a:tbl', NS)
    if tbl is None: return None
    cols = [int(c.get('w')) / EMU_MM for c in tbl.findall('a:tblGrid/a:gridCol', NS)]
    rows, cells = [], []
    for ri, tr in enumerate(tbl.findall('a:tr', NS)):
        rows.append(int(tr.get('h')) / EMU_MM)
        for ci, tc in enumerate(tr.findall('a:tc', NS)):
            if tc.get('hMerge') == '1' or tc.get('vMerge') == '1':
                continue
            tcPr = tc.find('a:tcPr', NS)
            m = (lambda k, d: int(tcPr.get(k, d)) / EMU_MM if tcPr is not None else d / EMU_MM)
            cells.append({
                'r': ri, 'c': ci,
                'cs': int(tc.get('gridSpan', 1)), 'rs': int(tc.get('rowSpan', 1)),
                'paras': paragraphs(tc),
                'fill': resolve_color(tcPr.find('a:solidFill', NS)) if tcPr is not None else None,
                'b': {k: border(tcPr, k) for k in ('lnL', 'lnR', 'lnT', 'lnB')},
                'marL': m('marL', 91440), 'marR': m('marR', 91440),
                'marT': m('marT', 45720), 'marB': m('marB', 45720),
                'anchor': (tcPr.get('anchor') if tcPr is not None else None) or 't',
            })
    return {'cols': cols, 'rows': rows, 'cells': cells}

def prst_geom(el):
    g = el.find('.//a:prstGeom', NS)
    return g.get('prst') if g is not None else None

def cust_geom(el):
    """Extract custom geometry paths (freeforms) in shape-local coords."""
    cg = el.find('.//a:custGeom/a:pathLst', NS)
    if cg is None: return None
    paths = []
    for path in cg.findall('a:path', NS):
        pw = int(path.get('w', 0)); ph = int(path.get('h', 0))
        cmds = []
        for c in path:
            tag = c.tag.split('}')[1]
            if tag in ('moveTo', 'lnTo', 'cubicBezTo'):
                pts = [(int(pt.get('x')), int(pt.get('y'))) for pt in c.findall('a:pt', NS)]
                cmds.append((tag, pts))
            elif tag == 'close':
                cmds.append(('close', []))
            elif tag in ('arcTo', 'quadBezTo'):
                pts = [(int(pt.get('x')), int(pt.get('y'))) for pt in c.findall('a:pt', NS)]
                cmds.append((tag, pts, dict(c.attrib)))
        paths.append({'w': pw, 'h': ph, 'cmds': cmds})
    return paths

def walk(el, transform, out, depth=0):
    """transform: function mapping local (x,y,w,h) -> absolute (x,y,w,h) plus flip flags."""
    tag = el.tag.split('}')[1]
    if tag == 'grpSp':
        xf = get_xfrm(el)
        if xf and xf['off'] and xf['chOff'] and xf['chExt'] and xf['ext']:
            ox, oy = xf['off']; cx, cy = xf['chOff']; cw, ch = xf['chExt']; ew, eh = xf['ext']
            sx = ew / cw if cw else 1.0; sy = eh / ch if ch else 1.0
            parent = transform
            def tr(x, y, w, h, ox=ox, oy=oy, cx=cx, cy=cy, sx=sx, sy=sy, parent=parent):
                lx = ox + (x - cx) * sx; ly = oy + (y - cy) * sy
                return parent(lx, ly, w * sx, h * sy)
            for child in el:
                walk(child, tr, out, depth + 1)
        else:
            for child in el:
                walk(child, transform, out, depth + 1)
        return
    if tag not in ('sp', 'cxnSp', 'pic', 'graphicFrame'):
        return
    xf = get_xfrm(el)
    if not xf or not xf['off'] or not xf['ext']:
        return
    x, y = xf['off']; w, h = xf['ext']
    ax, ay, aw, ah = transform(x, y, w, h)
    # shape id from cNvPr
    cnv = el.find('.//p:cNvPr', NS)
    sid = cnv.get('id') if cnv is not None else None
    name = cnv.get('name') if cnv is not None else ''
    rec = {
        'kind': tag, 'id': sid, 'name': name,
        'x': round(ax, 2), 'y': round(ay, 2), 'w': round(aw, 2), 'h': round(ah, 2),
        'rot': xf['rot'], 'flipH': xf['flipH'], 'flipV': xf['flipV'],
        'geom': prst_geom(el), 'cust': cust_geom(el), 'fill': fill_info(el), 'line': line_info(el),
        'paras': [] if tag == 'graphicFrame' else paragraphs(el),
        'body': body_info(el),
    }
    if tag == 'graphicFrame':
        tb = table_info(el)
        if tb is None:
            return
        # scale table grid by the group transform (ext vs. local size)
        sx = aw / w if w else 1.0; sy = ah / h if h else 1.0
        tb['cols'] = [c * sx for c in tb['cols']]; tb['rows'] = [r * sy for r in tb['rows']]
        rec['kind'] = 'tbl'; rec['tbl'] = tb
    if tag == 'cxnSp':
        cxn = {}
        for which, tname in (('st', 'a:stCxn'), ('end', 'a:endCxn')):
            e = el.find('.//' + tname, NS)
            if e is not None:
                cxn[which] = {'id': e.get('id'), 'idx': int(e.get('idx', 0))}
        rec['cxn'] = cxn
        # begin/end points from off/ext + flips already captured
    out.append(rec)

def main():
    z = zipfile.ZipFile(PPTX)
    pres = ET.fromstring(z.read('ppt/presentation.xml'))
    sldsz = pres.find('.//p:sldSz', NS)
    SW = int(sldsz.get('cx')) / EMU_MM; SH = int(sldsz.get('cy')) / EMU_MM
    root = ET.fromstring(z.read('ppt/slides/slide1.xml'))
    out = []
    identity = lambda x, y, w, h: (x, y, w, h)
    spTree = root.find('.//p:spTree', NS)
    for child in spTree:
        walk(child, identity, out)
    data = {'slide_mm': [round(SW, 2), round(SH, 2)], 'shapes': out}
    os.makedirs(BUILD, exist_ok=True)
    with open(OUT, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    ntext = sum(1 for s in out if any(r['t'] for p in s['paras'] for r in p['runs']))
    print(f'slide {SW:.1f}x{SH:.1f} mm, shapes={len(out)}, with_text={ntext}')
    kinds = {}
    for s in out: kinds[s['kind']] = kinds.get(s['kind'], 0) + 1
    print('kinds:', kinds)
    geoms = {}
    for s in out: geoms[s['geom']] = geoms.get(s['geom'], 0) + 1
    print('geoms:', geoms)

if __name__ == '__main__':
    main()
