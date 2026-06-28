const CACHE = 'seattle-2026-v15';
const ASSETS = [
  './', './index.html', './manifest.webmanifest', './icon-180.png', './icon-512.png',
  './images/mount-rainier.jpg',
  './images/lake-22.webp',
  './images/snow-lake.webp',
  './images/skyline-loop.webp',
  './images/enchantments.webp',
  './images/bridal-veil.webp',
  './images/mount-pilchuck.webp',
  './images/lake-valhalla.webp',
  './images/talapus-lake.webp',
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
