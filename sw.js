const CACHE = 'guides-v18';
const ASSETS = [
  './', './index.html', './manifest.webmanifest', './icon-180.png', './icon-512.png',
  './images/okinawa-hero.jpg',
  './images/nz-hero.jpg',
  './images/mount-rainier.jpg',
  './images/lake-22.webp',
  './images/snow-lake.webp',
  './images/skyline-loop.webp',
  './images/enchantments.webp',
  './images/bridal-veil.webp',
  './images/mount-pilchuck.webp',
  './images/lake-valhalla.webp',
  './images/talapus-lake.webp',
  './images/dive/boat.jpg',
  './images/tidepool/pool.jpg',
  './images/tidepool/scramble.jpg',
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
  // No skipWaiting here: the page shows a "New version available" banner and this
  // worker takes over only when the user taps Refresh (or the app is fully closed).
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
        // Our own complete 200s only — opaque, 4xx/5xx and 206 would poison the cache.
        if(resp && resp.ok && resp.type==='basic'){
          var copy = resp.clone();
          caches.open(CACHE).then(function(c){c.put(e.request, copy);});
        }
        return resp;
      }).catch(function(){
        // Offline and uncached: the shell for navigations, an honest error otherwise.
        return e.request.mode==='navigation' ? caches.match('./index.html') : Response.error();
      });
    })
  );
});
