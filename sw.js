/* Two caches. SHELL is the app itself and is renamed on every deploy. MEDIA is every photo, under a
   name that never changes, so a deploy that only touched index.html does not send each phone 5 MB
   of pictures it already has. That rests on one rule: a photo is never changed in place — a changed
   photo gets a new filename, and the old one leaves the list below. */
const SHELL = 'shell-v20';
const MEDIA = 'media';
/* icon-512 is not here: iOS installs from the 180 apple-touch-icon and never asks for it. */
const APP = ['./', './index.html', './manifest.webmanifest', './icon-180.png'];
const PHOTOS = [
  './images/covers/okinawa.jpg', './images/covers/seattle.jpg', './images/covers/nz.jpg',
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
/* The versions before the split kept everything in one cache; a first split install borrows
   their photos rather than fetching them again. */
const LEGACY = /^guides-v/;

self.addEventListener('install', function(e){
  // No skipWaiting here: the page shows a "New version available" banner and this
  // worker takes over only when the user taps Refresh (or the app is fully closed).
  e.waitUntil(Promise.all([
    /* cache:'reload' goes past the HTTP cache: Pages sends max-age=600, and within that window a
       new version could otherwise be filled with the previous build's index.html. */
    caches.open(SHELL).then(function(c){
      return c.addAll(APP.map(function(u){return new Request(u,{cache:'reload'});}));
    }),
    caches.open(MEDIA).then(function(media){
      return Promise.all(PHOTOS.map(function(u){
        return media.match(u).then(function(hit){
          if(hit) return;
          return caches.keys().then(function(ks){
            var old=ks.filter(function(k){return LEGACY.test(k);});
            return old.reduce(function(p,k){
              return p.then(function(r){return r||caches.open(k).then(function(c){return c.match(u);});});
            },Promise.resolve(null));
          }).then(function(r){return r?media.put(u,r):media.add(u);});
        });
      }));
    })
  ]));
});
self.addEventListener('message', function(e){
  if(e.data && e.data.type==='SKIP_WAITING') self.skipWaiting();
});
self.addEventListener('activate', function(e){
  var keep=PHOTOS.map(function(u){return new URL(u,self.location).href;});
  e.waitUntil(caches.keys().then(function(ks){
    return Promise.all(ks.filter(function(k){return k!==SHELL&&k!==MEDIA;}).map(function(k){return caches.delete(k);}));
  }).then(function(){
    /* A photo that left the list leaves the cache. */
    return caches.open(MEDIA).then(function(c){
      return c.keys().then(function(rs){
        return Promise.all(rs.filter(function(r){return keep.indexOf(r.url)<0;}).map(function(r){return c.delete(r);}));
      });
    });
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
          caches.open(SHELL).then(function(c){c.put(e.request, copy);});
        }
        return resp;
      }).catch(function(){
        // Offline and uncached: the shell for navigations, an honest error otherwise.
        return e.request.mode==='navigation' ? caches.match('./index.html') : Response.error();
      });
    })
  );
});
