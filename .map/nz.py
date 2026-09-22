# -*- coding: utf-8 -*-
"""Generates the static inline-SVG map for the New Zealand book — the North Island, the road
routes and every pin. index.html stays the source of truth: this writes markup you paste into it,
there is no build step at runtime.

Days 1-4 all happen inside Auckland and days 5-6 cross the island, so the map is one frame that
pinch-zooms (picking a day fits the view to that day's stops) rather than a set of fixed frames.
That is why the coastline is simplified far finer than the overview needs.

The window stops at lat -40.45, just north of Cook Strait: the trip never goes further south, and
the South Island would otherwise clip into the corner as a meaningless tangle.

It needs two fetched inputs next to it. Neither ships to the browser, and both come from an
in-page fetch() in the chrome-devtools MCP:

  .map/nz_coast.json   OSM coastline ways, as [[[lat,lon],...],...]
    POST https://overpass-api.de/api/interpreter  with
      [out:json][timeout:300];way["natural"="coastline"](<s>,<w>,<n>,<e>);out geom;
    over six tiles covering lat -41.8..-34.2, lon 172.3..179.0, deduped by way id. One query for
    the whole island times out.

  .map/nz_legs.json    one OSRM driving route per leg, keyed "d<day>-<leg>", as {t,km,geom}
    GET https://router.project-osrm.org/route/v1/driving/<lon,lat>;<lon,lat>?overview=simplified&geometries=geojson
    for each consecutive pair of DAYS[] stops that is not a walk or a ferry.
    OSRM's per-leg minutes are also how the itinerary drive times were set.

Then:  python3 .map/nz.py   ->  .map/nz.svg.html and .map/nz.lists.html
and splice those into index.html, over the <svg class="map"> block and the six
<ul class="tl stoplist"> blocks in the New Zealand guide. Bump CACHE in sw.js afterwards.
"""
import json, math

LAT0, LAT1 = -40.45, -34.30
LON0, LON1 = 172.40, 178.90
WIDTH = 692
# Tolerances are in user units, where one unit is about 820 m. Fine enough that the coast still
# reads as a coast at the deepest zoom a day fit reaches (Auckland, roughly 12x).
COAST_TOL = 0.16
ROUTE_TOL = 0.25
MIN_AREA = 0.5              # drop specks smaller than this, in user units squared
# Which way round the frame edge a chain closes decides whether the fill lands on the coast's
# land side or its sea side, so it is checked against known points rather than OSM's winding.
LAND_PT = (-36.90939, 174.68405)                    # New Lynn
SEA_PTS = [(-37.00, 173.00), (-35.50, 177.50)]      # Tasman Sea, Pacific

K = math.cos(math.radians((LAT0 + LAT1) / 2))
SC = WIDTH / ((LON1 - LON0) * K)
HEIGHT = round((LAT1 - LAT0) * SC)


def prj(lat, lon):
    return ((lon - LON0) * K * SC, (LAT1 - lat) * SC)


def dp(pts, tol):
    """Douglas-Peucker, iterative so a 360k-point coastline cannot blow the stack."""
    if len(pts) < 3:
        return pts
    keep = [False] * len(pts)
    keep[0] = keep[-1] = True
    stack = [(0, len(pts) - 1)]
    while stack:
        a, b = stack.pop()
        (x1, y1), (x2, y2) = pts[a], pts[b]
        dx, dy = x2 - x1, y2 - y1
        n = math.hypot(dx, dy)
        mi, md = -1, 0.0
        for i in range(a + 1, b):
            x, y = pts[i]
            d = abs(dy * (x - x1) - dx * (y - y1)) / n if n else math.hypot(x - x1, y - y1)
            if d > md:
                mi, md = i, d
        if md > tol:
            keep[mi] = True
            stack += [(a, mi), (mi, b)]
    return [p for p, k in zip(pts, keep) if k]


def path(pts, close=False):
    return 'M' + 'L'.join('%.1f %.1f' % p for p in pts) + ('Z' if close else '')


def area(ring):
    a = 0.0
    for i in range(len(ring)):
        (x1, y1), (x2, y2) = ring[i], ring[(i + 1) % len(ring)]
        a += x1 * y2 - x2 * y1
    return abs(a) / 2


# ---------------------------------------------------------------- land
# Overpass hands back ways cut at the tile edges, so the mainland arrives as open chains. Islands
# close on their own; the open ones are joined up along the frame edge.
def chains(ways):
    """Stitch ways end-to-end into the longest chains they will form."""
    from collections import defaultdict
    start = defaultdict(list)
    for i, w in enumerate(ways):
        start[tuple(w[0])].append(i)
    used = [False] * len(ways)
    out = []
    for i, w in enumerate(ways):
        if used[i]:
            continue
        ch = list(w)
        used[i] = True
        while True:
            nxt = [j for j in start.get(tuple(ch[-1]), []) if not used[j]]
            if not nxt:
                break
            j = nxt[0]
            used[j] = True
            ch.extend(ways[j][1:])
        out.append(ch)
    return out


CORNERS = [(0.0, 0.0), (WIDTH, 0.0), (WIDTH, HEIGHT), (0.0, HEIGHT)]


def edge_t(p):
    """Where a point on the frame edge sits, 0..4 clockwise from the top-left corner."""
    x, y = p
    if abs(y) < 1e-6:
        return x / WIDTH
    if abs(x - WIDTH) < 1e-6:
        return 1 + y / HEIGHT
    if abs(y - HEIGHT) < 1e-6:
        return 2 + (WIDTH - x) / WIDTH
    return 3 + (HEIGHT - y) / HEIGHT


def inside(p):
    return 0 <= p[0] <= WIDTH and 0 <= p[1] <= HEIGHT


def clip(ring):
    """Sutherland-Hodgman against the frame, so a ring that leaves the window is trimmed to it
    instead of carrying hundreds of points nobody will ever see."""
    m = 20.0                                      # a little slack, so edges land off-canvas
    for keep, at in (
        (lambda p: p[0] >= -m, lambda a, b: (-m, a[1] + (b[1] - a[1]) * (-m - a[0]) / (b[0] - a[0]))),
        (lambda p: p[0] <= WIDTH + m, lambda a, b: (WIDTH + m, a[1] + (b[1] - a[1]) * (WIDTH + m - a[0]) / (b[0] - a[0]))),
        (lambda p: p[1] >= -m, lambda a, b: (a[0] + (b[0] - a[0]) * (-m - a[1]) / (b[1] - a[1]), -m)),
        (lambda p: p[1] <= HEIGHT + m, lambda a, b: (a[0] + (b[0] - a[0]) * (HEIGHT + m - a[1]) / (b[1] - a[1]), HEIGHT + m)),
    ):
        out = []
        for i in range(len(ring)):
            a, b = ring[i], ring[(i + 1) % len(ring)]
            ka, kb = keep(a), keep(b)
            if ka:
                out.append(a)
            if ka != kb:
                out.append(at(a, b))
        ring = out
        if not ring:
            return []
    return ring


def crossings(a, b):
    """Where segment a->b crosses the frame edge, in order along a->b."""
    ts = []
    for hi, i in ((WIDTH, 0), (HEIGHT, 1)):
        for v in (0.0, hi):
            if a[i] != b[i]:
                t = (v - a[i]) / (b[i] - a[i])
                if 0 <= t <= 1:
                    p = (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
                    if -1e-6 <= p[0] <= WIDTH + 1e-6 and -1e-6 <= p[1] <= HEIGHT + 1e-6:
                        ts.append((t, (min(max(p[0], 0), WIDTH), min(max(p[1], 0), HEIGHT))))
    ts.sort()
    return [p for _, p in ts]


def cut(chain):
    """Split a projected polyline into the runs inside the frame, each starting and ending on the
    edge where it enters and leaves."""
    runs, cur = [], []
    for k in range(len(chain) - 1):
        a, b = chain[k], chain[k + 1]
        ia, ib = inside(a), inside(b)
        if ia:
            cur.append(a)
        if ia and not ib:
            x = crossings(a, b)
            if x:
                cur.append(x[0])
            runs.append(cur)
            cur = []
        elif not ia and ib:
            x = crossings(a, b)
            cur = [x[-1]] if x else []
        elif not ia and not ib:
            x = crossings(a, b)                   # a chord straight across the frame
            if len(x) >= 2:
                runs.append([x[0], x[-1]])
    if inside(chain[-1]):
        cur.append(chain[-1])
    if cur:
        runs.append(cur)
    return [r for r in runs if len(r) >= 2]


def land():
    """OSM coastline ways -> filled land rings. With the whole island fetched, the mainland
    stitches into one closed ring and is simply clipped to the frame. Any chain left open (a gap
    in the data) is closed along the frame edge instead, and LAND_PT then decides which way round
    to walk, since OSM's winding is not to be trusted."""
    closed, open_ = [], []
    for ch in chains(json.load(open('.map/nz_coast.json'))):
        pts = [prj(la, lo) for la, lo in ch]
        if ch[0] == ch[-1]:
            r = clip(pts) if any(inside(p) for p in pts) else []
            if len(r) >= 3 and area(r) >= MIN_AREA:
                closed.append(r)
            continue
        open_ += cut(pts)

    def join(direction):
        runs = list(open_)
        rings, guard = [], 0
        while runs and guard < 20000:
            guard += 1
            ring = list(runs.pop(0))
            while guard < 20000:
                guard += 1
                te = edge_t(ring[-1])

                def ahead(p):                     # how far round the edge p sits, walking on
                    return ((edge_t(p) - te) * direction) % 4

                best, bd = None, 9e9
                for r in runs:
                    d = ahead(r[0])
                    if d < bd:
                        best, bd = r, d
                if best is None or ahead(ring[0]) <= bd:   # closing on itself is nearest: done
                    tgt, nxt = ahead(ring[0]), None
                else:
                    tgt, nxt = bd, best
                for c in sorted(range(4), key=lambda c: ahead(CORNERS[c])):
                    if 0 < ahead(CORNERS[c]) < tgt:
                        ring.append(CORNERS[c])
                if nxt is None:
                    rings.append(ring)
                    break
                runs.remove(nxt)
                ring += nxt
        return rings

    def covers(rings, p):
        n = 0
        for r in rings:
            for i in range(len(r)):
                (x1, y1), (x2, y2) = r[i], r[(i + 1) % len(r)]
                if (y1 > p[1]) != (y2 > p[1]) and p[0] < x1 + (p[1] - y1) / (y2 - y1) * (x2 - x1):
                    n += 1
        return n % 2 == 1

    def right_way(rings):
        return (covers(rings, prj(*LAND_PT))
                and not any(covers(rings, prj(*p)) for p in SEA_PTS))

    rings = []
    if open_:
        rings = join(1)
        if not right_way(rings + closed):
            rings = join(-1)
            assert right_way(rings + closed), 'edge closing put the fill on the sea both ways round'
    rings = [r for r in rings if area(r) >= MIN_AREA] + closed
    rings.sort(key=lambda r: -area(r))
    return [path(dp(r, COAST_TOL), True) for r in rings]


# ---------------------------------------------------------------- places
def mins(hhmm):
    h, m = hhmm.split(':')
    return int(h) * 60 + int(m)


NL   = ('New Lynn', 'ニューリン', -36.90939, 174.68405)   # the base, named by suburb, not by address
AKL  = ('Auckland Airport', 'オークランド空港', -37.00820, 174.78500)
MATI = ('Matiatia Wharf', 'マティアティア埠頭', -36.78250, 175.00550)
FERR = ('Downtown Ferry Terminal', 'ダウンタウン・フェリーターミナル', -36.84320, 174.76770)
MANG = ('Mangorei Track trailhead', 'マンゴレイ・トラック登山口', -39.20365, 174.05618)
NP   = ('New Plymouth', 'ニュープリマス', -39.05560, 174.07520)

# day stops: (time, en, ja, lat, lon) — English is the markup, Japanese goes in data-ja
DAYS = {
 1: [('09:00',) + AKL,
     ('11:00',) + NL,
     ('12:15', 'Daily Bread, New Lynn', 'Daily Bread ニューリン店', -36.90738, 174.69136),
     ('14:00', 'Cornwall Park', 'コーンウォール・パーク', -36.89745, 174.78431),
     ('15:15', 'One Tree Hill', 'ワンツリーヒル', -36.90494, 174.78957),
     ('17:00',) + NL],
 2: [('09:30',) + NL,
     ('10:00', 'Crushes', 'Crushes', -36.85754, 174.75926),
     ('11:00', 'Porter James', 'Porter James', -36.86323, 174.75973),
     ('11:45', 'Hard To Find Books', 'Hard To Find Books', -36.86166, 174.76252),
     ('13:00', 'MIBO', 'MIBO', -36.86918, 174.76319),
     ('14:30', 'Outdoors Society', 'Outdoors Society', -36.87069, 174.76106),
     ('16:00',) + NL],
 3: [('08:15',) + NL,
     ('08:40', "Parnell Farmers' Market", 'パーネル・ファーマーズマーケット', -36.86331, 174.78006),
     ('10:00', 'Domain Wintergardens', 'ドメイン・ウィンターガーデン', -36.86024, 174.77409),
     ('11:45', 'Kauri Glen Reserve', 'カウリ・グレン保護区', -36.80625, 174.73482),
     ('13:15', 'Daily Bread, Belmont', 'Daily Bread ベルモント店', -36.80381, 174.78347),
     ('15:00', 'Takarunga / Mount Victoria', 'タカルンガ／マウント・ビクトリア', -36.82638, 174.79902),
     ('17:30',) + NL],
 4: [('08:30',) + NL,
     ('09:00',) + FERR,
     ('10:15',) + MATI,
     ('10:45', 'Allpress Olive Groves', 'Allpress オリーブ農園', -36.80943, 175.06142),
     ('12:30', 'Batch Winery', 'Batch ワイナリー', -36.81462, 175.08318),
     ('15:15',) + MATI,
     ('16:30',) + FERR,
     ('17:30', 'Amano, Britomart', 'Amano ブリトマート店', -36.84441, 174.77046),
     ('19:45',) + NL],
 5: [('07:00',) + NL,
     ('09:45', 'Waitomo Glowworm Caves', 'ワイトモ鍾乳洞', -38.26070, 175.10361),
     ('15:15',) + NP],
 6: [('04:00',) + NP,
     ('04:25',) + MANG,
     ('06:45', 'Pouākai Tarns', 'ポウアカイ・ターン', -39.24930, 174.05300),
     ('10:00',) + MANG,
     ('10:45',) + NP,
     ('17:45',) + AKL],
}
# leg kinds by (day, destination index) — everything else is a driving route from OSRM
KIND = {(1, 4): 'walk',
        (2, 2): 'walk', (2, 3): 'walk', (2, 4): 'walk', (2, 5): 'walk',
        (3, 2): 'walk',
        (4, 2): 'boat', (4, 6): 'boat', (4, 7): 'walk',
        (6, 2): 'walk', (6, 3): 'walk'}


# ---------------------------------------------------------------- output
def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')


def lab(x, y, en, ja):
    """label text element, flipped to the left of the pin when the pin sits on the right. The gap
    from pin to label is a CSS translate, so it holds its size on screen at any zoom."""
    a = ' text-anchor="end"' if x > WIDTH * 0.45 else ''
    return '<text class="lab"%s x="%.1f" y="%.1f" data-ja="%s">%s</text>' % (a, x, y, esc(ja), esc(en))


legs = json.load(open('.map/nz_legs.json'))
out = ['<svg class="map" viewBox="0 0 %d %d" role="img">' % (WIDTH, HEIGHT),
       '<title data-ja="ニュージーランド北島 &mdash; 走るルートと立ち寄り先">New Zealand North Island '
       '&mdash; our route and the stops on it</title>']
out.append('<rect class="sea" width="%d" height="%d"/>' % (WIDTH, HEIGHT))
paths = land()
out.append('<g class="land">\n' + '\n'.join('<path d="%s"/>' % d for d in paths) + '\n</g>')

rt = []
for d, stops in DAYS.items():
    for i in range(1, len(stops)):
        kind = KIND.get((d, i), '')
        m = mins(stops[i][0])
        cls = 'leg d%d%s' % (d, ' ' + kind if kind else '')
        if kind:                                  # a ferry or a walk draws straight
            a, b = stops[i - 1], stops[i]
            pts = [prj(a[3], a[4]), prj(b[3], b[4])]
        else:
            pts = dp([prj(*p) for p in legs['d%d-%d' % (d, i - 1)]['geom']], ROUTE_TOL)
        rt.append('<path class="%s" data-day="%d" data-min="%d" d="%s"/>' % (cls, d, m, path(pts)))
out.append('<g class="routes">\n' + '\n'.join(rt) + '\n</g>')

sp = []
for d, stops in DAYS.items():
    for i, (t, en, ja, la, lo) in enumerate(stops):
        x, y = prj(la, lo)
        sp.append('<g class="pin stop d%d" data-day="%d" data-i="%d" data-min="%d">'
                  '<circle class="hit" cx="%.1f" cy="%.1f" r="24"/>'
                  '<circle class="ring" cx="%.1f" cy="%.1f" r="20"/>'
                  '<circle class="mk" cx="%.1f" cy="%.1f" r="11"/>%s</g>'
                  % (d, d, i, mins(t), x, y, x, y, x, y, lab(x, y, en, ja)))
out.append('<g class="stops">\n' + '\n'.join(sp) + '\n</g>')
out.append('</svg>')
svg = '\n'.join(out)

lists = []
for d, stops in DAYS.items():
    rows = []
    for i, (t, en, ja, la, lo) in enumerate(stops):
        rows.append('<li data-i="%d" data-min="%d" tabindex="0" role="button">'
                    '<span class="time">%s</span><span class="dot"></span>'
                    '<span class="txt" data-ja="%s">%s</span></li>'
                    % (i, mins(t), t, esc(ja), esc(en)))
    lists.append('      <ul class="tl stoplist d%d" data-day="%d">\n        %s\n      </ul>'
                 % (d, d, '\n        '.join(rows)))

open('.map/nz.svg.html', 'w').write(svg)
open('.map/nz.lists.html', 'w').write('\n'.join(lists))
print('viewBox %d x %d' % (WIDTH, HEIGHT))
print('land rings %d  legs %d  pins %d' % (len(paths), len(rt), len(sp)))
print('svg %d KB  lists %d KB' % (len(svg) / 1024, sum(map(len, lists)) / 1024))
for d, s in DAYS.items():
    print('day %d  %s -> %s  (%d stops)' % (d, s[0][0], s[-1][0], len(s)))
