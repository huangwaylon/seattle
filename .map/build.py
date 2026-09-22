# -*- coding: utf-8 -*-
"""Generates the static inline-SVG map (#view-map in index.html) — the island, the road
routes and all 67 pins. index.html stays the source of truth: this writes markup you paste
into it, there is no build step at runtime.

It needs two fetched inputs next to it. Neither ships to the browser, and both come from an
in-page fetch() in the chrome-devtools MCP (curl/WebFetch are blocked by the sandbox):

  .map/coast.json   OSM coastline ways, as [[[lat,lon],...],...]
    POST https://overpass-api.de/api/interpreter  with
      data=[out:json][timeout:120];way["natural"="coastline"](25.95,127.5,26.95,128.45);out geom;
    then  d.elements.filter(e=>e.geometry).map(e=>e.geometry.map(p=>[+p.lat.toFixed(5),+p.lon.toFixed(5)]))

  .map/legs.json    one OSRM driving route per leg, keyed "d<day>-<leg>", as {t,km,geom}
    GET https://router.project-osrm.org/route/v1/driving/<lon,lat>;<lon,lat>?overview=full&geometries=geojson
    for each consecutive pair of DAYS[] stops below (skipping the two boat legs).
    OSRM's per-leg minutes are also how the itinerary drive times were checked.

Then:  python3 .map/build.py   ->  .map/map.svg.html and .map/map.lists.html
and splice those into index.html, replacing the <svg class="map">...</svg> block and the
three <ul class="tl stoplist"> blocks. Bump CACHE in sw.js afterwards.
"""
import json, math

# The lon window is widened past what the island needs so the frame comes out 692x824, the same
# shape as the New Zealand map — both map cards then sit the same height on screen.
LAT0,LAT1 = 26.055, 26.895
LON0,LON1 = 127.586, 128.374
K  = math.cos(math.radians((LAT0+LAT1)/2))
H  = 824.0
SC = H/(LAT1-LAT0)
W  = round((LON1-LON0)*K*SC)
def prj(lat,lon): return ((lon-LON0)*K*SC, (LAT1-lat)*SC)
def dp(pts,tol):
    import sys; sys.setrecursionlimit(80000)
    if len(pts)<3: return pts
    def rec(a,b):
        (x1,y1),(x2,y2)=pts[a],pts[b]; dx,dy=x2-x1,y2-y1; n=math.hypot(dx,dy)
        mi,md=-1,0.0
        for i in range(a+1,b):
            x,y=pts[i]
            d=abs(dy*(x-x1)-dx*(y-y1))/n if n else math.hypot(x-x1,y-y1)
            if d>md: mi,md=i,d
        return rec(a,mi)[:-1]+rec(mi,b) if md>tol else [pts[a],pts[b]]
    return rec(0,len(pts)-1)
def path(pts,close=False):
    return 'M'+'L'.join('%.1f %.1f'%p for p in pts)+('Z' if close else '')

# ---------------------------------------------------------------- land
ways=json.load(open('.map/coast.json'))
from collections import defaultdict
st=defaultdict(list)
for i,w in enumerate(ways): st[tuple(w[0])].append(i)
used=[False]*len(ways); rings=[]
for i,w in enumerate(ways):
    if used[i]: continue
    ch=list(w); used[i]=True
    while True:
        nx=[j for j in st.get(tuple(ch[-1]),[]) if not used[j]]
        if not nx: break
        j=nx[0]; used[j]=True; ch.extend(ways[j][1:])
    if ch[0]==ch[-1]: rings.append(ch)
def area(r):
    a=0.0
    for k in range(len(r)-1):
        (x1,y1),(x2,y2)=prj(*r[k]),prj(*r[k+1]); a+=x1*y2-x2*y1
    return abs(a)/2
isl=[]
for r in rings:
    la=[p[0] for p in r]; lo=[p[1] for p in r]
    if max(la)<LAT0 or min(la)>LAT1 or max(lo)<LON0 or min(lo)>LON1: continue
    a=area(r)
    if a>=18: isl.append((a,r))
isl.sort(key=lambda t:-t[0])
land=[path(dp([prj(*p) for p in r], 1.8 if a>1e5 else 1.1), True) for a,r in isl]

# ---------------------------------------------------------------- places
def mins(hhmm):
    h,m=hhmm.split(':'); return int(h)*60+int(m)
# day stops: (time, ja, en, lat, lon)
DAYS={
 1:[('08:55','那覇空港','Naha Airport',26.19670,127.64895),
    ('10:45','沖縄北IC','Okinawa Kita IC',26.37480,127.82040),
    ('11:00','Evertrail営業所','Evertrail office',26.38051,127.82639),
    ('11:55','キングタコス金武','King Tacos, Kin',26.45328,127.91728),
    ('13:05','万座毛','Cape Manzamo',26.50501,127.85026),
    ('14:45','フンガー滝','Hunga Falls',26.60810,128.05392),
    ('16:05','名護 買い出し','Nago groceries',26.60700,127.97942),
    ('16:50','キャンプ 屋我地','Camp, Yagaji',26.64820,128.03368)],
 2:[('06:25','キャンプ 屋我地','Camp, Yagaji',26.64820,128.03368),
    ('08:00','DIVENUTS 瀬底','Dive Nuts, Sesoko',26.64200,127.86300),
    ('09:00','水納島 シュノーケル','Minna Island, snorkel',26.64767,127.81791),
    ('13:10','百年古家 大家','Ufuya',26.62100,127.96367),
    ('14:30','みるくふぁーむカフェ','Okinawa Milk Farm Cafe',26.60526,127.97327),
    ('15:30','名護 買い出し','Nago groceries',26.60700,127.97942),
    ('16:20','キャンプ 屋我地','Camp, Yagaji',26.64820,128.03368)],
 3:[('07:30','キャンプ 屋我地','Camp, Yagaji',26.64820,128.03368),
    ('09:15','残波岬','Cape Zanpa',26.44050,127.71192),
    ('10:15','瀬名波ビーチ','Senaha Beach',26.42465,127.73394),
    ('11:00','バンタカフェ','Banta Cafe',26.41771,127.71400),
    ('13:50','具志川城跡 秘境プール','Gushikawa tide pool',26.08036,127.66452),
    ('16:45','Evertrail営業所 返却','Evertrail office, car back',26.38051,127.82639),
    ('17:05','沖縄北IC','Okinawa Kita IC',26.37480,127.82040),
    ('18:25','那覇空港','Naha Airport',26.19670,127.64895)],
}
# leg kinds by (day, destination index)
KIND={(1,1):'bus',(1,2):'walk',(2,2):'boat',(2,3):'boat',(3,6):'walk',(3,7):'bus'}

CAMPS=[('勝連ビーチ','Katsuren Beach',26.32630,127.87750),
 ('沖縄県民の森',"Okinawa Prefectural People's Forrest",26.51170,127.90640),
 ('幸喜の野営地','Koki Camp Spot',26.54360,127.96000),
 ('名護城橋の野営地','Nago Castle Bridge Spot',26.58686,127.99276),
 ('NEOSアウトドアパーク','NEOS Outdoor Park',26.14820,127.80390),
 ('あざまサンサンビーチ','Azama Sun Beach Camping Ground',26.17800,127.82920),
 ('北名城ビーチ','Kita Nashiro Beach',26.10800,127.66160),
 ('久手堅ビーチ','Kudeken Beach',26.16620,127.82560),
 ('ベースキャンプ','Base Camp',26.61681,127.93812),
 ('屋我地ビーチ キャンプ場','Yagaji Beach Campsite',26.64820,128.03368),
 ('稲嶺の野営地','Inamine Camp Spot',26.63460,128.05000),
 ('屋我地島の野営地','Yagajima Spot',26.65472,128.03404),
 ('平南橋','Henan Bridge',26.64990,128.08770),
 ('津波ビーチの野営地','Tsuha Beach Camp Spot',26.66150,128.10150),
 ('渡野喜屋キャンプ場','Tonokiya Campsite',26.66378,128.10874),
 ('古宇利島キャンプ場','Kouri Island Camp Ground',26.70850,128.01800),
 ('大保川キャンプ場','Daiboo River Camp',26.65352,128.14329),
 ('福地川海浜公園','Fukuchi River Seaside Park',26.63160,128.15860),
 ('コキョウノビーチ','Kokyono Beach',26.74660,128.17200),
 ('辺土名の野営地','Hentona Camp Spot',26.75060,128.18490),
 ('奥間の山あい','Okuma Mountains',26.72960,128.19040),
 ('辺野喜の野営地','Benoki Camp Spot',26.79850,128.23210),
 ('やんばる学びの森','Yanbaru Discovery Forest',26.72350,128.26490),
 ('安波（やんばる）','Aha, Yanbaru',26.71590,128.29390),
 ('奥のビーチロード','Oku Beach Road',26.84620,128.28570),
 ('アダンビーチ キャンプ場','Adan Beach Campsite',26.82100,128.31350)]

NATURE=[('比地大滝','Hiji Falls',26.71053,128.18661),
 ('ター滝','Ta Falls',26.63136,128.09272),
 ('茅打バンタ','Kayauchi Banta',26.85432,128.24978),
 ('辺戸岬','Cape Hedo',26.87197,128.26564),
 ('ゴリラチョップ','Gorilla Chop',26.63703,127.88235),
 ('ふれあいヒルギ公園','Yagaji mangroves',26.60399,128.14484),
 ('ダイヤモンドビーチ','Diamond Beach',26.50675,127.87912),
 ('古宇利島','Kouri Island',26.70730,128.01817),
 ('備瀬のフクギ並木','Bise Fukugi tree road',26.70159,127.88022)]

FOOD=[('新垣ぜんざい屋','Aragaki Zenzai',26.66063,127.89583),
 ('きしもと食堂','Kishimoto Shokudo',26.66032,127.89590),
 ('ひがし食堂','Higashi Shokudo',26.58881,127.98866),
 ('三矢 道の駅許田店','Mitsuya, Kyoda',26.55201,127.96999),
 ('琉冰 おんなの駅','Ryupin, Onna',26.43624,127.79470),
 ('鶴亀堂ぜんざい','Tsurukamedo',26.40620,127.74229),
 ('氷ヲ刻メ','Kori wo Kizame',26.32752,127.75176),
 ('花人逢','Kajinho',26.66859,127.90082),
 ('cafe CAHAYA BULAN','Cafe Cahaya Bulan',26.70213,127.87989),
 ('亜熱帯茶屋','Anettai Chaya',26.66711,127.90033),
 ('バンタカフェ','Banta Cafe',26.41772,127.71401)]

# ---------------------------------------------------------------- output
def esc(s): return s.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;').replace('"','&quot;')
def lab(x,ja,en,dy):
    """label text element, flipped to the left half when the pin sits on the right. The gap from
    pin to label is a CSS translate, so it holds its size on screen at any zoom."""
    a=' text-anchor="end"' if x > W*0.45 else ''
    return '<text class="lab"%s x="%.1f" y="%.1f" data-en="%s">%s</text>'%(a,x,dy,esc(en),esc(ja))

out=[]
out.append('<svg class="map" viewBox="0 0 %d %d" role="img" aria-labelledby="mapTitle">'%(W,H))
out.append('<title id="mapTitle" data-en="Okinawa main island: our route and the places on it">沖縄本島 &mdash; 走るルートと立ち寄り先</title>')
out.append('<rect class="sea" width="%d" height="%d"/>'%(W,H))
out.append('<g class="land">\n'+'\n'.join('<path d="%s"/>'%d for d in land)+'\n</g>')

# routes
legs=json.load(open('.map/legs.json'))
rt=[]
for d,stops in DAYS.items():
    for i in range(1,len(stops)):
        kind=KIND.get((d,i),'')
        dest=stops[i]; m=mins(dest[0])
        cls='leg d%d%s'%(d,' '+kind if kind else '')
        if kind in ('boat','walk'):
            # straight line: the boat out to Minna and back, and the walk to the bus stop
            a,b = ((stops[1],stops[2]) if i==2 else (stops[2],stops[1])) if kind=='boat' else (stops[i-1],dest)
            pts=[prj(a[3],a[4]),prj(b[3],b[4])]
            rt.append('<path class="%s" data-day="%d" data-min="%d" d="%s"/>'%(cls,d,m,path(pts)))
            continue
        key='d%d-%d'%(d,i-1)
        if key not in legs:   # minna -> ufuya: boat back, then drive from the shop
            continue
        pts=dp([prj(*p) for p in legs[key]['geom']],1.2)
        rt.append('<path class="%s" data-day="%d" data-min="%d" d="%s"/>'%(cls,d,m,path(pts)))
# day2 leg 3 (minna -> ufuya) is the boat back plus the drive from the shop
d2=DAYS[2]; m=mins(d2[3][0])
pts=dp([prj(*p) for p in legs['d2-2']['geom']],1.2)
rt.append('<path class="leg d2" data-day="2" data-min="%d" d="%s"/>'%(m,path(pts)))
out.append('<g class="routes">\n'+'\n'.join(rt)+'\n</g>')

# candidate pins
def cand(items,cls,shape):
    g=[]
    for ja,en,la,lo in items:
        x,y=prj(la,lo)
        g.append('<g class="pin %s">'
                 '<circle class="hit" cx="%.1f" cy="%.1f" r="22"/>'
                 '<circle class="ring" cx="%.1f" cy="%.1f" r="17"/>%s%s</g>'
                 %(cls,x,y,x,y,shape(x,y),lab(x,ja,en,y)))
    return '\n'.join(g)+'\n'
sq   =lambda x,y:'<rect class="mk" x="%.1f" y="%.1f" width="11" height="11"/>'%(x-5.5,y-5.5)
tri  =lambda x,y:'<path class="mk" d="M%.1f %.1fL%.1f %.1fL%.1f %.1fZ"/>'%(x,y-7,x+6.4,y+4.5,x-6.4,y+4.5)
di   =lambda x,y:'<rect class="mk" x="-5" y="-5" width="10" height="10" transform="translate(%.1f %.1f) rotate(45)"/>'%(x,y)
out.append('<g class="cands">\n')
out.append(cand(CAMPS,'p-camp',sq))
out.append(cand(NATURE,'p-nature',tri))
out.append(cand(FOOD,'p-food',di))
out.append('</g>')

# stop pins
sp=[]
for d,stops in DAYS.items():
    for i,(t,ja,en,la,lo) in enumerate(stops):
        x,y=prj(la,lo)
        sp.append('<g class="pin stop d%d" data-day="%d" data-i="%d" data-min="%d">'
                  '<circle class="hit" cx="%.1f" cy="%.1f" r="24"/>'
                  '<circle class="ring" cx="%.1f" cy="%.1f" r="20"/>'
                  '<circle class="mk" cx="%.1f" cy="%.1f" r="11"/>%s</g>'
                  %(d,d,i,mins(t),x,y,x,y,x,y,lab(x,ja,en,y)))
out.append('<g class="stops">\n'+'\n'.join(sp)+'\n</g>')
out.append('</svg>')
svg='\n'.join(out)

# stop lists
lists=[]
for d,stops in DAYS.items():
    rows=[]
    for i,(t,ja,en,la,lo) in enumerate(stops):
        rows.append('<li data-i="%d" data-min="%d" tabindex="0" role="button">'
                    '<span class="time">%s</span><span class="dot"></span>'
                    '<span class="txt" data-en="%s">%s</span></li>'%(i,mins(t),t,esc(en),esc(ja)))
    lists.append('      <ul class="tl stoplist d%d" data-day="%d">\n        %s\n      </ul>'%(d,d,'\n        '.join(rows)))

open('.map/map.svg.html','w').write(svg)
open('.map/map.lists.html','w').write('\n'.join(lists))
print('viewBox %d x %d'%(W,H))
print('svg bytes',len(svg),' lists bytes',sum(map(len,lists)))
print('route paths',len(rt),'pins',len(CAMPS)+len(NATURE)+len(FOOD)+sum(len(v) for v in DAYS.values()))
# scrub ranges
for d,s in DAYS.items(): print('day',d,mins(s[0][0]),mins(s[-1][0]))
