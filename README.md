# うめうぇの旅 📚

A self-contained, offline-first **bookshelf of trip guide books**, built as an installable PWA for
iPhone. Tap a book and it opens; close the app and it reopens where you left off.

**Live:** https://huangwaylon.github.io/seattle/

Two books, both 2026:

- **沖縄 2026** — Oct 10–12, a camping road trip on the main island in a Jimny with a rooftop tent.
  Itinerary, an inline-SVG map, all 26 drivable campsites, and a packing list. Fully bilingual 日本語 / English.
- **Seattle 2026** — Jul 2–19, a Pacific Northwest hiking trip. Itinerary with per-hike stats, photos
  and trail-map links, plus its own packing list.

## Features

- **The shelf** — cloth-spined books on a wooden shelf; the cover zooms up and turns open like a page.
- **Works fully offline** once installed; the service worker caches every asset.
- **Map tab (Okinawa)** — the real road route for each day, its stops, and campsite / nature / food
  candidates as optional layers. Tap a pin or a row and everything behind you on the day greys out.
  No tiles, no network.
- **Campsites tab (Okinawa)** — 26 sites with photos, ordered by road time from the office where the
  car is collected, filterable by free / paid / beach / toilet / shower.
- **Editable packing list** per book — add, rename, reorder and delete categories and items; saved on
  the device.
- **Metric ⇄ imperial** everywhere, and **English ⇄ 日本語** in the Okinawa book; both choices persist.
- Degrades gracefully: with JavaScript off (a plain file preview) every book still shows, stacked
  instead of tabbed.

## Files

| File | Purpose |
|------|---------|
| `index.html` | The entire app — content + inline CSS + inline JS. |
| `images/` | Book covers and card photos, all precached for offline use. |
| `sw.js` | Service worker — caches the app shell and every image. |
| `manifest.webmanifest`, `icon-180.png`, `icon-512.png` | PWA manifest and icons. |
| `.i18n/` | Translation source (glossary, strings, Japanese). Not shipped — see CLAUDE.md. |
| `.map/build.py` | Generator for the map's SVG geometry. Not shipped — see CLAUDE.md. |

## Install on iPhone (once, on Wi-Fi)

1. Open the live URL in **Safari** and let it fully load.
2. **Share → Add to Home Screen**.
3. Open it once from the icon while online. It now runs offline with saved state.

## Editing

`index.html` is the source of truth; itineraries, campsites and the packing seed rows are static HTML,
so edit them directly. After any change, bump `CACHE` in `sw.js` so installed phones pick up the new
version. See `CLAUDE.md` for the architecture and conventions.
