# CLAUDE.md

Guidance for this repo — keep it accurate. Per-trip facts live in `TRIPS.md`.

## What this is

A single-page, **offline-first PWA bookshelf of trip guide books** for iPhone. The whole app (HTML,
CSS, JS, two inline-SVG maps) lives in one self-contained `index.html`. Photos are real files in
`images/`; the service worker makes it fully offline once loaded.

Three books: **Okinawa 2026** (Oct 10–12, camping road trip), **Seattle 2026** (Jul 2–19, hiking)
and **New Zealand 2027** (Feb 11–16, Auckland and Taranaki). Tap a book and the cover zooms and
turns open; a back button returns to the shelf, and where the reader was is remembered across
launches.

Live: https://huangwaylon.github.io/seattle/ — still named `seattle` from the first trip, on purpose.

## Files

| File | Role |
|------|------|
| `index.html` | The entire app. **Source of truth — edit directly.** |
| `images/okinawa-hero.jpg`, `mount-rainier.jpg`, `nz-hero.jpg` | The three heroes. |
| `images/covers/*.jpg` | The shelf's covers: 560×760 crops of the heroes, so the shelf decodes a fifth of the pixels it would otherwise. |
| `images/camps/*`, `tidepool/*`, `dive/*`, `cafe/*` | Okinawa card photos, 720 px (`dive/boat.jpg` is 442). `*.webp` are Seattle's hikes. |
| `sw.js` | Cache-first service worker: a versioned `SHELL` cache for the app, a fixed-name `media` cache for the photos. A new worker waits for the refresh banner (or a full app close). |
| `manifest.webmanifest`, `icon-180.png`, `icon-512.png` | PWA manifest and icons. |
| `.map/build.py`, `.map/nz.py` | Generators for the two maps. **Not shipped** — see "The maps". |
| `.i18n/` | Translation tooling and source. **Not shipped** — see "The Japanese layer". |
| `TRIPS.md` | Per-trip facts, verification state, open bookings. |

No build step, framework, dependencies or CDN assets; system fonts only. The only outbound links are
Google Maps, Evertrail and trail maps — they open externally and fail gracefully offline.

## Architecture

- **One attribute is the navigation state.** `data-place` on `<html>` is `shelf` or a book's slug and
  CSS shows that one place. The bootstrap script in `<head>` sets it before first paint and swaps
  `nojs` for `js-tabs`, so there is no flash; it persists in `localStorage['place']` and is mirrored
  into `history`. The bootstrap does not know which books exist — a slug with no book is corrected
  to `shelf` by the navigation module, which does.
- **Opening a book** zooms `#turner` (a fixed overlay holding the cover) from the book's rect to full
  screen, then rotates its inner page off the spine. The shelf's small cover is the bottom layer and
  the guide's hero goes over it as `--hero` only once `decode()` resolves, so no frame of the zoom
  waits on a decode; the shelf's animations pause (`html.turning`) while it runs. The zoom's scale
  is **uniform** and a `clip-path` trims the overhang to the book's rect, because scaling a viewport-shaped overlay down to a
  book-shaped one non-uniformly squeezed the photograph by half its width. One transition at a time,
  and a counter every navigation bumps lets a stale animation know not to finish. Reduced motion
  skips it.
- **Themes are token sets.** `:root` holds structure plus a neutral palette **and a default for every
  token the shared CSS reads**, so a theme that omits one degrades to something visible rather than
  to an invalid value. `.t-okinawa`, `.t-seattle` and `.t-nz` each declare their own colours,
  including `--d1..--d6` for map days. Nothing in the shared CSS names a guide.
- **The shelf** is one recessed case of rows, on warm paper a shade off every guide background so
  opening a book is not a jump. Each book is a 3D scene: a cloth `.book-spine` face hinged
  (`rotateY(90deg)`) to the photo `.book-cover` — that face is seen from behind, so `.spine-txt` is
  mirrored to read right. It is a touch UI, so there is **no hover state**: each book turns, floats
  and slides a gloss on cycle lengths given per book (`--sway`, `--float` and their delays, inline),
  so no two fall into step. Each book is an `<a href="#g-…">`, so the no-JS path still navigates.
  A book's *title* is never translated — on the cover as on the spine — only its eyebrow and dates.
  The cover's fore-edge round is **kept small (6px) on purpose**: the cover is clipped under a
  perspective matrix, where the corner arc collapses to one un-antialiased chord, and at 12px that
  chord cut a visible dark triangle off the bottom-right of every cover at the far end of the sway.
  A mask, a `clip-path`, a forced render surface and a radius on the children all chamfer the same
  way — the fault is the perspective, not how the round is asked for.
- **Adding a book** means: a `.book` in a `.books` grid (two per row, each row followed by a
  `.shelf-plank`), an `<article class="guide t-slug">`, a theme block, and one two-line block giving
  the place its `--shell` and its `display:block`. Nothing else.
- **Tabs are pure CSS.** Each guide has one radio group (`name="tab-<slug>"`, unique per book) with
  each radio inside its `<label class="tabbtn">`, and `.guide:has(.t-<tab>:checked) .v-<tab>` shows
  the view. A new tab means one more selector there; the tab-bar highlight is already generic.
  `:has()` carries the whole mechanism, so there is an `@supports not (selector(:has(*)))` escape
  hatch to the stacked layout.
- **`.spine`** is the shared vertical timeline behind the cards; each carries a `.node` dot and
  optionally a `.lead-chip`. Accordions are native `<details>`, checklists are `.cb` + `.checkrow`.
- **No-JS fallback is required**, because plain file previews (macOS Quick Look) run without JS, so
  all content is static HTML. Without JS every place and view shows stacked, tab bars / back buttons
  / `.jsonly` controls are hidden, and the packing list shows its seed rows read-only. Anything a
  module *builds* is therefore marked `.jsonly`, which costs no-JS nothing.
- **Per-guide JS.** One loop wires each `.guide`: today, campsite filter, packing, map. A module
  whose markup that guide lacks returns early — which is how Seattle has no map and New Zealand no
  campsite filter. Language and units are document-wide instead, because both are global settings.
- **Modules build their own chrome.** `map(g)` creates the zoom cluster, one day chip per stop list
  and — only where the SVG has candidate layers — one layer chip per kind; `packing(g)` creates its
  two-button toolbar. So a book's day chips cannot fall out of step with its days, and a fourth book
  gets all of it for free. Labels come from `T()` and are re-set on `langchange`.
- **Units.** Every distance and temperature is a
  `<span class="u" data-metric="11.5 km" data-imperial="7 mi">11.5 km</span>` — both literals, so JS
  never does live maths. Metric is the default text, the choice persists in `localStorage['units']`,
  and the module is document-wide, so every book stays in sync.
- **One toolbar rhythm on every tab:** heading → intro 6px, intro → control row 20px, row → row 12px,
  row → content 14px. On the itinerary the hero → first card gap is the gutter instead, so the first
  card has the same air above it as it has beside it.
- **Settings live once, on the shelf** — a `.setbtn` opens a panel with the unit and language
  toggles, both applying to every book. Day cards open by default, so there is no expand-all button.
- **The packing list is the one exception to static markup.** Its `.group` rows are both the no-JS
  fallback and the one-time seed: JS builds a model from them, or restores the saved one, then
  re-renders. **Edit list** renames, adds, deletes and reorders; blanks are pruned on exit. Saved per
  book as `localStorage['packingData:<slug>']` =
  `{v:2, cats:[{id,name,nameJa,icon,items:[{id,text,textJa,note,noteJa,done}]}]}`, and a saved model
  wins over the seed. The seed itself is never saved — the first check or edit does that — so
  editing the defaults reaches every phone that has not touched that list. Ids come from `uid()`,
  and the DOM id carries the book because two guides seed a millisecond apart. Typing coalesces its
  writes; leaving edit mode flushes them. Okinawa also reads the pre-shelf `packingData` key, so old
  phones keep their list.
- **`LS.get` / `LS.set`** wrap every `localStorage` access — it throws in private and preview
  contexts, and a failure should just mean "no saved state". Never call `localStorage` directly.

## Touch and iPhone

Safari on iPhone is the platform; everything else is a convenience.

- **Every interactive control clears 44×44.** Where a chip or icon button is visually smaller, a
  `::before` pads the hit area out without changing how it looks. The destructive button in the
  packing editor keeps its distance from the reorder pair.
- **There is always a way back.** `.backbtn` is a child of the `.guide`, absolute on the itinerary so
  it scrolls away with the hero, and hidden on every other tab, which have no hero to hold it — from
  those, the tab bar leads back to the itinerary and the button is there. Where `:has()` is missing
  every view is stacked and there is no tab bar, so the hiding rule being dropped is the right
  outcome.
- `-webkit-text-size-adjust:100%` stops iOS inflating text in landscape; `100dvh` (with `100vh`
  first as the fallback) keeps full-height boxes off the URL bar; `-webkit-touch-callout:none` on the
  tappable, non-text elements stops the long-press preview sheet.
- The status bar is `default`, i.e. opaque, so iOS picks glyphs that contrast with `theme-color` —
  which JS keeps in step with the current place's `--shell`. `black-translucent` drew white glyphs
  over the near-white shelf and the light map, campsite and packing tabs.
- `--faint` and every de-emphasis colour clears 4.5:1 on the lightest *and* darkest surface it lands
  on. Check any new one: these books get read outdoors.
- A stop row is a real `<button>` inside its `<li>`, so Enter, Space and VoiceOver work with no
  keyboard handler of our own, and the list keeps its list semantics.

## The maps

Both maps are inline SVG — no tiles, no library, no network. Coastlines, routes, pins and the stop
timelines are **static markup generated at authoring time**; JS only sets state, so with JS off every
day and pin shows. Shared conventions, in the CSS and in the one `map(g)` module:

- **Layout:** no heading — the map card is pinned with `position:sticky`, and the day and layer chips
  and the stop list scroll under it. Both frames are 692×824, so both cards sit the same height.
- **Colour = day**, from the theme's `--d1..--d6`. One CSS rule per day covers the map layer, the
  chip fill and the chip swatch, so **the chips are the legend** and a seventh day costs one line.
  The "all days" chip draws every day at once and fits the whole frame.
- **State lives in attributes on the view:** `data-day`, plus Okinawa's `data-camp`/`nature`/`food`.
  Show/hide is all CSS under `.js-tabs`, so their absence means "show everything". The day rules hide
  `.leg`, `.stop` and `.stoplist` then re-show the chosen day's — both halves weigh the same, so keep
  them equally specific or the show half loses.
- **There is no time slider.** Tapping a stop — a pin or a row — is the only clock: that stop is
  `.now` and everything earlier that day goes grey. A day opens at its first stop, or during the trip
  at the stop you should be at by now. A stop can appear twice, so selection matches day and index.
- **Pinch, drag, wheel and the +/− buttons move the `viewBox`**, nothing else. JS writes the zoom
  factor to `--z`, and every stroke width, pin radius and label divides by it to hold its size on
  screen; the pin-to-label gap is a CSS translate for the same reason, so generators emit labels at
  the pin with no offset. Because nine rules read `--z`, every write restyles the whole SVG:
  **writes are coalesced to one per frame**, and a gesture measures the screen **once** at the start
  instead of reading layout back on every move. Screen points become map units through
  `getScreenCTM()`, never the bounding rect — `max-height:66vh` letterboxes the drawing inside its
  box and the rect knows nothing about that. A drag is not a tap, but only a drag *of the map*
  swallows its click, so a chip tapped straight afterwards still lands.
- **`data-fit` on the view** fits the view to the day's pins. New Zealand sets it, since city days
  and island days cannot share a frame; Okinawa does not, so its island never moves.
- **Pins are not focusable** — the SVG is one `role="img"` named by its `<title>`, the stop rows are
  the keyboard path, and each pin carries a wide invisible `circle.hit` so a small dot stays hittable.
- **Regenerating** either map writes `.html` fragments next to the generator; splice them over the
  `<svg class="map">` and `<ul class="tl stoplist">` blocks, then bump `SHELL` in `sw.js`. Edit the
  place tables, never the generated coordinates. Each script documents its fetched inputs in its
  header; those are gitignored and come from an in-page `fetch()` in the chrome-devtools MCP, because
  `curl` and `WebFetch` reach neither Overpass nor OSRM from here. OSRM does answer that in-page
  fetch, which is how drive times are checked. The on-page OSRM/OpenStreetMap credit was removed on
  request — the attribution ODbL asks for now lives only in the README.

Both project equirectangular with a `cos(lat)` correction, from OSM `natural=coastline` ways stitched
end to end.

`.map/build.py` — **Okinawa**: 70 pins over 3 days plus campsite / nature / food candidate layers,
told apart by shape (■ ▲ ◆). Window `lat 26.055–26.895 / lon 127.586–128.374`, keeping the 24 closed
rings with area ≥ 18 px²; the lon window is wider than the island needs so the frame comes out
692×824. Colour = day, from `--d1..--d3`.

`.map/nz.py` — **New Zealand**: 38 pins over 6 days, one day at a time. Window
`lat -40.45 – -34.30 / lon 172.40–178.90` — it stops just north of Cook Strait, because the trip
never goes further south and the South Island would otherwise clip into the corner as a tangle. The
coastline is fetched in six tiles (one query for the island times out) and deduped by way id; with
the island whole it stitches into a single closed ring, clipped to the frame. A chain left *open* is
closed along the frame edge instead, and which way round is decided by testing known land and sea
points, because OSM's winding is not to be trusted. Simplified to 0.16 user units (about 130 m) —
far finer than the overview needs, because a day fit zooms to roughly 12×.

Both emit paths as one absolute `M` and then relative `l` steps in whole tenths, each point rounded
*before* differencing so the steps sum back to exactly the `%.1f` coordinates — half the bytes of
absolute `L` commands for the same geometry.

## The Japanese layer

A book's markup is written in **one** language and every translatable element carries the **other**
in `data-en` or `data-ja`. The attribute an element *lacks* is the language its markup holds, so the
first sweep caches that and both directions work from then on. That is the whole mechanism: Okinawa
is authored in Japanese with `data-en`, New Zealand in English with `data-ja`, and neither is a
special case. The shelf and the update banner are swept too.

- The choice is **global**, in `localStorage['lang']` and mirrored on `<html lang>`. Japanese is the
  default. There is no per-book language attribute; a book "is bilingual" simply by carrying
  translations.
- A `data-*` value must reproduce any nested `span.u` **byte-for-byte**, and escapes its own quotes
  as `&quot;` — the dataset getter resolves them again, so `innerHTML` comes back identical.
- Runtime strings JS sets live in the `T()` table, keyed by name, two entries each.
- The packing list is skipped by the sweep and renders from its own bilingual model. Inside it,
  `span.ctxt` holds only the item text and the nested `<small>` holds the note, because
  `seedFromDOM()` reads them as two fields — everywhere else a `data-*` value includes its `<small>`.
- Icon-only controls get a `.sr` span for their name, not an `aria-label`: the sweep replaces
  `innerHTML`, so a name in an attribute cannot be translated.

`.i18n/i18n.py` is the tooling. It finds every translatable slot in a guide, keys it by
`sha1(slot|source)[:10]`, and injects the translation as one attribute on the opening tag — never
unwrapping a wrapper span, since the ones in `h2.section`, `a.outlink`, `.glabel`, `summary.head` and
the buttons are load-bearing.

    python3 .i18n/i18n.py slots   <guide>   # what would be translated, and from where
    python3 .i18n/i18n.py check   <guide>   # every slot translated? any stale leftovers?
    python3 .i18n/i18n.py extract <guide>   # -> .i18n/strings-<guide>.json
    python3 .i18n/i18n.py inject  <guide>   # .i18n/ja-<guide>.json -> index.html

Because an id hashes its source, changing one word of English orphans that translation — which is the
point. `check` is the one to run after editing content: it names every slot that lost its pair.
`GLOSSARY.md` is the tone spec and the fixed place names, in both trips. The map generators own their
pin labels, in both languages, so the tooling skips the generated SVG.

Editing content in a book that has been translated is a two-step job: edit, then `check`, then
translate whatever it names and `inject`. `strings.json` and the `ja-*.json` files for Okinawa
predate this tool and are keyed the same way but were built by hand; `strings-nz.json` /
`ja-nz.json` are the tool's own.

## Editing content

1. Edit `index.html` directly. Day cards are `<details class="card day">` (or `.card.hike` /
   `.card.travel`) inside `.spine.days`, each with an hour-by-hour `<ul class="tl">`. Okinawa's
   campsites are `<details class="card camp wild|paid f-beach f-toilet f-shower">` in one flat list
   by road time from the Evertrail office (26.3794, 127.8257) — **not** from Naha Airport. The `f-*`
   classes drive `.camp-filters`; keep them in sync with the chips.
2. **Voice: factual only.** No tone, evaluation or persuasion — clipped fact-lists ("Calm bay,
   sunsets over the city. No toilets."), Japanese in 体言止め for headings, labels and timeline rows
   and です・ます for notes, never "worth it". There are **no `.note` callouts**: a fact that matters
   goes in a bullet, a `<small>`, or a stat tile. A fact that is true of a dozen cards goes in the
   tab intro once, with a chip on the cards it applies to.
3. **Do not hand-edit a map's SVG** — change the generator's tables and regenerate. A new or moved
   stop needs its OSRM leg refetched too, or the line will not reach its pin.
4. Checklist rows are an `<input class="cb" id="ok-|se-|nz-packing-<group>-<index>">` plus its
   `<label class="checkrow" for="…">`; the prefix only has to be unique per book, since
   `seedFromDOM()` reads structure (`.group`, `.glabel .gname`, `.checkrow`, `.ctxt`, the
   `.gicon use` href), never ids.
5. **A private home address never goes in the markup** — the Pages site is public. Name the suburb.
6. **Every gap in a timeline must clear its drive** by the margin `TRIPS.md` records for that trip.
   Quote **per-leg** OSRM minutes, which is what the map draws.
7. **Bump `SHELL` in `sw.js` after any change**, or installed phones keep serving the old copy.
   Photos live in the `media` cache, whose name never changes, so a deploy does not re-send 5 MB of
   pictures. The price is one rule: **never change a photo in place** — a changed photo gets a new
   filename, and `PHOTOS` lists the new one. A photo that leaves the list leaves the cache.

**Place links** — resolving and verifying a Google Maps link: see `TRIPS.md`.

## Testing

Service workers need a real origin: `python3 -m http.server 8765`. To check offline, load once,
confirm the worker is activated, stop the server and reload. **An old worker serves stale HTML** —
unregister it and clear caches first. For the no-JS path set `documentElement.className='nojs'` and
drop `data-place`.

Chrome is drivable here through the chrome-devtools MCP, including iPhone-sized viewport and touch
emulation. Safari and Brave are **not**: AppleScript automation, screen capture and localhost CDP are
all blocked by this machine's security policy, so anything WebKit-specific has to be reasoned about
in the code and then confirmed on the phone.

## Deploying

Remote `git@github.com:huangwaylon/seattle.git` (personal github.com, SSH). The local `gh` CLI is
logged into Apple's internal GitHub — do **not** use it here. Commit and push to `main` (end commits
with the `Co-Authored-By` trailer); Pages rebuilds in about a minute. Asset paths are relative, so
the project site works under `/seattle/`.

**On iPhone:** open the live URL in Safari on Wi-Fi, let it load, Share → Add to Home Screen, then
open once from the icon while online. After a `SHELL` bump an installed app shows the refresh banner
on its next online launch. Installed PWAs escape Safari's 7-day storage cap — install a week or two
ahead.

**Privacy:** the Pages site is public even for a private repo, and names the travellers and their
flight references. Flag this before adding more sensitive detail.
