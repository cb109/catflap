self.addEventListener('install', function(e) {
  e.waitUntil(
    caches.open('catflap').then(function(cache){
      cache.addAll([

      ]);
    })
  );
});

self.addEventListener('fetch', function(e) {

});
