const CACHE = 'okinawa-2026-v11';
const ASSETS = [
  './', './index.html', './manifest.webmanifest', './icon-180.png', './icon-512.png',
  './images/okinawa-hero.jpg',
  './images/dive/boat.jpg',
  './images/cafe/kajinho.jpg',
  './images/camps/adan-beach-campsite.jpg',
  './images/camps/aha-yanbaru.jpg',
  './images/camps/azama-sun-beach-camping-ground.jpg',
  './images/camps/base-camp.jpg',
  './images/camps/benoki-camp-spot.jpg',
  './images/camps/daiboo-river-camp.jpg',
  './images/camps/fukuchi-river-seaside-park.jpg',
  './images/camps/henan-bridge.jpg',
  './images/camps/hentona-camp-spot.jpg',
  './images/camps/inamine-camp-spot.jpg',
  './images/camps/katsuren-beach.jpg',
  './images/camps/kita-nashiro-beach.jpg',
  './images/camps/koki-camp-spot.jpg',
  './images/camps/kokyono-beach.jpg',
  './images/camps/kouri-island-camp-ground.jpg',
  './images/camps/kudeken-beach.jpg',
  './images/camps/nago-castle-bridge-spot.jpg',
  './images/camps/neos-outdoor-park.jpg',
  './images/camps/okinawa-prefectural-people-s-forrest.jpg',
  './images/camps/oku-beach-road.jpg',
  './images/camps/okuma-mountains.jpg',
  './images/camps/tonokiya-campsite.jpg',
  './images/camps/tsuha-beach-camp-spot.jpg',
  './images/camps/yagaji-beach-campsite.jpg',
  './images/camps/yagajima-spot.jpg',
  './images/camps/yanbaru-discovery-forest.jpg',
];
self.addEventListener('install', function(e){
  // Precache the shell, but DON'T skipWaiting automatically — the page surfaces a
  // "New version available" banner and only this newer worker takes over when the
  // user taps Refresh (it still activates on its own once the app is fully closed).
  e.waitUntil(caches.open(CACHE).then(function(c){return c.addAll(ASSETS);}));
});
self.addEventListener('message', function(e){
  if(e.data && e.data.type==='SKIP_WAITING') self.skipWaiting();
});
self.addEventListener('activate', function(e){
  e.waitUntil(caches.keys().then(function(ks){
    return Promise.all(ks.filter(function(k){return k!==CACHE;}).map(function(k){return caches.delete(k);}));
  }).then(function(){return self.clients.claim();}));
});
self.addEventListener('fetch', function(e){
  if(e.request.method!=='GET') return;
  e.respondWith(
    caches.match(e.request).then(function(r){
      return r || fetch(e.request).then(function(resp){
        // Only cache our own complete, successful responses — never opaque
        // cross-origin, 4xx/5xx, or 206 partial responses (they'd poison the cache).
        if(resp && resp.ok && resp.type==='basic'){
          var copy = resp.clone();
          caches.open(CACHE).then(function(c){c.put(e.request, copy);});
        }
        return resp;
      }).catch(function(){
        // Offline + uncached: fall back to the app shell only for page navigations.
        // For other requests (images, etc.) fail honestly rather than returning HTML.
        return e.request.mode==='navigation' ? caches.match('./index.html') : Response.error();
      });
    })
  );
});
