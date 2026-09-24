# TRIPS.md

Per-trip facts that are not derivable from the markup: what is verified, what is still open, and the
few decisions that would otherwise get undone by accident. `CLAUDE.md` covers the app itself.

## Place links

Every link points at a real place, never a coordinate: campsites use the Evertrail directory's own
`Google maps` field, named venues use `https://www.google.com/maps/place//data=!4m2!3m1!1s<FID>`, and
a place Google cannot resolve to one match uses `?api=1&query=<name>` instead.

Short `maps.app.goo.gl` links resolve with `curl -o /dev/null -w '%{redirect_url}'`; without one,
`window.open('https://www.google.com/maps/search/<query>')` from an allowlisted origin and then
chrome-devtools `list_pages` shows the same resolved URL. Either way it carries the name,
`!1s0x…:0x…` (the FID) and `!3d/!4d` (Google's coordinates) — verify those against an independent
reference (Tabelog, OSM/Nominatim, the operator's record). Gaps already accepted: 比地大滝 130 m and
崎本部緑地 45 m (place pin vs OSM node), ター滝 ~625 m (falls vs trailhead), 古宇利島 (island centroid).
**Never invent an FID.** A query link is the correct answer when there is no single match.
**`https://maps.google.com/?cid=…` no longer works** — it looks right and fails silently.

## Okinawa 2026 — Oct 10–12, bilingual JA/EN

**Trip shape.** The car is collected at the Evertrail office in **Okinawa City**, not the airport:
bus 111 or 117 from Naha, ~1 h, ¥1,330 pp, off at Okinawa Kita IC, then a 10-min walk or a free
pickup arranged by email. It goes **back to the same office**, so the bus is a round trip (¥5,320 for
two, both ways; Evertrail's ¥10,000 shuttle only runs 10:30–16:00 and cannot cover the return).

The travellers want nature — waterfalls, capes, beaches, reef — and explicitly **not** shopping,
souvenirs, crowds, caves or historical sites, so American Village, the pottery village and the Blue
Cave were removed. Don't reintroduce them.

**The three days, and why they are shaped that way.**

- **Night 1 is Yagaji Beach Campsite** in the north; **night 2 is あざまサンサンビーチ (Azama Sun Sun
  Beach) in Nanjo**, in the deep south — FID `0x34e571f35ecd6173:0x79be19cfdb7ae1e4`,
  (26.17810, 127.82925), which OSM independently puts within 7 m. Paid, toilets, showers, six BBQ
  pavilions, mown lawn, sunrise over Kudaka Island, 47 min from the office. Both campsites carry a
  「1泊目」/「2泊目」 chip in the campsite list, so it is obvious which two of the 26 are the plan.
- **Day 2 is snorkelling and then the drive south.** Dive Nuts' ボートシュノーケル morning boat
  (08:00 meet, 12:00 back at the port), ¥9,900 each at 2+ people for one drop and ¥2,750 for the
  second — ¥25,300 for two doing both. Phone bookings are suspended: email or LINE only. The
  no-fly-after-diving constraint does not apply to snorkelling. **Snorkelling stays on Day 2** —
  it is the one fixed point in the week.
- **Ufuya (百年古家 大家) and Okinawa Milk Farm Cafe are both required, so they are split across two
  days** — a soba lunch and a kakigori 80 minutes apart was too much food in one afternoon. The cafe
  moved to **Day 1**, where it costs only 3 extra minutes of driving: Manzamo → cafe → Hunga Falls is
  36 + 20 min against 53 min direct, because the cafe sits almost exactly on that line. Ufuya stays on
  Day 2 as the meal after the boat.
- **Day 3 runs west along the south coast**, because night 2 is in the south: Chinen Misaki Park
  (4 min from the campsite) → 浜辺の茶屋 at Mibaru → Odohama Beach → Cape Kyan → the Gushikawa tide
  pool, which is 3 min from Cape Kyan. The old west-coast trio (Cape Zanpa, Senaha Beach, Banta Cafe)
  came off Day 3 — from Azama they are a two-hour detour *away* from the tide pool, and the tide is
  what fixes the day. Banta Cafe keeps its card under 周辺 as a candidate.
- **Day 3 ends at the Gushikawa tide pool, not the onsen.** The pool only exists around low tide, and
  Oct 12 2026's afternoon low at Naha is **14:53** (JMA), which is what the 13:50 arrival is built on.
  Ryujin-no-yu came out because the car goes back to Okinawa City, 41 min *north* of it, before the
  office shuts at 18:00. Access to the pool was closed in 2020 with no published end date — check for
  a notice. Day 3 has no snorkelling.
- **The Day 1 waterfall is フンガー滝**, 名護市真喜屋 (26.60810, 128.05392, FID
  `0x34e4570022eb29ff:0xfbbd1edacdb1b196`). It has been wrongly called 福川の滝 and 普久川の滝: OSM
  has a 普久川滝 node 400 m away with no Google place, and OSRM snaps both to the same road point, so
  the drive times "confirm" either name. **Don't rename it without a Google place id.** It is not a
  managed site — a local operator has publicly asked for the pin's removal, and there is no phone
  signal further in.

**Drive times** are OSRM free-flow, fetched per leg, and every gap in the itinerary clears its drive
by **26 min or more** (the tightest is Odohama → Cape Kyan). Quote **per-leg** figures, which is what
the map draws. The long one is Nago → Azama, 80.5 km / 89 min down the length of the island on the
Sunday of a three-day weekend — the row says to add 20–40 min. Campsite-list times are free-flow too;
Koki's coordinate snaps to the expressway, so its figure is unreliable.

**Jellyfish first aid is species-dependent.** Vinegar is right for habu-kurage and makes a
Portuguese man o' war sting **worse**. Never simplify that bullet into generic "use vinegar" advice.

**Verified:** Solaseed flight times; the Azama campsite's place id and coordinate; Ufuya's hours
(11:00–15:30, L.O. 15:00, from ufuya.com — it also does dinner 17:30–21:00); Oct 12 2026 = Sports Day;
the ¥1,040 ETC vs ¥1,610 cash toll; Churaumi's ¥2,180; JMA normals; habu campaign dates; that a gas
canister cannot be flown; every Dive Nuts price; every drive time above; and the OSM coordinates of
all four new Day 3 stops (Chinen Misaki, 浜辺の茶屋, Odohama, Cape Kyan — Gushikawa's own coordinate
was confirmed independently to within 4 m).

**Still unverified:** 浜辺の茶屋's opening hours and closed days (its domain is unreachable from here;
the card says so, and the itinerary row says to check before going), the Azama campsite's October fee
and whether it takes bookings, King Tacos' hours, Kishimoto's 1905 founding and cash-only policy, and
every other campsite fee (the directory prices only two).

**Two claims were wrong and are corrected:** King Tacos is not the 1984 original (taco rice began at
Parlour Senri in Kin), and Daisekirinzan was renamed **ASMUI** in Dec 2024 and charges ¥2,500.

**Where the campsites came from.** The 26 drivable main-island sites in the **Evertrail directory**
(https://directory.evertrailokinawa.com/ — a React SPA over Airtable base `apph4puq05ed8CGbz`, table
`Sites`, read-only PAT in its JS bundle; its `Hot spot` / `Dining` records sourced itinerary stops).
Nine ferry-only outer-island sites are deliberately excluded.

## Seattle 2026 — Jul 2–19, English

- Restored from commit `70b95b6`, the last state before the repo was rebuilt around Okinawa. Kept so
  the trip is not lost, not because it is being planned — it is in the past.
- Hike data came from WTA and AllTrails; the trail maps link out to `huangwaylon.github.io/gpx`.
- Only the itinerary and the packing list exist: no map, no campsite list. Its content is
  English-only by design; only its chrome (tab labels, back button) follows the language setting.

## New Zealand 2027 — Feb 11–16, bilingual JA/EN

- **Flights** are booked and ticketed: NZ 98 Narita 18:30 Feb 10 → Auckland 09:00 Feb 11, NZ 95
  Auckland 00:10 Feb 17 → Narita 07:05. Air NZ confirmation 5HXFYH, Expedia itinerary
  73531978112284. Economy, one checked bag each, no seats chosen, cancellation not included.
- **The base is the host mother's home in New Lynn, west Auckland.** The exact street address is
  deliberately **not** in `index.html` — the Pages site is public and it is someone else's home. The
  map pin and every "New Lynn" reference use the suburb centre (−36.90939, 174.68405).
- **Taranaki is days 3–4 (Feb 13–14), in the middle, on purpose.** It was days 5–6, and that put a
  03:10 climb and a 362 km drive on the day of the flight, with no slack for weather on the
  mountain or a slow road. Days 1–2 and 5–6 are Auckland. Day 3 still starts at Parnell Farmers'
  Market, because it is **Saturday-only** and Feb 13 is the trip's one Saturday; the Wintergardens
  moved to day 6 with the North Shore. The split is why the map zooms: at island scale an Auckland
  day is a 25 px blob, so picking a day fits the view to it.
- **Taranaki and Taupō do not both fit into Feb 13–14.** The itinerary takes Taranaki (Waitomo caves,
  then sunrise at the Pouākai Tarns, which is the hero photo); the Taupō loop — Tīrau, Orakei Korako,
  Huka Falls — is listed in the "Not Scheduled Yet" card with its real drive times, as the
  alternative. Don't try to merge them.
- **Sunrise at the tarns drives Day 4, and the climb is 2 h 45, not 2 h.** DOC gives the Mangorei
  Track 2 h 30 to Pouākai Hut and the tarns sit past it, so the day is built backwards from a
  **06:49** New Plymouth sunrise (Feb 14 2027, NOAA; sunset the evening before 20:28): leave 03:10,
  trailhead 03:30, climbing from 03:45, tarns 06:30. An 04:45 start reached them *after* the sun. The descent is allowed 2 h. Doing
  it the other way round — sunset the evening before — means coming down by headlamp after a 5 h drive.
- **Drive times are OSRM free-flow**, fetched per leg: AKL ↔ New Lynn 20 km / 22 min, Parnell →
  Waitomo 193 km / 2 h 31, Waitomo → New Plymouth 181 km / 2 h 30, New Plymouth → New Lynn 362 km /
  4 h 49, New Lynn → Wintergardens 14 km / 20 min. Auckland at peak adds 20–40 min; the Feb 14
  return lands on a Sunday evening instead.
- **Orakei Korako keeps the operator's own unmacronised spelling**, unlike every other Māori name in
  the book — it is the trading name. Don't "fix" it.
- **Pouākai Tarns has no Google place.** The coordinate (−39.24930, 174.05300) is the centroid of the
  OSM `natural=water` cluster on the Pouākai plateau; the link on the day is the Mangorei Track
  trailhead instead.
- **The day cards' Open in Maps links are place *searches*, not pins.** The place ids were resolved
  once from the short links the traveller sent, but they are not in this repo, and a search beats an
  invented pin.
- **Verified:** the flight times and references (from the booking email), the sunrise and sunset times
  for Auckland and New Plymouth, every place's coordinates, and every drive time above.
- **Still unverified:** the Waitomo tour times and price, the Waiheke ferry timetable, how to get
  around Waiheke without a car, the Mangorei Track's length and climb (DOC's figures — and whether
  the track is open), Parnell Farmers' Market hours, and the opening hours of every shop and cafe on
  the Auckland days — and now that Waiheke is a Monday and the Wintergardens a Tuesday, whether
  Allpress, Batch and Amano open on a Monday. The One Tree Hill (182 m) and Mount Victoria (87 m) heights are the commonly published
  ones, not checked against LINZ.
- **Still to book:** the rental car, the cave tour, a bed in New Plymouth for Feb 13, the ferry, and
  seats on both flights.
- **Border facts worth keeping:** both passports need an **NZeTA** plus the visitor levy before
  boarding. Biosecurity is strict — no food, seeds, honey or plants, and hiking boots must be
  declared and scrubbed clean. An American licence is valid to drive for 12 months, so no
  international permit. Plugs are Type I at 230 V, which Japanese plugs do not fit.
