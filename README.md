# Seattle 2026 🏔️

A self-contained, offline-first travel itinerary for a July 2026 trip to Seattle, WA — built as an installable PWA for iPhone.

**Live:** https://huangwaylon.github.io/seattle/

## Features
- 18-day itinerary, 8 hikes with stats, and an editable packing list — all in one file.
- Works **fully offline** once installed (service worker caches everything).
- **Tabs + expanding cards**; the **packing list is fully editable** — add, rename, and remove categories and items — and everything **saves** to `localStorage`.
- Degrades gracefully: with JavaScript off (e.g. a plain file preview) all content still shows, just stacked instead of tabbed.

## Files
| File | Purpose |
|------|---------|
| `index.html` | The entire app — HTML content + inline CSS + inline JS. |
| `images/` | Mt Rainier hero + 8 hike photos (real files, precached for offline use). |
| `sw.js` | Service worker — caches the app shell and images for offline use. |
| `manifest.webmanifest` | PWA manifest (name, icons, standalone display). |
| `icon-180.png` / `icon-512.png` | App icons. |

## Install on iPhone (do once, on Wi-Fi)
1. Open the live URL in **Safari** and let it fully load (caches it offline).
2. **Share → Add to Home Screen**.
3. Open it once from the icon while online. Done — it now runs offline with saved state.

## Editing
`index.html` is the source of truth — the itinerary is static HTML, so edit it directly. The packing list is data-driven: its static rows seed an editable model that each device saves to `localStorage` (so on-device edits survive). After any change, bump the cache name in `sw.js` (e.g. `seattle-2026-v12` → `v13`) so installed phones pick up the new version.
