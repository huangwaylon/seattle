# TRIPS.md

Per-trip facts that are not derivable from the markup: what was verified, what was wrong before, and
what is still open. `CLAUDE.md` covers the app itself.

## Place links

Every link points at a real place, never a coordinate: campsites use the Evertrail directory's own
`Google maps` field, named venues use `https://www.google.com/maps/place//data=!4m2!3m1!1s<FID>`, and
Cape Hedo uses a `?api=1&query=` place query because Google returns a list for it.

Short `maps.app.goo.gl` links resolve with `curl -o /dev/null -w '%{redirect_url}'`; without one,
`window.open('https://www.google.com/maps/search/<query>')` from an allowlisted origin and then
chrome-devtools `list_pages` shows the same resolved URL. Either way it carries the name,
`!1s0x…:0x…` (the FID) and `!3d/!4d` (Google's coordinates) — verify those against an independent
reference (Tabelog, OSM/Nominatim, the operator's record). Gaps already accepted: 比地大滝 130 m and
崎本部緑地 45 m (place pin vs OSM node), ター滝 ~625 m (falls vs trailhead), 古宇利島 (island centroid).
A page still on `/maps/search/` has no single match: retry with the official name, then leave a query
link rather than invent a pin.
**`https://maps.google.com/?cid=…` no longer works** — it looks right and fails silently.

## Okinawa 2026 — Oct 10–12, bilingual JA/EN

- **Trip shape.** The car is collected at the Evertrail office in **Okinawa City**, not the airport:
  bus 111 or 117 from Naha, ~1 h, ¥1,330 pp, off at Okinawa Kita IC, then a 10-min walk or a free
  pickup arranged by email. It goes **back to the same office**, so the bus is a round trip (¥5,320
  for two, both ways; Evertrail's ¥10,000 shuttle only runs 10:30–16:00 and cannot cover the return).
  The travellers want nature — waterfalls, capes, beaches, reef — and explicitly **not** shopping,
  souvenirs, crowds, caves or historical sites, so American Village, the pottery village and the Blue
  Cave were removed. Don't reintroduce them.
- **Day 2 is snorkelling, not diving:** Dive Nuts' ボートシュノーケル morning boat (08:00 meet, 12:00
  back at the port), ¥9,900 each at 2+ people for one drop and ¥2,750 for the second — ¥25,300 for
  two doing both. The no-fly-after-diving constraint therefore no longer applies; the boat stays on
  Day 2 by choice. Phone bookings are suspended — email or LINE only.
- **Day 3 ends at the Gushikawa tide pool, not the onsen.** The pool only exists around low tide, and
  Oct 12 2026's afternoon low at Naha is **14:53** (JMA), exactly when the drive lands there.
  Ryujin-no-yu came out because the car goes back to Okinawa City, 41 min *north* of it, before the
  office shuts at 18:00. Access was closed in 2020 with no published end date — check for a notice.
  Day 3 also has no snorkelling: 11:00 is バンタカフェ (Yomitan), not Maeda Point.
- **The Day 1 waterfall is フンガー滝**, 名護市真喜屋 (26.60810, 128.05392, FID
  `0x34e4570022eb29ff:0xfbbd1edacdb1b196`). It has been wrongly called 福川の滝 and 普久川の滝: OSM
  has a 普久川滝 node 400 m away with no Google place, and OSRM snaps both to the same road point, so
  the drive times "confirm" either name. **Don't rename it without a Google place id.** It is not a
  managed site — a local operator has publicly asked for the pin's removal, and there is no phone
  signal further in.
- **Drive-time buffers were audited leg by leg against OSRM**; every gap clears its drive by 18 min
  or more. Quote **per-leg** figures, which is what the map draws (office → King Tacos is 26 min; Kin
  → Manzamo is 19 per-leg but 21 chained). Campsite times are free-flow — add 20–40 min in holiday
  traffic, and Koki's coordinate snaps to the expressway so its figure is unreliable.
- **Jellyfish first aid is species-dependent.** Vinegar is right for habu-kurage and makes a
  Portuguese man o' war sting **worse**. Never simplify that bullet into generic "use vinegar" advice.
- **Verified in Sep 2026:** Solaseed flight times, Naha sunrise/sunset, Oct 12 2026 = Sports Day, the
  ¥1,040 ETC vs ¥1,610 cash toll, Churaumi's ¥2,180, JMA normals, habu campaign dates, that a gas
  canister cannot be flown, every Dive Nuts price. **Still unverified:** King Tacos' hours,
  Ryujin-no-yu's rate, Kishimoto's 1905 founding and cash-only policy, every campsite fee (the
  directory prices only two), and whether the tide pool is accessible at all. Two claims were wrong
  and are corrected: King Tacos is not the 1984 original (taco rice began at Parlour Senri in Kin),
  and Daisekirinzan was renamed **ASMUI** in Dec 2024 and charges ¥2,500.
- **Where the campsites came from.** The 26 drivable main-island sites in the **Evertrail directory**
  (https://directory.evertrailokinawa.com/ — a React SPA over Airtable base `apph4puq05ed8CGbz`,
  table `Sites`, read-only PAT in its JS bundle; its `Hot spot` / `Dining` records sourced itinerary
  stops). Nine ferry-only outer-island sites are deliberately excluded.

## Seattle 2026 — Jul 2–19, English

- Restored from commit `70b95b6`, the last state before the repo was rebuilt around Okinawa. Kept so
  the trip is not lost, not because it is being planned — it is in the past.
- Hike data came from WTA and AllTrails; the trail maps link out to `huangwaylon.github.io/gpx`.
- Only the itinerary and the packing list exist: no map, no campsite list, no Japanese.

## New Zealand 2027 — Feb 11–16, English

- **Flights** are booked and ticketed: NZ 98 Narita 18:30 Feb 10 → Auckland 09:00 Feb 11, NZ 95
  Auckland 00:10 Feb 17 → Narita 07:05. Air NZ confirmation 5HXFYH, Expedia itinerary
  73531978112284. Economy, one checked bag each, no seats chosen, cancellation not included.
- **The base is the host mother's home in New Lynn, west Auckland.** The exact street address is
  deliberately **not** in `index.html` — the Pages site is public and it is someone else's home. The
  map pin and every "New Lynn" reference use the suburb centre (−36.90939, 174.68405).
- **Days 1–4 are Auckland, days 5–6 are the drive south.** That split is why the map zooms: at island
  scale the Auckland week is a 25 px blob, so picking a day fits the view to it.
- **Taranaki and Taupō do not both fit into Feb 15–16.** The itinerary takes Taranaki (Waitomo caves,
  then sunrise at the Pouākai Tarns, which is the hero photo); the Taupō loop — Tīrau, Orakei Korako,
  Huka Falls — is listed in the "Not Scheduled Yet" card with its real drive times, as the
  alternative. Don't try to merge them.
- **Sunrise at the tarns drives Day 6.** New Plymouth sunrise on Feb 16 2027 is **06:52** NZDT
  (computed, NOAA algorithm), so the climb starts at 04:45 in the dark and the descent is in
  daylight. The other way round — sunset the evening before — means coming down by headlamp after a
  5 h drive.
- **Drive times are OSRM free-flow**, fetched per leg: AKL → New Lynn 20 km / 22 min, New Lynn →
  Waitomo 197 km / 2 h 36, Waitomo → New Plymouth 181 km / 2 h 30, New Plymouth → AKL 349 km /
  4 h 41. Auckland at peak adds 20–40 min.
- **Verified:** the flight times and references (from the booking email), the sunrise and sunset times
  for Auckland and New Plymouth, every place's coordinates and Google place id (resolved from the
  short links the traveller sent), and every drive time above.
- **Still unverified:** the Waitomo tour times and price, the Waiheke ferry timetable, how to get
  around Waiheke without a car, the Mangorei Track's length and climb (DOC's figures — and whether
  the track is open), Parnell Farmers' Market hours, and the opening hours of every shop and cafe on
  days 1–4. The One Tree Hill (182 m) and Mount Victoria (87 m) heights are the commonly published
  ones, not checked against LINZ.
- **Still to book:** the rental car, the cave tour, a bed in New Plymouth for Feb 15, the ferry, and
  seats on both flights.
- **Border facts worth keeping:** both passports need an **NZeTA** plus the visitor levy before
  boarding. Biosecurity is strict — no food, seeds, honey or plants, and hiking boots must be
  declared and scrubbed clean. An American licence is valid to drive for 12 months, so no
  international permit. Plugs are Type I at 230 V, which Japanese plugs do not fit.
- **Pouākai Tarns has no Google place.** The coordinate (−39.24930, 174.05300) is the centroid of the
  OSM `natural=water` cluster on the Pouākai plateau; the Google link on the day is the Mangorei
  Track trailhead instead.
