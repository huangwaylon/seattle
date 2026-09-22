# CLAUDE.md

Guidance for this repo — keep it accurate. Per-trip facts live in `TRIPS.md`.

## What this is

A single-page, **offline-first PWA bookshelf of trip guide books** for iPhone. The whole app (HTML,
CSS, JS, two inline-SVG maps) lives in one self-contained `index.html`. Photos are real files in
`images/`; the service worker makes it fully offline once loaded.

Three books: **Okinawa 2026** (Oct 10–12, camping road trip, bilingual JA/EN), **Seattle 2026**
(Jul 2–19, hiking, English) and **New Zealand 2027** (Feb 11–16, Auckland and Taranaki, English). The
reader lands on the shelf, taps a book, and the cover zooms and turns open; a back button in the hero
returns to the shelf. Where they were is remembered across launches.

Live: https://huangwaylon.github.io/seattle/ — the repo is still named `seattle` from the first trip,
and the URL and remote are unchanged on purpose.

## Files

| File | Role |
|------|------|
| `index.html` | The entire app. **Source of truth — edit directly.** |
| `images/okinawa-hero.jpg`, `mount-rainier.jpg`, `nz-hero.jpg` | The three book covers, which are also the heroes. |
| `images/camps/*`, `tidepool/*`, `dive/*`, `cafe/*` | Okinawa card photos, 720 px wide (`dive/boat.jpg` is 442). |
| `images/*.webp` | Seattle hike photos. |
| `sw.js` | Cache-first service worker, precaching the shell and every image. A new worker waits for the refresh banner (or a full app close). |
| `manifest.webmanifest`, `icon-180.png`, `icon-512.png` | PWA manifest and icons. |
| `.map/build.py`, `.map/nz.py` | Generators for the two maps. **Not shipped** — see "The maps". |
| `.i18n/` | Translation source of truth. **Not shipped** — see "The Japanese layer". |
| `TRIPS.md` | Per-trip facts, verification state, open bookings. |

No build step, framework, dependencies or CDN assets; system fonts only. The only outbound links are
Google Maps, Evertrail and trail maps, which open externally and fail gracefully offline.

## Architecture

- **One attribute is the navigation state.** `data-place` on `<html>` is `shelf` or a book's slug and
  CSS shows that one place. The bootstrap script in `<head>` sets it before first paint and swaps `nojs`
  for `js-tabs`, so there is no flash; it persists in `localStorage['place']` and is mirrored into
  `history` so Back works.
- **Opening a book** zooms `#turner` (a fixed overlay holding the cover) from the book's rect to full
  screen, then rotates its inner page off the spine. One transition at a time, and a counter every
  navigation bumps lets a stale animation know not to finish. Reduced motion skips it.
- **Themes are token sets.** `:root` holds structure plus a neutral palette for the shelf and update
  banner; `.t-okinawa`, `.t-seattle` and `.t-nz` each declare their own colours (`--acc`, `--acc2`,
  `--ink`, `--bg`, …). Nothing in the shared CSS names a guide, bar one deliberate exception: day
  colours on a map that draws several days at once. `--shell` is the page backdrop per place, and JS
  copies it into the `theme-color` meta.
- **The shelf** is one recessed case of rows, on warm paper a shade off every guide background so
  opening a book is not a jump. Each book is a 3D scene: a cloth `.book-spine` face hinged
  (`rotateY(90deg)`) to the photo `.book-cover`. It is a touch UI, so there is **no hover state** —
  each book turns, floats and slides a gloss on cycle lengths given per book (`--sway`, `--float` and
  their delays, inline), so no two fall into step. Each book is an `<a href="#g-…">`, so the no-JS path
  still navigates, and the back button sits inside the hero and scrolls away with it.
- **Adding a book** means: a `.book` in a `.shelf-row` (two columns per row), an
  `<article class="guide t-slug">`, a theme block, a `--shell`, one more selector in the
  `html[data-place=…]` rule, and the slug in the bootstrap script's whitelist.
- **Tabs are pure CSS.** Each guide has one radio group (`name="tab-<slug>"`) with each radio inside
  its `<label class="tabbtn">`, and `.guide:has(.t-<tab>:checked) .v-<tab>` shows the view. A new tab
  means one more selector there; the tab-bar highlight is already generic. `:has()` carries the whole
  mechanism, so there is an `@supports not (selector(:has(*)))` escape hatch to the stacked layout.
- **Accordions** are native `<details>`; **checklists** are `.cb` + `.checkrow`. No JS in either.
- **`.spine`** is the shared vertical timeline behind day, logistics and campsite cards; each card
  carries a `.node` dot and optionally a `.lead-chip` (a date on a day, a drive time on a campsite).
- **No-JS fallback is required**, because plain file previews (macOS Quick Look) run without JS, so
  all content is static HTML. Without JS every place and view shows stacked, tab bars / back buttons /
  `.jsonly` controls are hidden, and the packing list shows its seed rows read-only.
- **Per-guide JS.** One loop wires each `.guide`: language, expand-all, today, tab scroll, campsite
  filter, packing, map. A module whose markup that guide lacks returns early — which is how Seattle has
  no map and New Zealand no campsite filter.
- **Bilingual, Japanese-first (Okinawa only).** Japanese is the markup, so first paint and the no-JS
  path are Japanese; every translatable element holds its English inner HTML in `data-en`, the Japanese
  is cached into `data-ja` on the first switch, and a bubbling `langchange` lets other modules
  re-apply. `data-bilingual` declares a book translatable (the language sweep and the packing model
  both check it) and `data-lang` holds the choice, persisted in `localStorage['lang']`. Runtime strings
  live in the `T()` table — keep its Japanese identical to the markup. The packing list renders from
  its own bilingual model, so the sweep skips it.
- **Units.** Every distance and temperature is a
  `<span class="u" data-metric="11.5 km" data-imperial="7 mi">11.5 km</span>` — both literals, so JS
  never does live maths. Metric is the default text, the choice persists in `localStorage['units']`,
  and the module is document-wide, so every book stays in sync.
- **One toolbar rhythm on every tab:** heading → intro 6px, intro → control row 20px, row → row 12px,
  row → content 14px. Every book's itinerary toolbar holds a unit toggle; only Okinawa has a language one.
- **The packing list is the one exception to static markup.** Its `.group` rows are both the no-JS
  fallback and the one-time seed: JS builds a model from them, or restores the saved one, then
  re-renders. **Edit list** renames, adds, deletes and reorders; blanks are pruned on exit. Saved per
  book as `localStorage['packingData:<slug>']` =
  `{v:2, cats:[{id,name,nameJa,icon,items:[{id,text,textJa,note,noteJa,done}]}]}`, and a saved model
  wins over the seed, so editing the defaults only reaches a fresh install. Ids come from `uid()` at
  runtime — never hard-code them, and the DOM id carries the book because two guides seed a millisecond
  apart. Okinawa also reads the pre-shelf `packingData` key, so old phones keep their list.
- **`LS.get` / `LS.set`** wrap every `localStorage` access — it throws in private and preview contexts,
  and a failure should just mean "no saved state". Never call `localStorage` directly.

## The maps

Both maps are inline SVG — no tiles, no library, no network. Coastlines, routes, pins and the stop
timelines are **static markup generated at authoring time**; JS only sets state, so with JS off every
day and pin shows. Shared conventions, in the CSS and in the one `map(g)` module:

- **State lives in attributes on the view:** `data-day`, plus Okinawa's `data-camp`/`nature`/`food`.
  Show/hide is all CSS under `.js-tabs`, so their absence means "show everything". The day rules hide
  `.leg`, `.stop` and `.stoplist` then re-show the chosen day's — both halves weigh the same, so keep
  them equally specific or the show half loses.
- **There is no time slider.** Tapping a stop — a pin or a row — is the only clock: that stop is
  `.now` and everything earlier that day goes grey. A day opens at its first stop, or during the trip
  at the stop you should be at by now. A stop can appear twice, so selection matches day and index.
- **Pinch, drag, wheel and the +/− buttons move the `viewBox`**, and nothing else. JS writes the zoom
  factor to `--z`, and every stroke width, pin radius and label size divides by it to hold its size on
  screen; the pin-to-label gap is a CSS translate for the same reason, so generators emit labels at the
  pin with no offset. A drag is not a tap — a gesture that moved swallows its click.
- **`data-fit` on the view** makes picking a day fit to that day's pins. New Zealand sets it, since city
  days and island days cannot share a frame; Okinawa does not, so its island never moves.
- **Pins are not focusable** — the SVG is one `role="img"`, the stop rows are the keyboard path, and
  each pin carries a wide invisible `circle.hit` so a small dot stays hittable.
- **Regenerating** either map writes `.html` fragments next to the generator; splice them over the
  `<svg class="map">` and `<ul class="tl stoplist">` blocks, then bump `CACHE` in `sw.js`. Edit the
  place tables, never the generated coordinates. Each script documents its fetched inputs in its
  header; those are gitignored and come from an in-page `fetch()` in the chrome-devtools MCP, because
  `curl` reaches neither Overpass nor OSRM reliably. **Keep the footer credit to OSRM and OSM.**

Both project equirectangular with a `cos(lat)` correction, from OSM `natural=coastline` ways stitched
end to end.

`.map/build.py` — **Okinawa**: 69 pins over 3 days plus campsite / nature / food candidate layers,
told apart by shape (■ ▲ ◆). Window `lat 26.055–26.895 / lon 127.615–128.345`, `viewBox="0 0 778 1000"`,
keeping the 24 closed rings with area ≥ 18 px². Colour = day (`--acc`, `--acc2`, `--sun`), and the day
chips carry matching `.sw` swatches, so **the chips are the legend**.

`.map/nz.py` — **New Zealand**: 38 pins over 6 days, one day at a time, so every day uses the guide
accent and the chips carry no swatch. Window `lat -40.45 – -34.30 / lon 172.40–178.90`,
`viewBox="0 0 692 824"` — it stops just north of Cook Strait, because the trip never goes further south
and the South Island would otherwise clip into the corner as a tangle. The coastline is fetched in
eight tiles (one query for the island times out) and deduped by way id; with the island whole it
stitches into a single closed ring, clipped to the frame. A chain left *open* is closed along the frame
edge instead, and which way round is decided by testing known land and sea points, because OSM's
winding is not to be trusted. Simplified to 0.16 user units (about 130 m) — far finer than the overview
needs, because a day fit zooms to roughly 10×.

## The Japanese layer

`.i18n/` is the translation source of truth: `GLOSSARY.md` (tone spec + fixed place names),
`strings.json` (English, keyed by `sha1(slot|en)[:10]`) and `ja-*.json` (the Japanese by the same id).
Note the direction — `.i18n` keys on **English** while the shipped markup is Japanese with English in
`data-en`, so regenerating means flipping the file back to English-base first, running the
extract/inject scripts, then flipping again. An id hashes its English, so changing one word orphans
that translation — which is the point.

Three traps: strip the layer with `re.sub(r'( data-en="[^"]*")+', '', html)` — **the attribute only,
never unwrap a `<span>`**, since wrapper spans in `h2.section`, `a.outlink`, `.glabel` and the edit
button are load-bearing; injecting onto an already-injected file duplicates attributes; and a
`data-en`/`data-ja` value must reproduce any nested `span.u` byte-for-byte.

**Known drift:** the maps, the Day 2 snorkelling rewrite, the shelf and both English-only books added
strings that have never been through the extractor. Nothing is broken at runtime — re-extract before
the next translation pass.

## Editing content

1. Edit `index.html` directly. Day cards are `<details class="card day">` (or `.card.hike` /
   `.card.travel`) inside `.spine.days`, each with an hour-by-hour `<ul class="tl">`. Okinawa's
   campsites are `<details class="card camp wild|paid f-beach f-toilet f-shower">` in one flat list by
   road time from the Evertrail office (26.3794, 127.8257) — **not** from Naha Airport. The `f-*`
   classes drive `.camp-filters`; keep them in sync with the chips.
2. **Voice: factual only.** No tone, evaluation or persuasion — clipped fact-lists ("Calm bay, sunsets
   over the city. No toilets."), Japanese in 体言止め, never "worth it" or "the best". There are **no
   `.note` callouts**: a fact that matters goes in a bullet, a `<small>`, or a stat tile.
3. **Do not hand-edit a map's SVG** — change the generator's tables and regenerate. A new or moved
   stop needs its OSRM leg refetched too, or the line will not reach its pin.
4. Checklist rows are an `<input class="cb" id="ok-|se-|nz-packing-<group>-<index>">` plus its
   `<label class="checkrow" for="…">`; the prefix only has to be unique per book, since `seedFromDOM()`
   reads structure (`.group`, `.checkrow`, `.ctxt`, the `.gicon use` href), never ids.
5. **A private home address never goes in the markup** — the Pages site is public. Name the suburb.
6. **After any change to `index.html` or another cached asset, bump `CACHE` in `sw.js`** — otherwise
   installed phones keep serving the old copy.

**Place links** — resolving and verifying a Google Maps link: see `TRIPS.md`.

## Testing locally

Service workers need a real origin: `python3 -m http.server 8765`. To check offline, load once, confirm
the worker is activated, stop the server and reload. **An old worker serves stale HTML** — unregister it
and clear caches first. For the no-JS path set `documentElement.className='nojs'` and drop `data-place`.

## Deploying

Remote `git@github.com:huangwaylon/seattle.git` (personal github.com, SSH). The local `gh` CLI is
logged into Apple's internal GitHub — do **not** use it here. Commit and push to `main` (end commits
with the `Co-Authored-By` trailer); Pages rebuilds in about a minute. Asset paths are relative, so the
project site works under `/seattle/`.

**On iPhone:** open the live URL in Safari on Wi-Fi, let it load, Share → Add to Home Screen, then open
once from the icon while online. After a `CACHE` bump an installed app shows the refresh banner on its
next online launch. Installed PWAs escape Safari's 7-day storage cap, so the packing list survives —
install a week or two before the trip.

**Privacy:** the Pages site is public even for a private repo, and names the travellers and their
flight references. Flag this before adding more sensitive detail.
