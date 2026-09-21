# CLAUDE.md

Guidance for working in this repo. Keep it accurate — update it when the architecture changes.

## What this is

A single-page, **offline-first travel itinerary** for an October 2026 Okinawa camping road trip,
built as an installable **PWA** for iPhone. The whole app (HTML, CSS, JS) lives in one
self-contained `index.html` — including an inline-SVG map of the island, so there are no map tiles
and no network dependency. The hero photo is a real file in `images/`. The service worker makes it
work fully offline once loaded.

The trip: Oct 10–12 2026, Haneda ⇄ Naha on Solaseed Air, main island only, self-driving a rented
Suzuki Jimny Sierra with a rooftop tent, camping two nights.

Live site: https://huangwaylon.github.io/seattle/ (the repo is still named `seattle` from the
previous trip — the URL and remote are unchanged on purpose).

## Files

| File | Role |
|------|------|
| `index.html` | The entire app. Static HTML content + inline `<style>` + inline `<script>`. **Source of truth — edit directly.** |
| `images/okinawa-hero.jpg` | The hero photo (the Jimny + rooftop tent on a coastal bluff). Precached by the service worker. |
| `images/camps/*.jpg` | One photo per campsite, 720 px wide, scraped from the Evertrail directory's Airtable `Photos` field. All precached. |
| `images/tidepool/*.jpg` | Two photos of the Gushikawa tide pool, 720 px wide, from the note.com article (credited in the card). Precached. |
| `sw.js` | Service worker. Cache-first; precaches the app shell **and the hero image**. Update is **message-driven**: a freshly-installed worker waits (no auto-skipWaiting) until the page tells it to `SKIP_WAITING` via the refresh banner — or until the app is fully closed, when it activates on its own. |
| `manifest.webmanifest` | PWA manifest (name, icons, `standalone` display, theme colors). |
| `icon-180.png` | iOS `apple-touch-icon` (Home Screen). |
| `icon-512.png` | Manifest/PWA install icon (also `maskable`). |
| `.map/build.py` | Generator for the map tab's SVG geometry. **Not shipped** — see "The map tab". |
| `README.md` | User-facing description + install steps. |

There is no build step or framework. No dependencies. No bundler.

## Core architecture & conventions

- **Self-contained:** no external CSS/JS/fonts/CDN assets. The only outbound links are per-campsite
  Google Maps and Evertrail listing links, plus the Evertrail onboarding link (all open externally
  and fail gracefully offline). System font stack only.
- **Four tabs:** Itinerary, Map, Campsites, Packing. Nature, kakigori and cafe recommendations sit in
  `details.card.travel` cards under a "Nearby" heading at the bottom of the Itinerary tab — there is
  deliberately no separate Eat tab.
- **Voice: factual only.** No tone, no evaluation, no explanation, no persuasion. Entries are clipped
  fact-lists ("Calm bay, sunsets over the city. No toilets."), and Japanese matches with 体言止め throughout.
  Do not add words like "worth it", "the best", "don't miss", or reasons-why. **There are no `.note`
  callouts anywhere** — the class and its icon were removed. If a fact matters, it goes in a plain bullet
  or a stat tile.
- **`.lead-chip` appears only on the three day cards** (the date). Every other card — logistics, Nearby,
  campsites — has no leading number. A campsite's drive time lives in a `From office` stat tile instead.
- **Bilingual, Japanese-first.** **Japanese is the markup**, so first paint and the no-JS path are
  Japanese with no flash. Every translatable element carries a `data-en` attribute holding its **English
  inner HTML**; the language module caches the Japanese into `data-ja` the first time you switch away,
  swaps `innerHTML`, and fires a `langchange` event that the units and packing modules listen for.
  `#packing` is excluded from the sweep because it renders from its own bilingual model.
  **There is exactly one language toggle, in the Itinerary toolbar** — it is global, so repeating it on
  every tab was noise. The module still binds `querySelectorAll('.lang-toggle')`, so adding a second one
  back would just work.
  **The flag is `lang-en` on `<html>`, and its absence means Japanese** — so `T()` and the packing model
  test `!contains('lang-en')`. Choice persists in `localStorage['lang']`; only `'en'` does any work on load.
  Strings JS sets at runtime (button labels, placeholders, `confirm()` text) live in the `T()` table at the
  top of the script block — keep its Japanese wording identical to the markup, or a label will change
  the first time the user toggles.
- **Units (metric / imperial):** every distance *and temperature* is wrapped in
  `<span class="u" data-metric="11.5 km" data-imperial="7 mi">11.5 km</span>`. The default text is
  metric (so the no-JS path shows metric). Every `.unit-toggle` on the page swaps all `span.u` to
  the chosen string and they stay in sync; the choice persists in `localStorage['units']`
  (`'metric'` | `'imperial'`). Both strings are literals — JS never does live math, avoiding
  rounding drift. **Like the language switch, there is exactly one toggle, in the Itinerary
  toolbar** — both settings are global and persisted, so repeating them per tab was noise. The
  modules still bind `querySelectorAll`, so a second toggle anywhere would just work.
  When adding a measurement, always wrap it in a `span.u` with both attributes.
- **No-JS fallback is required.** Plain file previews (e.g. macOS Quick Look) run the page
  *without* JavaScript. So:
  - All content is **static HTML** — never generated by JS at runtime.
  - `<html class="nojs">`; JS removes `nojs` and adds `js-tabs` on load.
  - Without JS: every `.view` is `display:block` (all sections stacked, scrollable), the tab bar
    is hidden, and the packing list shows its static seed rows (read-only). Fully usable.
  - With JS (`.js-tabs`): only the selected `.view` shows (CSS `:checked ~` on hidden radios),
    the tab bar appears, the packing list becomes editable, the campsite filter works, and the
    "today" highlight lights the matching itinerary date's spine node during the trip (Oct 2026).
  - Quick Look renders `details[open] .content` mid-animation, so open cards can look blank in a
    `qlmanage` thumbnail. That is a Quick Look artifact only — verify no-JS layout in a browser.
- **Tabs = pure CSS.** Four hidden `<input type="radio" name="tab">` (`#tab-itinerary`, `#tab-map`,
  `#tab-camps`, `#tab-packing`) at the top of `<body>` drive
  `#tab-*:checked ~ .views #view-*{display:block}`. The bottom bar uses `<label for=...>`.
  No JS needed for tab switching. Adding a tab means touching four rule blocks — the
  `:checked ~ .views` show rule, the two `.tabbar` colour/underline rules, and the
  `padding-top:var(--safe-t)` list.
- **Accordions = native `<details>/<summary>`.** No JS for expand/collapse. The chevron rotates
  via `details[open] > summary .chev`.
- **Checklists = native `<input type="checkbox" class="cb">` + `<label class="checkrow">`.**
  Checked styling is pure CSS (`.cb:checked + .checkrow ...`).
- **`.spine`** is the shared vertical-timeline wrapper (a `::before` rule) used by the itinerary
  days, the logistics cards, and the campsite list. Each card carries an absolutely-positioned
  `.node` dot; `.lead-chip` is the shared left column (a date on the itinerary, a drive time on
  campsites).
- **The packing list is data-driven & user-editable** (the one exception to "static markup").
  The static `.group` blocks inside `#packing` are BOTH the no-JS fallback AND the one-time seed:
  on load the packing script builds a model from that DOM, or restores the saved model, then
  re-renders `#packing` from the model. An **Edit list** toggle swaps each row into inline inputs
  with controls to create / rename / delete categories and create / edit / delete items, plus
  **up/down buttons to reorder the top-level categories** (reordering just permutes the `cats`
  array, so it's automatically compatible with older saved data); blank rows are pruned on exit.
  Everything (structure + order + checks) persists. The itinerary and campsites stay 100% static
  HTML — not user-editable.
- **`LS.get` / `LS.set`** wrap every `localStorage` access, because it throws in some private and
  preview contexts and a failure should just mean "no saved state". Don't call `localStorage`
  directly.
- **Persistence:** the whole packing model saves to `localStorage['packingData']` as
  `{v:2, cats:[{id, name, nameJa, icon, items:[{id, text, textJa, note, noteJa, done}]}]}`, written on
  every edit/check. Japanese is seeded from the static rows' `data-ja`; editing writes to whichever
  language is on screen and falls back to the other when one is blank. A saved model wins over the seed,
  so a device that already has one will **not** pick up edited defaults — clear the key to re-seed.
  Item/category ids are generated at runtime (`uid()`), so they're stable per device but differ
  across installs — never hard-code them. Only persists in a real browser context (Safari /
  installed PWA), not in ephemeral Quick Look.
- **`.jsonly` elements** (e.g. "Expand all", "Edit list" / "Reset checks", the unit toggles, the
  campsite filter, group counts) are hidden unless JS runs, via `.nojs .jsonly{display:none}`.
- **One vertical rhythm above the fold**, the same on all four tabs: heading → intro 6px, intro →
  first control row 20px, control row → control row 12px, control row → content 14px. `.toolbar`
  and `.filters` share one padding declaration, and `.spine` / `.mapcard` / `#packing` all carry the
  same 8px top offset so the last control row sits the same distance above a card, a map or a list.
- **Responsive:** content is a centered `max-width:var(--maxw)` (720px) column; the hero height
  is `clamp(...)`. Works phone portrait/landscape, tablet, desktop. Respects safe-area insets.
- **Theme:** light "Okinawa Reef" palette (warm sand paper, deep sea-ink text, ocean teal `--sea`
  + coral `--coral` accents), all via CSS custom properties in `:root`. Keep the variable set
  tight — don't reintroduce dead ones.

## The map tab

`#view-map` is an inline SVG — no tiles, no library, no network. Everything in it (the island, the
route, all 67 pins, the three stop timelines) is **static markup generated at authoring time** by
`.map/build.py`; the JS module only toggles state. That keeps the "all content is static HTML" rule
intact, and the no-JS path still shows a real map with all three days and every pin on it.

- **Projection** is plain equirectangular with a `cos(lat)` correction, window
  `lat 26.055–26.895 / lon 127.615–128.345`, giving `viewBox="0 0 778 1000"`. North is up and the
  frame is **the same for every day** on purpose — day 2 only fills the north of it, but the island
  never moves, so you always know where you are. Geometry is Douglas-Peucker simplified (coastline
  tol 1.8 / 1.1 user units, routes 1.2) and rounded to 1 dp.
- **Data.** Coastline = OSM `natural=coastline` via Overpass, stitched into closed rings, keeping the
  24 rings with area ≥ 18 px² inside the window. Routes = one **OSRM driving leg per pair of
  consecutive stops**, so the lines follow real roads; the two snorkel-boat legs and the airport bus legs
  are straight dashed lines instead. OSRM's per-leg minutes are also what the itinerary's drive times
  were checked against (all within a minute or two). Both sources need attribution — the footer credits
  OSRM and OpenStreetMap, keep it.
- **Colour = day.** `--sun` (a new token) is day 3, alongside `--sea` (day 1) and `--coral` (day 2).
  Each day's paths and pins carry `.d1`/`.d2`/`.d3`, which set `--c`; every fill and stroke reads
  `var(--c)`. The day and layer chips carry a matching `.sw` swatch, so **the chips are the legend** —
  there is deliberately no separate legend block. Candidate layers are told apart by **shape**, not
  colour: ■ campsite, ▲ nature, ◆ food.
- **State lives in attributes on `#view-map`:** `data-day="1|2|3|all"` and `data-camp` / `data-nature` /
  `data-food`. All the show/hide is CSS keyed off those, scoped under `.js-tabs` so the absence of the
  attributes (the no-JS case) means "show everything". The JS sets nothing else except the state
  classes `.past` / `.now` / `.future` / `.sel`.
- **The clock** (`#timeScrub`) is a range input over the selected day's first-to-last stop, in minutes.
  It **starts at the top of the day and resets there on every day switch**, so the opening view is always
  "here is the day ahead": the first stop gets `.now` (ring + label) and the whole route reads `.future`
  (faded to .34 — deliberately still legible, since this is the default state, not an edge case). Drag
  forward and stops behind you go `.past` (hollow) while driven legs come up to full. **Selecting a stop
  also moves the clock to it** — from the map pin or from the row, since they are the same thing; a
  candidate pin has no time and leaves the clock alone. During Oct 10–12 2026 the tab opens on today at
  the current time instead.
- **Pins are not focusable.** The SVG is one `role="img"` with a `<title>`, because 67 tab stops would
  swamp the keyboard order; the stop rows below the map are the keyboard path, and candidate names all
  exist in the Campsites and Nearby cards. Each pin does carry a wide invisible `circle.hit`, so the
  visible dot can stay small without being unhittable.
- **Regenerating.** `python3 .map/build.py` needs `.map/coast.json` and `.map/legs.json` (gitignored —
  the header in `build.py` has the exact Overpass and OSRM calls, run from an in-page `fetch()`). It
  writes `.map/map.svg.html` and `.map/map.lists.html`; splice those over the `<svg class="map">` block
  and the three `<ul class="tl stoplist">` blocks, then bump `CACHE` in `sw.js`. Edit the place tables
  in `build.py`, never the generated coordinates by hand.

## The Japanese layer

`.i18n/` is the translation source of truth. It is **not** shipped to the browser — `index.html` is still
self-contained — but keep it, or any future English edit means re-translating from scratch.

| File | Role |
|------|------|
| `.i18n/GLOSSARY.md` | Tone spec (ガイドブック調) + fixed place-name and term list. Read this before translating. |
| `.i18n/strings.json` | Every extracted English string as `{id, slot, en}`. `id` = sha1(`slot|en`)[:10]. |
| `.i18n/ja-*.json` | The Japanese, keyed by the same `id`. Several files, merged on inject. |

Note the direction: `.i18n` holds **English** as the keying language (`strings.json`) with Japanese in
`ja-*.json`, but the **shipped markup is Japanese with English in `data-en`**. The extract/inject scripts
were written against an English-base file, so regenerating means flipping the file back to English-base
first (swap each `data-en` value with its element's content), re-running them, then flipping again.

**Workflow when you change English text:**
1. Edit `index.html` **from a clean base** — strip the layer first with
   `re.sub(r'( data-en="[^"]*")+', '', html)`. **Strip the attribute only, never unwrap a `<span>`.**
   Wrapper spans inside `h2.section`, `a.maplink`, `.glabel` and the `#editPacking` button are load-bearing:
   the packing seed reads its category name by selector, and the JS sets button labels through
   `querySelector('span')`. An earlier regex that unwrapped `<span data-ja="…">x</span>` silently broke
   all four, and the symptom (category names rendering as "List", button labels frozen) shows up only at
   runtime.
2. Re-extract, diff against the merged `ja-*.json` by `id`, and translate only the missing ids.
3. Re-inject onto the clean base. Injecting onto an already-injected file yields duplicate attributes.

**Known drift:** the map tab and the Day 2 snorkelling rewrite added English strings that have never been
through the extractor, so `.i18n/strings.json` is behind `index.html` for those. The shipped markup carries
both languages (Japanese inline, English in `data-en`), so nothing is broken at runtime — but re-extract
before the next translation pass or those strings will look "new" twice.

Because an `id` is a hash of the English, changing one word orphans its translation — that is the point,
it surfaces exactly what needs re-translating. Note the extractor's bullet pattern also matches timeline
`<li>`s, so a few "unresolved" units on every run are expected noise.

Two constraints worth remembering:
- A `data-ja` value may contain `<small>`/`<strong>`, and must reproduce any nested
  `<span class="u" …>` **byte-for-byte**, since switching language re-parses it.
- **Packing rows must not contain inline HTML.** The packing model escapes its strings, so a `<strong>`
  in a packing item renders as literal text. Keep emphasis out of `.ctxt` and its `<small>`.

## Editing content

1. Edit `index.html` directly — itinerary days, logistics cards, campsites, and the packing list's
   seed rows are plain HTML.
   - **Day cards:** `<details class="card day">` inside `#days`, each with an hour-by-hour
     `<ul class="tl">`. The things that will actually bite us (closing days, the 17:30 airport car
     return, habu season) go in a plain `<small>` under the line they belong to — there are no callouts.
   - **Logistics cards:** `<details class="card travel">` (Flights, The Jimny, Know Before You Go)
     in the second `.spine` under the "Logistics" heading.
   - **Campsite cards:** `<details class="card camp wild|paid f-beach f-toilet f-shower">` in one flat
     list. The `f-*` classes and `wild`/`paid` drive the filter buttons in `#campFilters` — the filter
     shows one criterion at a time and reveals `#campEmpty` if nothing matches. Keep the class list in
     sync with the chips. The list is a **flat ordering by road time from the Evertrail
     office** (Ikehara, Okinawa City — 26.3794, 127.8257), which is where the car is collected. It is *not*
     measured from Naha Airport.
   - **Map:** do not hand-edit `#view-map`'s SVG — change the tables in `.map/build.py` and regenerate.
     A new or moved itinerary stop needs its OSRM leg refetched too, or the line will not reach its pin.
   - **Checklist items:** an `<input class="cb" id="<store>-<group>-<index>">` immediately followed
     by its `<label class="checkrow" for="...">`. These static rows are the packing list's **seed +
     no-JS fallback** — editing them changes the defaults a *fresh* install starts from. Once a
     device has saved its own `packingData`, that model wins and the static seed is ignored there.
     `seedFromDOM()` reads the *structure* (`.group`, `.checkrow`, `.ctxt`, the `.gicon use` href),
     not the ids, so a row needs no bookkeeping attributes — only the `id`/`for` pair the no-JS
     path uses.
2. Keep markup static — do not move content rendering into JS. (The packing list is the one
   deliberate exception: its static rows seed a JS-rendered, editable model — see above.)
3. **After ANY change to `index.html` (or other cached assets): bump the cache name in `sw.js`**
   (`okinawa-2026-v1` → `v2`). Otherwise installed phones keep serving the old cached copy.

### Google Maps links — how they were built

Every link points at a real place, never a coordinate. Three tiers, in descending precision:

1. **Campsites (26)** — the Evertrail directory's own `Google maps` field, i.e. the operator's pin.
   For unnamed wild sites this is the best available; do not "improve" it into a coordinate search.
2. **Named venues (19)** — an exact place link of the form
   `https://www.google.com/maps/place//data=!4m2!3m1!1s<FID>` where `<FID>` is Google's
   `0x…:0x…` feature id.
3. **Cape Hedo (1)** — a `?api=1&query=` place query, because Google returns a result list for it
   rather than one place. Flagged here so nobody assumes it was missed.

**How a FID is obtained** (no API key needed):
1. From a page on an allowlisted origin, `window.open('https://www.google.com/maps/search/<query>')`
   for each venue — several at once is fine.
2. Wait ~6 s, then call chrome-devtools `list_pages`. Each tab's entry shows its **resolved** URL,
   which for a single match becomes `/maps/place/<name>/@<lat>,<lon>,17z/data=…!1s0x…:0x…!8m2!3d<lat>!4d<lon>`.
   This is the trick that makes it cheap — the page list carries the resolved URL, so one call reads
   a whole batch. `evaluate_script` on each tab would work too but costs a call per venue.
3. Take `!1s0x…:0x…` as the FID and `!3d/!4d` as Google's coordinates for that place.
4. **Verify**: compare `!3d/!4d` against an independent reference — Tabelog's coordinates for shops,
   OSM/Nominatim for landmarks, the Evertrail record otherwise. All ten shops and cafes matched to
   within ~2 m. Accept a larger gap only with a reason: 比地大滝 130 m and 崎本部緑地 45 m are the
   place pin versus the OSM node; ター滝 is ~625 m from Evertrail's pin because Google marks the falls
   and Evertrail marks the trailhead; 古宇利島 is the island centroid, not the bridge.
5. If a tab stays on `/maps/search/`, there is no single matching place. Retry with the official name
   (ゴリラチョップ only resolved as 崎本部緑地, Seragaki only as ダイヤモンドビーチ). If it still does
   not resolve, leave a query link rather than inventing a pin.

**Dead end worth remembering:** `https://maps.google.com/?cid=<decimal>` no longer works. It looks
right and fails silently — a test link opened in Tokyo. Only the FID form or a place query is safe.

### Where the campsite data came from

The 26 campsites are the drivable main-island subset of the **Evertrail Okinawa directory**
(https://directory.evertrailokinawa.com/). That site is a React SPA backed by Airtable base
`apph4puq05ed8CGbz`, table `Sites` — the read-only PAT ships in its `assets/App-*.js` bundle, and
the table also holds `Hot spot` / `Dining` records used to source itinerary stops. Nine ferry-only
outer-island sites (Iheya, Izena, Tokashiki, Zamami) are deliberately excluded. Drive times are
real road times from Naha Airport via the public OSRM router, not straight-line estimates.

Note: `WebFetch` and direct `curl` are blocked by the local sandbox, but in-page `fetch()` from
the chrome-devtools MCP works — that is how this data was retrieved.

### Replacing the hero photo

```bash
sips --resampleHeightWidthMax 1600 NEW.jpg --out /tmp/hero.jpg
sips -s format jpeg -s formatOptions 48 /tmp/hero.jpg --out images/okinawa-hero.jpg
# Icons, cropped square from the same photo:
sips -c 1280 1280 --cropOffset 200 0 /tmp/hero.jpg --out /tmp/sq.jpg
sips -z 180 180 -s format png /tmp/sq.jpg --out icon-180.png
sips -z 512 512 -s format png /tmp/sq.jpg --out icon-512.png
```
`--cropOffset` is `<top> <left>`; keep `top + 1280 <=` the image height or you get a black band.
Then **bump `CACHE` in `sw.js`** so installed PWAs pick up the new bytes.

## Testing locally

Service workers need a real origin (not `file://`):
```bash
python3 -m http.server 8765      # then open http://localhost:8765/index.html
```
To check offline: load once, confirm the SW is `activated`, stop the server, reload — it should
still load from cache. If an old worker from a previous trip is still registered on
`localhost:8765`, unregister it and clear caches first or you'll be served stale HTML.
The no-JS path is best checked by forcing `documentElement.classList` to `nojs` in a browser
(`qlmanage -t -s 1400 -o . index.html` also works but see the animation caveat above).

## Deploying to GitHub Pages

Remote: `git@github.com:huangwaylon/seattle.git` (personal github.com; SSH).
The local `gh` CLI is logged into Apple's internal GitHub only — do **not** use it for this repo.

**Routine deploy (Pages already enabled):**
```bash
git add -A
git commit -m "..."     # end commits with the Co-Authored-By trailer
git push
```
GitHub Pages auto-rebuilds from `main` (~1 min). Check the **Actions** tab for the
"pages build and deployment" run.

**One-time Pages setup (already done, for reference):**
- Repo **Settings → Pages → Build and deployment**: Source = **Deploy from a branch**,
  Branch = **main**, Folder = **/ (root)** → Save.
- All asset paths are **relative**, so the project site works under the `/seattle/` subpath.
- HTTPS (required for the service worker) is automatic on `*.github.io`.

**Installing on iPhone (after a deploy):** open the live URL in **Safari on Wi-Fi**, let it fully
load (caches it), then **Share → Add to Home Screen**, and open once from the icon while online.
After bumping the SW cache, an installed app shows a **"New version available" refresh banner**
on its next **online** launch (or when it returns to the foreground and re-checks); tapping
**Refresh** activates the new worker and reloads. If the app is fully closed and reopened, the
new version activates on its own.

## Gotchas & notes

- **Privacy:** the Pages site is public (true even for a private repo on the free tier). It names
  the travellers, flight/booking references, and seat numbers. Flag this before adding more
  sensitive detail — and consider whether the ticket and booking numbers should stay.
- **iOS storage:** installed Home-Screen PWAs are exempt from Safari's 7-day script-storage cap,
  so the saved packing list persists — but only if opened occasionally. Install a week or two
  pre-trip.
- **Day 3 ends at the Gushikawa tide pool, not the onsen.** The pool (具志川城跡, Kyan, Itoman —
  26.08036, 127.66452, free) only exists around low tide, and **Oct 12 2026's afternoon low at Naha is
  14:53** (JMA tide table, station NS: lows 02:33 / 14:53, highs 08:50 / 20:31), which is exactly when the
  drive from Maeda Point lands you there. That forces it to be the day's last stop, which is why
  **Ryujin-no-yu came out** — it is only 23 min on from the pool and 10 min from the airport, so keeping
  both is possible but leaves about 30 min against the 17:30 car return instead of 45. The card documents
  that trade. Access was closed in 2020 with no published end date, so check for a current notice.
- **Trip shape.** The car is collected at the Evertrail office in **Okinawa City**, not the airport: bus 111 or
  117 from Naha Airport, ~1 h, ¥1,330 pp, off at Okinawa Kita IC, then a 10-min walk or a free pickup arranged
  by email. It is returned to the **airport**, where the cutoff is 17:30. Day 2 is the boat day. The
  travellers want nature — waterfalls, capes, beaches, reef — and explicitly not
  shopping, souvenirs, crowds, caves or historical sites, so American Village, the pottery village and the Blue
  Cave were all removed. Don't reintroduce them.
- **Verified, and what is not.** The content was fact-checked in Sep 2026. Confirmed against primary
  sources: the Solaseed flight times, Naha sunrise/sunset, Oct 12 2026 = Sports Day, the ¥1,040 ETC vs
  ¥1,610 cash toll and its ETC-only discount, Churaumi's ¥2,180, JMA weather normals, the habu campaign
  dates, that a gas canister cannot be flown, and every Dive Nuts price and time (read off
  divenuts.jp/taiken-snorkel in Sep 2026). **Still unverified** — King Tacos' hours, Ryujin-no-yu's rate
  and whether the holiday price applies on Sports Day, Kishimoto's 1905 founding and cash-only policy,
  and every campsite fee (the directory prices only two), and whether the Gushikawa tide pool is open at
  all. Note Dive Nuts has **suspended phone bookings** — those confirmations have to go by email or LINE.
- **Day 2 is snorkelling, not diving.** The booking is Dive Nuts' **ボートシュノーケル, morning boat**
  (`divenuts.jp/taiken-snorkel`, detail page `/about/20726/`): ¥9,900 each at 2+ people for one drop,
  ¥2,750 for the second, gear and photos included — ¥25,300 for two of us doing both. The morning boat
  runs 08:00 meet → 12:00 back at the port, which is what Day 2's timeline is built on. Two consequences
  worth remembering: the old ¥17,000-each fun-diving estimate is gone (it was never a published price),
  and **the no-fly-after-diving constraint no longer applies**, so the boat no longer *has* to be Day 2 —
  it stays there by choice, not necessity. The other four courses and their prices are listed in the card.
- **The Day 1 waterfall is 普久川の滝**, not 福川の滝. Both read "Fukugawa", but only 普久川の滝 (Ogimi,
  26.60537, 128.05676) exists, and OSRM backs it up: Manzamo → there is 53 min, there → Nago 19 min,
  matching the itinerary's 52 and 19.
- **Two claims were wrong and are now corrected** — King Tacos is *not* the 1984 original (taco rice was
  invented at Parlour Senri in Kin; King Tacos spread it), and Daisekirinzan was renamed **ASMUI** in
  Dec 2024 and charges ¥2,500. Campsite drive times are OSRM **free-flow** — add 20–40 min in holiday
  traffic, and note Koki's coordinate snaps to the expressway so its figure is unreliable.
- **Jellyfish first aid is species-dependent.** Vinegar is correct for habu-kurage and makes a Portuguese
  man o' war sting **worse**. Do not simplify that bullet into generic "use vinegar" advice.
- **Don't** add a runtime build/render step or external CDN assets.
