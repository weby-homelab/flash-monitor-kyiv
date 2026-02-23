const CACHE_NAME = 'flash-monitor-v4';
const ASSETS = [
  '/',
  '/static/icon.svg',
  '/static/manifest.json'
];

// Install Event
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(ASSETS);
    })
  );
});

// Fetch Event
self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);

  // NEVER cache API requests or generated charts
  if (url.pathname.startsWith('/api/') || url.pathname.endsWith('.png')) {
    event.respondWith(fetch(event.request));
    return;
  }

  // Cache First for other assets
  event.respondWith(
    caches.match(event.request).then((response) => {
      return response || fetch(event.request);
    })
  );
});