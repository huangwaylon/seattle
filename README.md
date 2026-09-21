# Okinawa 2026 🌺

A self-contained, offline-first travel itinerary for an October 2026 camping road trip on Okinawa's main island — built as an installable PWA for iPhone.

**Live:** https://huangwaylon.github.io/seattle/

## Features
- 3-day itinerary, logistics cards (flights, the Jimny, weather & hazards), and an editable packing list.
- **Campsites tab** — all 26 drivable main-island campsites with photos, ordered by real road time from Naha Airport, filterable by free / paid / beach / toilet / shower.
- **Eat tab** — kakigori, cafes and sweets sourced from Japanese guides, each checked open on the trip dates and tagged with the day it fits.
- Works **fully offline** once installed (service worker caches everything).
- **Metric ⇄ imperial toggle** swaps every distance and temperature; the choice persists.
- **English ⇄ 日本語 toggle** — the whole app is translated, guidebook-style; the choice persists.
- Degrades gracefully: with JavaScript off (e.g. a plain file preview) all content still shows, just stacked instead of tabbed.

## Files
| File | Purpose |
|------|---------|
| `index.html` | The entire app — HTML content + inline CSS + inline JS. |
| `images/okinawa-hero.jpg` | Hero photo (the Jimny + rooftop tent), precached for offline use. |
| `images/camps/` | One photo per campsite, precached for offline use. |
| `sw.js` | Service worker — caches the app shell and hero for offline use. |
| `manifest.webmanifest` | PWA manifest (name, icons, standalone display). |
| `icon-180.png` / `icon-512.png` | App icons. |
| `.i18n/` | Translation source (glossary, extracted strings, Japanese). Not shipped — see CLAUDE.md. |

## Install on iPhone (do once, on Wi-Fi)
1. Open the live URL in **Safari** and let it fully load (caches it offline).
2. **Share → Add to Home Screen**.
3. Open it once from the icon while online. Done — it now runs offline with saved state.

## Editing
`index.html` is the source of truth — the itinerary and campsites are static HTML, so edit them directly. The packing list is data-driven: its static rows seed an editable model that each device saves to `localStorage` (so on-device edits survive). After any change, bump the cache name in `sw.js` (e.g. `okinawa-2026-v1` → `v2`) so installed phones pick up the new version.
