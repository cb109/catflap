self.addEventListener('install', function(e) {
  e.waitUntil(
    caches.open('catflap').then(function(cache){
      cache.addAll([
        '/static/apexcharts.3.26.1.min.js',
        '/static/bulma.0.9.2.min.css',
        '/static/dayjs.1.8.28.min.js',
        '/static/icon-144x144.png',
        '/static/icon-192x192.png',
        '/static/icon-72x72.png',
        '/static/icon-96x96.png',
      ]);
    })
  );
});

self.addEventListener('fetch', function(e) {
  e.respondWith(
    caches.match(e.request).then(function(response) {
      return response || fetch(e.request);
    })
  );
});
