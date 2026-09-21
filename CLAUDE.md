# CLAUDE.md

Guidance for working in this repo. Keep it accurate — update it when the architecture changes.

## What this is

A single-page, **offline-first PWA bookshelf of trip guide books** for iPhone. The whole app (HTML,
CSS, JS, an inline-SVG map) lives in one self-contained `index.html`. Photos are real files in
`images/`; the service worker makes it fully offline once loaded.

Two books, both 2026: **Okinawa** (Oct 10–12, camping road trip, bilingual JA/EN) and **Seattle**
(Jul 2–19, hiking, English). The reader lands on the shelf, taps a book, and the cover zooms and turns
open; a back button in the hero returns to the shelf. Where they were is remembered across launches.

Live site: https://huangwaylon.github.io/seattle/ (the repo is still named `seattle` from the first
trip — the URL and remote are unchanged on purpose).

## Files

| File | Role |
|------|------|
| `index.html` | The entire app. **Source of truth — edit directly.** |
| `images/okinawa-hero.jpg`, `images/mount-rainier.jpg` | The two book covers, which are also the heroes. |
| `images/camps/*`, `images/tidepool/*`, `images/dive/*`, `images/cafe/*` | Okinawa card photos, 720 px wide (`dive/boat.jpg` is 442). |
| `images/*.webp` | Seattle hike photos. |
| `sw.js` | Cache-first service worker; precaches the shell and every image. A new worker waits until the refresh banner is tapped (or the app is fully closed). |
| `manifest.webmanifest`, `icon-180.png`, `icon-512.png` | PWA manifest and icons. |
| `.map/build.py` | Generator for the Okinawa map SVG. **Not shipped** — see "The map". |
| `.i18n/` | Translation source of truth. **Not shipped** — see "The Japanese layer". |

No build step, no framework, no dependencies, no CDN assets, system fonts only. The only outbound
links are Google Maps, Evertrail and trail maps, which open externally and fail gracefully offline.

## Architecture

- **One attribute is the navigation state.** `data-place` on `<html>` is `shelf`, `okinawa` or
  `seattle`, and CSS shows that one place. The bootstrap script in `<head>` sets it before first paint
  and swaps `nojs` for `js-tabs`, so there is no flash; it persists in `localStorage['place']` and is
  mirrored into `history` so Back works. Adding a book means one more selector in the
  `html[data-place=…]` rule, plus its slug in that bootstrap script's whitelist and one more
  `.book:nth-child()` pair for the shelf animation timings.
- **Opening a book** zooms `#turner` (a fixed overlay carrying the cover image) from the book's rect to
  full screen, then rotates its inner page off the spine. Reduced motion skips straight to the guide.
- **Themes are token sets.** `:root` holds structure plus a neutral palette for the shelf and the
  update banner; `.t-okinawa` and `.t-seattle` each declare their own colours (`--acc`, `--acc2`,
  `--ink`, `--bg`, …). Nothing in the shared CSS names a guide. `--shell` is the page backdrop per
  place, and JS copies it into the `theme-color` meta.
- **The shelf** is a 3D scene per book: a cloth `.book-spine` face hinged (`rotateY(90deg)`) to the
  photo `.book-cover`, in a recessed case on a plank, on warm paper a shade off both guide
  backgrounds so opening a book is not a jump. It is a touch UI, so there is **no hover state**: each
  book turns, floats and slides a gloss highlight on its own, with mismatched cycle lengths per book
  (`--sway` / `--float`) so they never fall into step. `.books` is always two columns — a third book
  means changing that one value. Each book is an `<a href="#g-…">`, so the no-JS path still navigates.
  The back button lives inside the hero and scrolls away with it.
- **Tabs are pure CSS.** Each guide has one radio group (`name="tab-<slug>"`) with each radio inside
  its `<label class="tabbtn">`, and `.guide:has(.t-<tab>:checked) .v-<tab>` shows the view. A new tab
  means one more selector there; the tab-bar highlight is already generic
  (`.tabbtn:has(.tabradio:checked)`). `:has()` carries the whole mechanism, so there is an
  `@supports not (selector(:has(*)))` escape hatch that falls back to the stacked layout.
- **Accordions** are native `<details>/<summary>`; **checklists** are `<input class="cb">` +
  `<label class="checkrow">`. Both are styled purely in CSS.
- **`.spine`** is the shared vertical timeline behind day, logistics and campsite cards. Each card
  carries a `.node` dot and, optionally, a `.lead-chip` left column — a date on a day, a drive time on
  a campsite.
- **No-JS fallback is required**, because plain file previews (macOS Quick Look) run without JS. All
  content is therefore static HTML, never generated at runtime. Without JS, every place and view shows
  stacked and scrollable, tab bars / back buttons / `.jsonly` controls are hidden, and the packing list
  shows its static seed rows read-only. (Quick Look renders `details[open] .content` mid-animation, so
  open cards can look blank in a thumbnail — a Quick Look artifact only.)
- **Per-guide JS.** One loop wires each `.guide`: language, expand-all, today, tab scroll, campsite
  filter, packing, map. A module whose markup that guide lacks returns early, which is how Seattle
  simply has no map, no filter and no language toggle.
- **Bilingual, Japanese-first (Okinawa only).** Japanese is the markup, so first paint and the no-JS
  path are Japanese. Every translatable element carries its English inner HTML in `data-en`; the
  Japanese is cached into `data-ja` on the first switch, and a bubbling `langchange` event lets other
  modules re-apply. `data-bilingual` on the guide is what declares a book translatable — both the
  language sweep and the packing model check it — and `data-lang` holds the current choice, persisted in
  `localStorage['lang']`. Strings JS sets at runtime live in the `T()` table — keep
  its Japanese identical to the markup. The packing list is excluded from the sweep: it renders from
  its own bilingual model.
- **Units.** Every distance and temperature is a
  `<span class="u" data-metric="11.5 km" data-imperial="7 mi">11.5 km</span>`. Both strings are
  literals, so JS never does live maths. The default text is metric, the choice persists in
  `localStorage['units']`, and the module is document-wide, so both books stay in sync. Always wrap a
  new measurement.
- **One toolbar rhythm on every tab:** heading → intro 6px, intro → control row 20px, row → row 12px,
  row → content 14px. Each book's itinerary toolbar holds a unit toggle; only Okinawa has a language
  toggle.
- **The packing list is the one exception to static markup.** The static `.group` rows are both the
  no-JS fallback and the one-time seed: JS builds a model from them, or restores the saved one, then
  re-renders. **Edit list** renames, adds, deletes and reorders categories and items; blank rows are
  pruned on exit. Saved per book as `localStorage['packingData:<slug>']` =
  `{v:2, cats:[{id,name,nameJa,icon,items:[{id,text,textJa,note,noteJa,done}]}]}`. A saved model wins
  over the seed, so editing the defaults only affects a fresh install. Ids come from `uid()` at
  runtime — never hard-code them. Okinawa also reads the pre-shelf `packingData` key, so phones that
  already have a list keep it.
- **`LS.get` / `LS.set`** wrap every `localStorage` access, because it throws in private and preview
  contexts and a failure should just mean "no saved state". Never call `localStorage` directly.
- **Responsive:** a centred `max-width:var(--maxw)` (720px) column, `clamp()` hero height, safe-area
  insets respected. Works phone portrait/landscape, tablet and desktop.

## The map (Okinawa)

`.v-map` is an inline SVG — no tiles, no library, no network. The island, the route, all 69 pins and
the three stop timelines are **static markup generated at authoring time** by `.map/build.py`; JS only
toggles state. With JS off, all three days and every pin show.

- **Projection:** equirectangular with a `cos(lat)` correction, window
  `lat 26.055–26.895 / lon 127.615–128.345`, `viewBox="0 0 778 1000"`. The frame is the same for every
  day on purpose, so the island never moves. Geometry is Douglas-Peucker simplified, rounded to 1 dp.
- **Data:** coastline = OSM `natural=coastline` via Overpass (the 24 rings with area ≥ 18 px²). Routes
  = one OSRM driving leg per pair of consecutive stops, so the lines follow real roads; the boat, bus
  and the walking legs are straight dashed lines instead (`KIND` names them; the ~870 m office→IC
  walk's car route loops 13 km onto the expressway and would draw a lie). OSRM's per-leg minutes are what the
  itinerary's drive times were checked against. **Keep the footer credit to OSRM and OpenStreetMap.**
- **Colour = day** (`--acc`, `--acc2`, `--sun`). The day and layer chips carry a matching `.sw`
  swatch, so **the chips are the legend** — there is deliberately no legend block. Candidate layers are
  told apart by **shape**: ■ campsite, ▲ nature, ◆ food.
- **State lives in attributes on the view:** `data-day="1|2|3|all"` and
  `data-camp`/`data-nature`/`data-food`. All show/hide is CSS scoped under `.js-tabs`, so their
  absence means "show everything".
- **There is no time slider.** Tapping a stop — a pin or a row — is the only clock. That stop is
  `.now`; everything earlier that day goes grey, so the day's colour is only what is still ahead. A day
  opens at its first stop, or during Oct 10–12 2026 at the stop you should be at by now.
- **Pins are not focusable** (69 tab stops would swamp the keyboard order): the SVG is one
  `role="img"` and the stop rows are the keyboard path. Each pin carries a wide invisible `circle.hit`
  so a small dot stays hittable.
- **Regenerating:** `python3 .map/build.py` needs `.map/coast.json` and `.map/legs.json` (gitignored —
  the header in `build.py` has the exact Overpass and OSRM calls, run from an in-page `fetch()`). It
  writes `.map/map.svg.html` and `.map/map.lists.html`; splice those over the `<svg class="map">` block
  and the three `<ul class="tl stoplist">` blocks, then bump `CACHE` in `sw.js`. Edit the place tables
  in `build.py`, never the generated coordinates.

## The Japanese layer

`.i18n/` is the translation source of truth: `GLOSSARY.md` (tone spec + fixed place names),
`strings.json` (English, keyed by `sha1(slot|en)[:10]`) and `ja-*.json` (the Japanese by the same id).
Note the direction — `.i18n` keys on **English**, but the **shipped markup is Japanese with English in
`data-en`**, so regenerating means flipping the file back to English-base first, re-running the
extract/inject scripts, then flipping again.

When you change English text: strip the layer first (`re.sub(r'( data-en="[^"]*")+', '', html)` —
**the attribute only, never unwrap a `<span>`**, since wrapper spans in `h2.section`, `a.outlink`,
`.glabel` and the edit button are load-bearing), re-extract, translate only the missing ids, then
re-inject onto the clean base. Injecting twice duplicates attributes. Because an id hashes the English,
changing one word orphans its translation — that is the point.

Two constraints: a `data-en`/`data-ja` value may contain `<small>`/`<strong>` and must reproduce any
nested `span.u` byte-for-byte; and **packing rows must not contain inline HTML**, because the packing
model escapes its strings.

**Known drift:** the map tab, the Day 2 snorkelling rewrite and the shelf added English strings that
have never been through the extractor. Nothing is broken at runtime — re-extract before the next
translation pass.

## Editing content

1. Edit `index.html` directly. Day cards are `<details class="card day">` (Okinawa) or `.card.hike` /
   `.card.travel` (Seattle) inside `.spine.days`, each with an hour-by-hour `<ul class="tl">`.
   Campsites are `<details class="card camp wild|paid f-beach f-toilet f-shower">` in one flat list
   ordered by road time from the Evertrail office in Okinawa City (26.3794, 127.8257) — **not** from
   Naha Airport. The `f-*` classes drive `.camp-filters`; keep them in sync with the chips.
2. **Voice: factual only.** No tone, no evaluation, no persuasion — clipped fact-lists ("Calm bay,
   sunsets over the city. No toilets."), Japanese in 体言止め. No "worth it", "the best" or
   reasons-why. There are **no `.note` callouts**: a fact that matters goes in a plain bullet, a
   `<small>` under the line it belongs to, or a stat tile.
3. **Do not hand-edit the map SVG** — change the tables in `.map/build.py` and regenerate. A new or
   moved stop needs its OSRM leg refetched too, or the line will not reach its pin.
4. Checklist rows are an `<input class="cb" id="ok-|se-packing-<group>-<index>">` followed by its
   `<label class="checkrow" for="…">`. The prefix only has to be unique per book — `seedFromDOM()`
   reads structure (`.group`, `.checkrow`, `.ctxt`, the `.gicon use` href), never ids.
5. **After any change to `index.html` or another cached asset, bump `CACHE` in `sw.js`** — otherwise
   installed phones keep serving the old copy.

### Google Maps links

Every link points at a real place, never a coordinate: campsites use the Evertrail directory's own
`Google maps` field (the operator's pin — do not "improve" it), named venues use
`https://www.google.com/maps/place//data=!4m2!3m1!1s<FID>`, and Cape Hedo uses a `?api=1&query=` place
query because Google returns a list for it.

To get a FID without an API key: `window.open('https://www.google.com/maps/search/<query>')` from an
allowlisted origin for several venues at once, wait ~6 s, then read chrome-devtools `list_pages` — each
tab's **resolved** URL carries `!1s0x…:0x…` (the FID) and `!3d/!4d` (Google's coordinates). Verify
those against an independent reference (Tabelog for shops, OSM/Nominatim for landmarks, the Evertrail
record otherwise). Known acceptable gaps: 比地大滝 130 m and 崎本部緑地 45 m (place pin vs OSM node),
ター滝 ~625 m (Google marks the falls, Evertrail the trailhead), 古宇利島 (island centroid). If a tab
stays on `/maps/search/` there is no single match — retry with the official name (ゴリラチョップ only
resolves as 崎本部緑地, Seragaki as ダイヤモンドビーチ), and failing that leave a query link rather
than inventing a pin. **`https://maps.google.com/?cid=<decimal>` no longer works** — it looks right
and fails silently.

### Where the data came from

Okinawa campsites are the 26 drivable main-island sites in the **Evertrail directory**
(https://directory.evertrailokinawa.com/ — a React SPA over Airtable base `apph4puq05ed8CGbz`, table
`Sites`, read-only PAT in its JS bundle; its `Hot spot` / `Dining` records sourced itinerary stops).
Nine ferry-only outer-island sites are deliberately excluded. Seattle hikes come from WTA and
AllTrails, with trail maps linked to `huangwaylon.github.io/gpx`. `WebFetch` and `curl` are
sandbox-blocked; in-page `fetch()` from chrome-devtools works.

## Testing locally

Service workers need a real origin: `python3 -m http.server 8765`, then
`http://localhost:8765/index.html`. To check offline, load once, confirm the worker is activated, stop
the server and reload. **An old worker from a previous version serves stale HTML** — unregister it and
clear caches first. Check the no-JS path in a browser by setting
`documentElement.className='nojs'` and removing `data-place`.

## Deploying

Remote `git@github.com:huangwaylon/seattle.git` (personal github.com, SSH). The local `gh` CLI is
logged into Apple's internal GitHub — do **not** use it here. Commit and push to `main` (end commits
with the `Co-Authored-By` trailer); Pages rebuilds in about a minute from `main` at folder `/`. All
asset paths are relative, so the project site works under `/seattle/`.

**On iPhone:** open the live URL in Safari on Wi-Fi, let it fully load, Share → Add to Home Screen,
then open once from the icon while online. After a `CACHE` bump, an installed app shows the refresh
banner on its next online launch; a full close-and-reopen activates the new worker on its own.
Installed PWAs are exempt from Safari's 7-day storage cap, so the packing list survives — install a
week or two before the trip.

## Trip facts worth remembering

- **Privacy:** the Pages site is public (true even for a private repo on the free tier) and names the
  travellers, flight/booking references and seat numbers. Flag this before adding more sensitive detail.
- **Okinawa shape.** The car is collected at the Evertrail office in **Okinawa City**, not the airport:
  bus 111 or 117 from Naha, ~1 h, ¥1,330 pp, off at Okinawa Kita IC, then a 10-min walk or a free
  pickup arranged by email. It goes **back to the same office**, so the bus is a round trip (¥5,320 for
  two, both ways; Evertrail's ¥10,000 shuttle only runs 10:30–16:00 and cannot cover the return). The
  travellers want nature — waterfalls, capes, beaches, reef — and explicitly **not** shopping,
  souvenirs, crowds, caves or historical sites, so American Village, the pottery village and the Blue
  Cave were removed. Don't reintroduce them.
- **Day 2 is snorkelling, not diving:** Dive Nuts' ボートシュノーケル morning boat (08:00 meet, 12:00
  back at the port), ¥9,900 each at 2+ people for one drop and ¥2,750 for the second — ¥25,300 for two
  doing both. The no-fly-after-diving constraint therefore no longer applies; the boat stays on Day 2
  by choice. Phone bookings are suspended — email or LINE only.
- **Day 3 ends at the Gushikawa tide pool, not the onsen.** The pool only exists around low tide, and
  Oct 12 2026's afternoon low at Naha is **14:53** (JMA), exactly when the drive lands there.
  Ryujin-no-yu came out because the car goes back to Okinawa City, 41 min *north* of it, before the
  office shuts at 18:00. Access was closed in 2020 with no published end date — check for a notice.
  Day 3 also has no snorkelling: 11:00 is バンタカフェ (Yomitan), not Maeda Point.
- **The Day 1 waterfall is フンガー滝**, 名護市真喜屋 (26.60810, 128.05392, FID
  `0x34e4570022eb29ff:0xfbbd1edacdb1b196`). It has been wrongly called 福川の滝 and 普久川の滝: OSM has
  a 普久川滝 node 400 m away with no Google place, and OSRM snaps both to the same road point, so the
  drive times "confirm" either name. **Don't rename it without a Google place id.** It is not a managed
  site — a local operator has publicly asked for the pin's removal, and there is no phone signal
  further in.
- **Drive-time buffers were audited leg by leg against OSRM**; every gap clears its drive by 18 min or
  more. Quote **per-leg** figures, which is what the map draws (office → King Tacos is 26 min; Kin →
  Manzamo is 19 per-leg but 21 chained). Campsite times are free-flow — add 20–40 min in holiday
  traffic, and Koki's coordinate snaps to the expressway so its figure is unreliable.
- **Jellyfish first aid is species-dependent.** Vinegar is right for habu-kurage and makes a Portuguese
  man o' war sting **worse**. Never simplify that bullet into generic "use vinegar" advice.
- **Verified in Sep 2026:** Solaseed flight times, Naha sunrise/sunset, Oct 12 2026 = Sports Day, the
  ¥1,040 ETC vs ¥1,610 cash toll, Churaumi's ¥2,180, JMA normals, habu campaign dates, that a gas
  canister cannot be flown, every Dive Nuts price. **Still unverified:** King Tacos' hours,
  Ryujin-no-yu's rate, Kishimoto's 1905 founding and cash-only policy, every campsite fee (the
  directory prices only two), and whether the tide pool is accessible at all. Two claims were wrong and
  are corrected: King Tacos is not the 1984 original (taco rice began at Parlour Senri in Kin), and
  Daisekirinzan was renamed **ASMUI** in Dec 2024 and charges ¥2,500.
- **Don't** add a runtime build/render step or external CDN assets.
