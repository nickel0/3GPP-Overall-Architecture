#!/usr/bin/env python3
"""Generate draw.io (.drawio) files from the extracted original pptx shapes.

Outputs (in composite/):
  composite-diagram-drawio-master.drawio  -- faithful reproduction of the
                                             original (Rel-17) figure only
  composite-diagram-drawio.drawio         -- master + Rel-18/Rel-19 additions
                                             integrated into the figure
Also renders SVG previews (work/render_master.svg, work/render_composite.svg)
for visual verification, and validates that every text string from the pptx
is present in the generated .drawio values.

Coordinate system: draw.io units = pt. Page = A0 landscape
(3370.39 x 2383.94 pt). The original slide (554.47 x 311.87 mm) is scaled
by K = 3370.39/554.47/25.4*72 ... see K below; fonts and stroke widths are
scaled by FS = K / (72/25.4) so the figure fills the A0 width.
A title band (TITLE_H units) is reserved at the top of the page.
"""
import json, math, re, sys
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape

BASE = '/home/hatch/workspace/work/ogawa-3gpp-poster/composite'
SRC = BASE + '/work/shapes_full.json'

PAGE_W, PAGE_H = 3370.39, 2383.94          # A0 landscape, pt
SLIDE_W_MM, SLIDE_H_MM = 554.47, 311.87
K = PAGE_W / SLIDE_W_MM                    # draw.io units per mm  (~6.079)
FS = K / (72.0 / 25.4)                     # font/stroke scale      (~2.145)
TITLE_H = 120.0                            # title band height (units)
OY = TITLE_H                               # figure top offset

GREEN = '00B050'   # Rel-18 (also used inside the original for Rel-16)
BLUE = '0070C0'    # Rel-19 (also used inside the original for Rel-17)
BLACK = '000000'

def X(mm): return mm * K
def Y(mm): return OY + mm * K

# ---------------------------------------------------------------- data load
data = json.load(open(SRC))
shapes = data['shapes']
by_id = {s['id']: s for s in shapes}

def shape_text(s):
    return '\n'.join(''.join(r['t'] for r in p['runs']) for p in s['paras']).strip()

# connection-site index -> (fx, fy) on the target bbox (PowerPoint convention)
SITES = {0: (0.5, 0.0), 1: (1.0, 0.5), 2: (0.5, 1.0), 3: (0.0, 0.5),
         4: (0.0, 0.0), 5: (1.0, 0.0), 6: (1.0, 1.0), 7: (0.0, 1.0)}

def conn_point(shape, idx):
    fx, fy = SITES.get(idx, (0.5, 0.5))
    return (shape['x'] + fx * shape['w'], shape['y'] + fy * shape['h'])

def line_endpoints(s):
    """Endpoints (mm) of a free line/connector from bbox + flips."""
    x, y, w, h = s['x'], s['y'], s['w'], s['h']
    sx = x + (w if s['flipH'] else 0.0)
    sy = y + (h if s['flipV'] else 0.0)
    ex = x + (0.0 if s['flipH'] else w)
    ey = y + (0.0 if s['flipV'] else h)
    return (sx, sy), (ex, ey)

# ---------------------------------------------------------------- text HTML
def para_align(s, p):
    if p['algn'] == 'ctr': return 'center'
    if p['algn'] == 'l': return 'left'
    if p['algn'] == 'r': return 'right'
    # deck default: boxed shapes centre, bare text blocks left
    if (s.get('line') and s['line'].get('color') not in (None, 'none')) or s.get('fill'):
        return 'center'
    return 'left'

def value_html(s, extra_style=''):
    """Build draw.io HTML value from paragraphs/runs."""
    if not s['paras']:
        return ''
    parts = []
    for p in s['paras']:
        algn = para_align(s, p)
        runs_html = ''
        for r in p['runs']:
            t = escape(r['t'])
            if not t:
                continue
            attrs = ''
            if r.get('color'): attrs += f' color="#{r["color"]}"'
            style = ''
            if r.get('sz'): style += f'font-size:{r["sz"] * FS:.1f}px;'
            if r.get('b'): style += 'font-weight:bold;'
            if r.get('i'): style += 'font-style:italic;'
            if style: attrs += f' style="{style}"'
            runs_html += f'<font{attrs}>{t}</font>' if attrs else t
        if not runs_html:
            runs_html = '<br>'
        parts.append(f'<div align="{algn}">{runs_html}</div>')
    return ''.join(parts)

def plain_value(s):
    return '\n'.join(''.join(r['t'] for r in p['runs']) for p in s['paras'])

# ---------------------------------------------------------------- styles
def vertex_style(s):
    geom = s['geom']
    st = ['whiteSpace=wrap', 'html=1']
    if geom == 'ellipse':
        st.append('ellipse')
    elif geom == 'leftBracket':
        st.append('shape=mxgraph.basic.l_bracket')
    elif geom == 'rightBracket':
        st.append('shape=mxgraph.basic.r_bracket')
    else:
        st.append('rounded=0')
    fill = s.get('fill')
    if fill and fill != 'none':
        st.append(f'fillColor=#{fill}')
    else:
        st.append('fillColor=none')
    ln = s.get('line') or {}
    lc = ln.get('color')
    if lc and lc != 'none':
        st.append(f'strokeColor=#{lc}')
        wpt = ln.get('w_pt', 0.75) * FS
        st.append(f'strokeWidth={wpt:.2f}')
        if ln.get('dash'): st.append('dashed=1')
    else:
        st.append('strokeColor=none')
    if s['rot']:
        st.append(f'rotation={s["rot"]:.1f}')
    st.append('fontFamily=Arial')
    st.append(f'fontSize={5.6 * FS:.1f}')
    st.append('fontColor=#000000')
    return ';'.join(st) + ';'

def edge_style(s, jumps=False):
    ln = s.get('line') or {}
    st = ['edgeStyle=none', 'curved=0', 'html=1']
    lc = ln.get('color') or BLACK
    st.append(f'strokeColor=#{lc}')
    st.append(f'strokeWidth={ln.get("w_pt", 0.75) * FS:.2f}')
    if ln.get('dash'): st.append('dashed=1')
    st.append('startArrow=classic' if ln.get('head') else 'startArrow=none')
    st.append('endArrow=classic' if ln.get('tail') else 'endArrow=none')
    if jumps: st.append('jumpStyle=arc'); st.append('jumpSize=8')
    return ';'.join(st) + ';'

# ---------------------------------------------------------------- model build
class Model:
    def __init__(self):
        self.cells = []   # (id, value, style, vertex, parent, geom_dict, source, target)
        self.n = 0
    def new_id(self, prefix):
        self.n += 1
        return f'{prefix}{self.n}'
    def add_vertex(self, value, style, x, y, w, h, cid=None):
        cid = cid or self.new_id('v')
        self.cells.append({'id': cid, 'value': value, 'style': style, 'vertex': 1,
                           'geom': {'x': x, 'y': y, 'w': w, 'h': h}})
        return cid
    def add_edge(self, value, style, source=None, target=None,
                 sp=None, tp=None, points=None, exit_xy=None, entry_xy=None, cid=None):
        cid = cid or self.new_id('e')
        g = {}
        if sp: g['sp'] = sp
        if tp: g['tp'] = tp
        if points: g['points'] = points
        sty = style
        if exit_xy: sty += f'exitX={exit_xy[0]};exitY={exit_xy[1]};'
        if entry_xy: sty += f'entryX={entry_xy[0]};entryY={entry_xy[1]};'
        self.cells.append({'id': cid, 'value': value, 'style': sty, 'edge': 1,
                           'source': source, 'target': target, 'geom': g})
        return cid
    def to_xml(self, title):
        m = ET.Element('mxfile', {'host': 'app.diagrams.net', 'type': 'device'})
        d = ET.SubElement(m, 'diagram', {'name': title, 'id': 'page1'})
        gm = ET.SubElement(d, 'mxGraphModel', {
            'dx': '1000', 'dy': '700', 'grid': '0', 'gridSize': '10',
            'guides': '1', 'tooltips': '1', 'connect': '1', 'arrows': '1',
            'fold': '1', 'page': '1', 'pageScale': '1',
            'pageWidth': f'{PAGE_W:.0f}', 'pageHeight': f'{PAGE_H:.0f}',
            'math': '0', 'shadow': '0'})
        root = ET.SubElement(gm, 'root')
        ET.SubElement(root, 'mxCell', {'id': '0'})
        ET.SubElement(root, 'mxCell', {'id': '1', 'parent': '0'})
        for c in self.cells:
            attrs = {'id': c['id'], 'value': c.get('value', ''), 'style': c['style'],
                     'parent': '1'}
            if c.get('vertex'): attrs['vertex'] = '1'
            if c.get('edge'):
                attrs['edge'] = '1'
                if c.get('source'): attrs['source'] = c['source']
                if c.get('target'): attrs['target'] = c['target']
            cell = ET.SubElement(root, 'mxCell', attrs)
            g = c['geom']
            ga = {'as': 'geometry'}
            if 'x' in g:
                ga.update({'x': f"{g['x']:.1f}", 'y': f"{g['y']:.1f}",
                           'width': f"{g['w']:.1f}", 'height': f"{g['h']:.1f}"})
            geo = ET.SubElement(cell, 'mxGeometry', ga)
            if 'sp' in g:
                ET.SubElement(geo, 'mxPoint', {'x': f"{g['sp'][0]:.1f}",
                                               'y': f"{g['sp'][1]:.1f}", 'as': 'sourcePoint'})
            if 'tp' in g:
                ET.SubElement(geo, 'mxPoint', {'x': f"{g['tp'][0]:.1f}",
                                               'y': f"{g['tp'][1]:.1f}", 'as': 'targetPoint'})
            if 'points' in g:
                arr = ET.SubElement(geo, 'Array', {'as': 'points'})
                for (px, py) in g['points']:
                    ET.SubElement(arr, 'mxPoint', {'x': f'{px:.1f}', 'y': f'{py:.1f}'})
        return ET.ElementTree(m)

# map pptx shape id -> drawio cell id
cell_of = {}

def build_original(model, jumps=False):
    """Add all original shapes. Returns dict of render items for SVG preview."""
    render = []  # ('rect'|'ellipse'|'line'|'poly'|'text', ...)
    # vertices first (connectors reference them)
    for s in shapes:
        if s['kind'] == 'cxnSp':
            continue
        geom = s['geom']
        if geom == 'line':
            (sx, sy), (ex, ey) = line_endpoints(s)
            cid = model.add_edge('', edge_style(s, jumps),
                                 sp=(X(sx), Y(sy)), tp=(X(ex), Y(ey)),
                                 cid='o' + s['id'])
            cell_of[s['id']] = cid
            render.append(('line', (X(sx), Y(sy)), (X(ex), Y(ey)), (s.get('line') or {}).get('color') or BLACK, (s.get('line') or {}).get('dash')))
        elif s.get('cust'):
            pts = []
            for path in s['cust']:
                for cmd in path['cmds']:
                    for (px, py) in (cmd[1] if len(cmd) > 1 else []):
                        pts.append((X(s['x'] + px / path['w'] * s['w']),
                                    Y(s['y'] + py / path['h'] * s['h'])))
            if len(pts) >= 2:
                cid = model.add_edge('', edge_style(s, jumps),
                                     sp=pts[0], tp=pts[-1], points=pts[1:-1],
                                     cid='o' + s['id'])
                cell_of[s['id']] = cid
                render.append(('poly', pts, (s.get('line') or {}).get('color') or BLACK))
        elif geom in ('bentConnector2', 'bentConnector3', 'bentConnector4', 'arc'):
            (sx, sy), (ex, ey) = line_endpoints(s)
            mx = (sx + ex) / 2.0
            pts = [(X(sx), Y(sy)), (X(mx), Y(sy)), (X(mx), Y(ey)), (X(ex), Y(ey))] \
                if abs(ex - sx) > abs(ey - sy) else \
                [(X(sx), Y(sy)), (X(sx), Y((sy + ey) / 2.0)), (X(ex), Y((sy + ey) / 2.0)), (X(ex), Y(ey))]
            cid = model.add_edge('', edge_style(s, jumps),
                                 sp=pts[0], tp=pts[-1], points=pts[1:-1],
                                 cid='o' + s['id'])
            cell_of[s['id']] = cid
            render.append(('poly', pts, (s.get('line') or {}).get('color') or BLACK))
        else:
            cid = model.add_vertex(value_html(s), vertex_style(s),
                                   X(s['x']), Y(s['y']), s['w'] * K, s['h'] * K,
                                   cid='o' + s['id'])
            cell_of[s['id']] = cid
            kind = 'ellipse' if geom == 'ellipse' else 'rect'
            render.append((kind, X(s['x']), Y(s['y']), s['w'] * K, s['h'] * K,
                           s.get('fill'), (s.get('line') or {}).get('color'),
                           plain_value(s)))
    # connectors
    for s in shapes:
        if s['kind'] != 'cxnSp':
            continue
        cxn = s.get('cxn') or {}
        value = value_html(s)
        if 'st' in cxn and 'end' in cxn and cxn['st']['id'] in cell_of and cxn['end']['id'] in cell_of:
            src = by_id[cxn['st']['id']]; dst = by_id[cxn['end']['id']]
            ex = SITES.get(cxn['st']['idx'], (0.5, 0.5))
            en = SITES.get(cxn['end']['idx'], (0.5, 0.5))
            cid = model.add_edge(value, edge_style(s, jumps),
                                 source=cell_of[src['id']], target=cell_of[dst['id']],
                                 exit_xy=ex, entry_xy=en, cid='o' + s['id'])
            p1 = conn_point(src, cxn['st']['idx']); p2 = conn_point(dst, cxn['end']['idx'])
            render.append(('line', (X(p1[0]), Y(p1[1])), (X(p2[0]), Y(p2[1])),
                           (s.get('line') or {}).get('color') or BLACK, (s.get('line') or {}).get('dash')))
        else:
            (sx, sy), (ex2, ey2) = line_endpoints(s)
            cid = model.add_edge(value, edge_style(s, jumps),
                                 sp=(X(sx), Y(sy)), tp=(X(ex2), Y(ey2)), cid='o' + s['id'])
            render.append(('line', (X(sx), Y(sy)), (X(ex2), Y(ey2)),
                           (s.get('line') or {}).get('color') or BLACK, (s.get('line') or {}).get('dash')))
        cell_of[s['id']] = cid
    return render

# ---------------------------------------------------------------- additions
def find_shape(pred, desc):
    hits = [s for s in shapes if pred(shape_text(s), s)]
    if not hits:
        raise SystemExit(f'target not found: {desc}')
    return hits[0]

def obstacles():
    """Hard obstacles: shapes with a visible border or fill.
    Text-only labels are soft obstacles (handled in place_box scoring)."""
    obs = []
    for s in shapes:
        if s['kind'] == 'sp' and s['geom'] not in ('line',) and not s.get('cust'):
            if s['w'] * s['h'] > 3000:
                continue  # frame / background panel: interior is usable space
            ln = (s.get('line') or {}).get('color')
            if (ln and ln != 'none') or s.get('fill'):
                obs.append((s['x'], s['y'], s['w'], s['h']))
    return obs

def soft_obstacles():
    obs = []
    hard = set(obstacles())
    for s in shapes:
        if s['kind'] == 'sp' and s['geom'] not in ('line',) and not s.get('cust'):
            t = (s['x'], s['y'], s['w'], s['h'])
            if t not in hard and s['w'] >= 4 and s['h'] >= 1.5:
                obs.append(t)
    return obs

SOFT = None  # lazily initialised after OBS

def segments():
    segs = []
    for s in shapes:
        if s['kind'] == 'cxnSp':
            cxn = s.get('cxn') or {}
            if 'st' in cxn and 'end' in cxn:
                p1 = conn_point(by_id[cxn['st']['id']], cxn['st']['idx'])
                p2 = conn_point(by_id[cxn['end']['id']], cxn['end']['idx'])
            else:
                p1, p2 = line_endpoints(s)
            segs.append((p1, p2))
        elif s['geom'] == 'line' and s['kind'] == 'sp':
            p1, p2 = line_endpoints(s)
            segs.append((p1, p2))
    return segs

OBS = obstacles()
SOFT = soft_obstacles()
SEGS = segments()

def seg_intersect(p1, p2, p3, p4):
    def orient(a, b, c):
        v = (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
        return 0 if abs(v) < 1e-9 else (1 if v > 0 else -1)
    o1, o2, o3, o4 = orient(p1, p2, p3), orient(p1, p2, p4), orient(p3, p4, p1), orient(p3, p4, p2)
    return o1 != o2 and o3 != o4

def place_box(w, h, region, anchors):
    """Scan region (x0,y0,x1,y1) mm for a spot with no vertex overlap.
    Score: line crossings of anchor lines + distance to anchors."""
    x0, y0, x1, y1 = region
    best = None
    step = 1.0
    yy = y0
    while yy + h <= y1:
        xx = x0
        while xx + w <= x1:
            ok = True
            for (ox, oy, ow, oh) in OBS:
                if xx - 0.7 < ox + ow and ox < xx + w + 0.7 and yy - 0.7 < oy + oh and oy < yy + h + 0.7:
                    ok = False; break
            if ok:
                soft_pen = 0.0
                for (ox, oy, ow, oh) in (SOFT or []):
                    if xx < ox + ow and ox < xx + w and yy < oy + oh and oy < yy + h:
                        soft_pen += 9.0
                # heavy penalty for existing lines passing through the box
                corners = [(xx, yy), (xx + w, yy), (xx + w, yy + h), (xx, yy + h)]
                edges = [(corners[i], corners[(i + 1) % 4]) for i in range(4)]
                for (p1, p2) in SEGS:
                    inside = (xx <= p1[0] <= xx + w and yy <= p1[1] <= yy + h) or \
                             (xx <= p2[0] <= xx + w and yy <= p2[1] <= yy + h)
                    if inside or any(seg_intersect(p1, p2, e1, e2) for (e1, e2) in edges):
                        soft_pen += 14.0
                cx, cy = xx + w / 2, yy + h / 2
                cross = 0
                dist = 0.0
                for (ax, ay) in anchors:
                    dist += math.hypot(cx - ax, cy - ay)
                    for (p1, p2) in SEGS:
                        if seg_intersect((cx, cy), (ax, ay), p1, p2):
                            cross += 1
                score = cross * 6.0 + dist + soft_pen
                if best is None or score < best[0]:
                    best = (score, xx, yy, cross)
            xx += step
        yy += step
    if best is None:
        return None
    # register as obstacle for subsequent placements
    OBS.append((best[1], best[2], w, h))
    return best

def new_box_style(color):
    return (f'rounded=0;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#{color};'
            f'strokeWidth={0.75 * FS:.2f};fontFamily=Arial;fontSize={8.42 * FS:.1f};fontColor=#{color};')

def new_edge_style(color, dashed=False):
    st = (f'edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;startArrow=none;endArrow=none;strokeColor=#{color};'
          f'strokeWidth={0.75 * FS:.2f};jumpStyle=arc;jumpSize=8;fontFamily=Arial;'
          f'fontSize={5.6 * FS:.1f};fontColor=#{color};labelBackgroundColor=#FFFFFF;')
    if dashed: st += 'dashed=1;'
    return st

def label_html(text, color, size=5.6):
    return f'<div align="center"><font color="#{color}" style="font-size:{size * FS:.1f}px">{escape(text)}</font></div>'

def build_additions(model, render):
    placed = {}
    # --- locate peers (slide mm centres)
    def centre(s): return (s['x'] + s['w'] / 2, s['y'] + s['h'] / 2)
    AF = find_shape(lambda t, s: t == 'AF', 'AF')
    NEF = find_shape(lambda t, s: t == 'NEF', 'NEF')
    UDM = find_shape(lambda t, s: t.startswith('UDM'), 'UDM')
    PCF = find_shape(lambda t, s: t == 'PCF', 'PCF')
    SMF = find_shape(lambda t, s: t.startswith('PGW-C') and 'SMF' in t, 'SMF (PGW-C (A-)SMF)')
    AMF = find_shape(lambda t, s: t == 'AMF', 'AMF')
    NRF = find_shape(lambda t, s: t == 'NRF', 'NRF')
    SCP = find_shape(lambda t, s: t == 'SCP', 'SCP')
    NWDAF = find_shape(lambda t, s: t == 'NWDAF', 'NWDAF')
    TSCTSF = find_shape(lambda t, s: t == 'TSCTSF', 'TSCTSF')
    DCCF = find_shape(lambda t, s: t == 'DCCF', 'DCCF')
    NSACF = find_shape(lambda t, s: t == 'NSACF', 'NSACF')
    UDR = find_shape(lambda t, s: t == 'UDR' and s['w'] > 8, 'UDR')
    NGRAN = find_shape(lambda t, s: t.startswith('NG-RAN'), 'NG-RAN')
    PSAUPF = find_shape(lambda t, s: t.startswith('PGW-U'), 'PSA-UPF')

    BW, BH = 13.8, 5.8
    # Free space identified by grid probe: a vertical strip at x=327..346
    # between the 5GC frame (right edge 329.2) and the side panels (~347),
    # plus the inside bottom edge of the 5GC frame (bottom 298.9).
    # The strip stack is hand-placed for a clean column (see notes).
    def fixed_box(x, y, w, h=BH):
        for (ox, oy, ow, oh) in OBS:
            if x - 0.5 < ox + ow and ox < x + w + 0.5 and y - 0.5 < oy + oh and oy < y + h + 0.5:
                print(f'  WARN fixed box at ({x},{y},{w}x{h}) overlaps obstacle ({ox},{oy},{ow},{oh})')
        OBS.append((x, y, w, h))
        return (x, y)
    # --- EIF (Rel-19, blue): peers AF/NEF/UDM/PCF/SMF; bottom of the strip
    ex, ey = fixed_box(328.3, 266.5, 16.5)
    eif = model.add_vertex(label_html('EIF', BLUE), new_box_style(BLUE),
                           X(ex), Y(ey), 16.5 * K, BH * K, cid='add_eif')
    placed['EIF'] = (ex, ey, 0)
    for tgt, lab in ((AF, 'N110'), (NEF, 'N111'), (UDM, 'N112'), (PCF, 'N113'), (SMF, 'N114')):
        model.add_edge(label_html(lab, BLUE), new_edge_style(BLUE),
                       source=eif, target=cell_of[tgt['id']])
    # EIF SBI caption
    cap = model.add_vertex(label_html('29.566 Neif (SBI)', BLUE),
                           'text;html=1;strokeColor=none;fillColor=none;fontFamily=Arial;',
                           X(ex), Y(ey + BH + 0.4), 16.5 * K, 3.4 * K, cid='add_eif_cap')
    # --- Ambient IoT cluster (Rel-19, blue): vertical stack in the strip
    vx, vy = fixed_box(328.3, 239.5, 16.5)
    dev = model.add_vertex(label_html('AIoT Device', BLUE), new_box_style(BLUE),
                           X(vx), Y(vy), 16.5 * K, BH * K, cid='add_aiot_dev')
    placed['AIoT Device'] = (vx, vy, 0)
    ax, ay = fixed_box(328.3, 247.5, 16.5)
    aiotf = model.add_vertex(label_html('AIOTF', BLUE), new_box_style(BLUE),
                             X(ax), Y(ay), 16.5 * K, BH * K, cid='add_aiotf')
    placed['AIOTF'] = (ax, ay, 0)
    dx, dy = fixed_box(328.3, 255.5, 17.0)
    adm = model.add_vertex(label_html('ADM', BLUE), new_box_style(BLUE),
                           X(dx), Y(dy), 17.0 * K, BH * K, cid='add_adm')
    placed['ADM'] = (dx, dy, 0)
    model.add_edge(label_html('AIOT1', BLUE), new_edge_style(BLUE, dashed=True), source=dev, target=aiotf)
    model.add_edge(label_html('AIOT2', BLUE), new_edge_style(BLUE), source=aiotf, target=cell_of[NGRAN['id']])
    model.add_edge(label_html('AIOT3', BLUE), new_edge_style(BLUE), source=aiotf, target=cell_of[AMF['id']])
    model.add_edge(label_html('AIOT4', BLUE), new_edge_style(BLUE), source=aiotf, target=cell_of[NEF['id']])
    model.add_edge(label_html('AIOT5', BLUE), new_edge_style(BLUE), source=aiotf, target=cell_of[NRF['id']])
    model.add_edge(label_html('AIOT6', BLUE), new_edge_style(BLUE), source=aiotf, target=adm)
    model.add_edge(label_html('AIOT7', BLUE), new_edge_style(BLUE), source=adm, target=cell_of[UDR['id']])
    model.add_edge(label_html('AIOT8', BLUE), new_edge_style(BLUE), source=adm, target=cell_of[NEF['id']])
    model.add_vertex(label_html('Naiotf (SBI) / Nadm (SBI)', BLUE),
                     'text;html=1;strokeColor=none;fillColor=none;fontFamily=Arial;',
                     X(dx), Y(dy + BH + 0.4), 17.0 * K, 3.4 * K, cid='add_aiot_cap')
    # --- NCR (Rel-18, green): near NG-RAN / AMF, avoiding the N3 user-plane line
    r = place_box(BW, BH, (95, 240, 185, 300), [centre(NGRAN), centre(AMF)])
    nx, ny = r[1], r[2]
    ncr = model.add_vertex(label_html('NCR', GREEN), new_box_style(GREEN),
                           X(nx), Y(ny), BW * K, BH * K, cid='add_ncr')
    placed['NCR'] = (nx, ny, r[3])
    model.add_edge(label_html('gNB control', GREEN), new_edge_style(GREEN),
                   source=ncr, target=cell_of[NGRAN['id']])
    # --- NR Femto (Rel-19, blue): east of NCR, same avoidance rules
    r = place_box(BW, BH, (150, 240, 330, 300), [centre(NGRAN), centre(AMF), centre(PSAUPF)])
    fx, fy = r[1], r[2]
    femto = model.add_vertex(label_html('NR Femto', BLUE), new_box_style(BLUE),
                             X(fx), Y(fy), BW * K, BH * K, cid='add_femto')
    placed['NR Femto'] = (fx, fy, r[3])
    model.add_edge(label_html('N2', BLUE), new_edge_style(BLUE), source=femto, target=cell_of[AMF['id']])
    model.add_edge(label_html('N3', BLUE), new_edge_style(BLUE), source=femto, target=cell_of[PSAUPF['id']])
    # --- Rel-18 long edges: N89 / N96 from TSCTSF panel item
    model.add_edge(label_html('N89', GREEN), new_edge_style(GREEN),
                   source=cell_of[TSCTSF['id']], target=cell_of[AMF['id']])
    model.add_edge(label_html('N96', GREEN), new_edge_style(GREEN),
                   source=cell_of[TSCTSF['id']], target=cell_of[NRF['id']])
    # --- Rel-19 long edges: N116 / N117 from SCP
    model.add_edge(label_html('N116', BLUE), new_edge_style(BLUE),
                   source=cell_of[SCP['id']], target=cell_of[NWDAF['id']])
    model.add_edge(label_html('N117', BLUE), new_edge_style(BLUE),
                   source=cell_of[SCP['id']], target=cell_of[DCCF['id']])
    # --- N97 / N99 stubs on NSACF (green chips to the right/below)
    nsx, nsy = NSACF['x'] + NSACF['w'] + 1.2, NSACF['y']
    chip_style = ('text;html=1;strokeColor=none;fillColor=none;fontFamily=Arial;align=left;')
    c1 = model.add_vertex(label_html('N97: NSACF in other PLMN', GREEN),
                          chip_style, X(nsx), Y(nsy - 1.5), 34 * K, 3.4 * K, cid='add_n97')
    c2 = model.add_vertex(label_html('N99: NSACF in same PLMN', GREEN),
                          chip_style, X(nsx), Y(nsy + 2.2), 34 * K, 3.4 * K, cid='add_n99')
    model.add_edge('', new_edge_style(GREEN), source=cell_of[NSACF['id']], target=c1)
    model.add_edge('', new_edge_style(GREEN), source=cell_of[NSACF['id']], target=c2)
    # --- Nupf chip on PSA-UPF (green)
    model.add_vertex(label_html('Nupf', GREEN),
                     'rounded=0;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#00B050;'
                     f'fontFamily=Arial;fontSize={5.6 * FS:.1f};fontColor=#00B050;',
                     X(PSAUPF['x'] + PSAUPF['w'] - 8), Y(PSAUPF['y'] - 4.6), 8 * K, 3.6 * K,
                     cid='add_nupf')
    return placed

# ---------------------------------------------------------------- SVG render
def render_svg(render, path, additions_render=None, view=None):
    items = []
    items.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{PAGE_W:.0f}" height="{PAGE_H:.0f}" viewBox="0 0 {PAGE_W:.0f} {PAGE_H:.0f}">')
    items.append('<rect x="0" y="0" width="100%" height="100%" fill="white"/>')
    for it in render:
        if it[0] == 'rect':
            _, x, y, w, h, fill, line, txt = it
            f = f'#{fill}' if fill and fill != 'none' else 'none'
            st = f'#{line}' if line and line != 'none' else 'none'
            items.append(f'<rect x="{x:.0f}" y="{y:.0f}" width="{w:.0f}" height="{h:.0f}" fill="{f}" stroke="{st}" stroke-width="1.5"/>')
            if txt:
                t = escape(txt.split(chr(10))[0][:26])
                items.append(f'<text x="{x + w / 2:.0f}" y="{y + h / 2 + 5:.0f}" font-size="15" text-anchor="middle" font-family="Arial">{t}</text>')
        elif it[0] == 'ellipse':
            _, x, y, w, h, fill, line, txt = it
            f = f'#{fill}' if fill and fill != 'none' else 'none'
            st = f'#{line}' if line and line != 'none' else 'none'
            items.append(f'<ellipse cx="{x + w / 2:.0f}" cy="{y + h / 2:.0f}" rx="{w / 2:.0f}" ry="{h / 2:.0f}" fill="{f}" stroke="{st}" stroke-width="1.5"/>')
            if txt:
                t = escape(txt.split(chr(10))[0][:26])
                items.append(f'<text x="{x + w / 2:.0f}" y="{y + h / 2 + 5:.0f}" font-size="15" text-anchor="middle" font-family="Arial">{t}</text>')
        elif it[0] == 'line':
            _, (x1, y1), (x2, y2), col, dash = it
            da = ' stroke-dasharray="10 6"' if dash else ''
            items.append(f'<line x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" stroke="#{col}" stroke-width="1.3"{da}/>')
        elif it[0] == 'poly':
            _, pts, col = it
            p = ' '.join(f'{a:.0f},{b:.0f}' for a, b in pts)
            items.append(f'<polyline points="{p}" fill="none" stroke="#{col}" stroke-width="1.3"/>')
    if additions_render:
        items.extend(additions_render)
    items.append('</svg>')
    with open(path, 'w') as f:
        f.write('\n'.join(items))

def additions_svg(placed):
    out = []
    widths = {'ADM': 17.0, 'AIoT Device': 16.5, 'AIOTF': 16.5, 'EIF': 16.5}
    for name, (x, y, _c) in placed.items():
        col = GREEN if name == 'NCR' else BLUE
        w = widths.get(name, 13.8)
        out.append(f'<rect x="{X(x):.0f}" y="{Y(y):.0f}" width="{w * K:.0f}" height="{5.8 * K:.0f}" fill="white" stroke="#{col}" stroke-width="4"/>')
        out.append(f'<text x="{X(x + w / 2):.0f}" y="{Y(y + 2.9) + 6:.0f}" font-size="17" font-weight="bold" fill="#{col}" text-anchor="middle" font-family="Arial">{escape(name)}</text>')
    return out

# ---------------------------------------------------------------- validation
def cell_texts(tree):
    texts = []
    for cell in tree.getroot().iter('mxCell'):
        v = cell.get('value') or ''
        t = re.sub(r'<[^>]+>', '\n', v)
        t = t.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
        texts.append((cell.get('id'), t))
    return texts

def validate(tree, label):
    texts = dict()
    for cid, t in cell_texts(tree):
        texts.setdefault(cid, t)
    missing = []
    total = 0
    for s in shapes:
        pt = plain_value(s).strip()
        if not pt:
            continue
        total += 1
        ct = texts.get('o' + s['id'], '')
        norm = lambda z: re.sub(r'\s+', '', z)
        if norm(pt) != norm(ct):
            missing.append((s['id'], pt[:50], ct[:50]))
    print(f'[{label}] original text shapes: {total}, mismatched: {len(missing)}')
    for m in missing[:15]:
        print('   MISMATCH', m)
    return len(missing)

# ---------------------------------------------------------------- main
def header(model, title, sub):
    model.add_vertex(
        f'<div align="left"><font style="font-size:44px"><b>{escape(title)}</b></font></div>',
        'text;html=1;strokeColor=none;fillColor=none;fontFamily=Arial;',
        30, 18, 2400, 55, cid='hdr_title')
    model.add_vertex(
        f'<div align="left"><font color="#404040" style="font-size:22px">{escape(sub)}</font></div>',
        'text;html=1;strokeColor=none;fillColor=none;fontFamily=Arial;',
        30, 74, 3000, 34, cid='hdr_sub')

def footer_notes(model):
    y = OY + SLIDE_H_MM * K + 26
    model.add_vertex(
        '<div align="left"><font color="#00B050" style="font-size:20px"><b>Release-18 additions (green):</b> '
        'N89 (TSCTSF-AMF), N96 (TSCTSF-NRF), N97/N99 (NSACF inter/intra-PLMN), Nupf (UPF SBI), NCR (TS 38.300 Cl.4.9); '
        'functional additions: 5.47 NCR, 5.20b-d, 5.28a, 5.35A MBSR, 5.43-5.46, eRedCap, DetNet, XR.</font></div>',
        'text;html=1;strokeColor=none;fillColor=none;fontFamily=Arial;whiteSpace=wrap;verticalAlign=top;',
        30, y, 3260, 62, cid='ftr_r18')
    model.add_vertex(
        '<div align="left"><font color="#0070C0" style="font-size:20px"><b>Release-19 additions (blue):</b> '
        'EIF (TS 23.501 Cl.6.2.34) with N110-N114 and Neif; N116 (SCP-NWDAF), N117 (SCP-DCCF), Nscp; '
        'Ambient IoT: AIOTF / ADM / AIoT Device with AIOT1-AIOT8 (TS 23.369); NR Femto (Cl.5.50); '
        'functional additions: 4.2.18 EE architecture, 5.48, 5.49 MWAB, 5.51, 5.52, sidelink multi-hop, LP-WUS/WUR, SBFD, AI/ML for NR air interface.</font></div>',
        'text;html=1;strokeColor=none;fillColor=none;fontFamily=Arial;whiteSpace=wrap;verticalAlign=top;',
        30, y + 68, 3260, 62, cid='ftr_r19')
    model.add_vertex(
        '<div align="left"><font color="#404040" style="font-size:20px"><b>Colour note:</b> '
        'inside the original figure, green already means Release-16 and blue Release-17; the Release-18 (green) / '
        'Release-19 (blue) additions reuse the same hues by series policy. Added elements are the ones listed above '
        'and in composite-drawio-notes.md. This is a DRAFT for review.</font></div>',
        'text;html=1;strokeColor=none;fillColor=none;fontFamily=Arial;whiteSpace=wrap;verticalAlign=top;',
        30, y + 136, 3260, 62, cid='ftr_note')

def main():
    # master: faithful reproduction
    m1 = Model()
    header(m1, '3GPP Overall Architecture and Specifications',
           'draw.io master — faithful, editable reproduction of the original figure (up to Release-17). '
           'Generated by script from the original pptx; do not edit positions by hand without updating the generator.')
    r1 = build_original(m1, jumps=False)
    t1 = m1.to_xml('Master (original, Rel-17)')
    t1.write(BASE + '/composite-diagram-drawio-master.drawio', encoding='unicode', xml_declaration=True)
    render_svg(r1, BASE + '/work/render_master.svg')
    validate(t1, 'master')

    # composite: + Rel-18/19 integrated
    cell_of.clear()
    m2 = Model()
    header(m2, '3GPP Overall Architecture and Specifications — Composite (Release-19 cumulative)',
           'DRAFT composite: original figure (up to Release-17) + Release-18 (green) + Release-19 (blue) additions '
           'integrated into the figure. Based on TS 23.501 V19.9.0 / TS 23.369 V19.5.0 / TS 38.300.')
    r2 = build_original(m2, jumps=True)
    placed = build_additions(m2, r2)
    footer_notes(m2)
    t2 = m2.to_xml('Composite (Rel-19 cumulative)')
    t2.write(BASE + '/composite-diagram-drawio.drawio', encoding='unicode', xml_declaration=True)
    render_svg(r2, BASE + '/work/render_composite.svg', additions_svg(placed))
    validate(t2, 'composite')
    print('placed additions:', placed)

if __name__ == '__main__':
    main()
