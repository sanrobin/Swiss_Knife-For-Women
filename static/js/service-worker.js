// Service Worker for Swiss Knife for Women Safety App
const CACHE_NAME = 'swiss-knife-cache-v1';
const ASSETS_TO_CACHE = [
  '/',
  '/static/css/main.css',
  '/static/css/normalize.css',
  '/static/css/dark-mode.css',
  '/static/js/main.js',
  '/static/js/safety-map.js',
  '/static/images/logo.svg',
  '/static/images/favicon.ico',
  '/static/images/icons/locate.svg',
  '/static/images/icons/share.svg',
  '/static/manifest.json',
  '/safety-map',
  '/emergency',
  'https://unpkg.com/leaflet@1.7.1/dist/leaflet.css',
  'https://unpkg.com/leaflet@1.7.1/dist/leaflet.js'
];

// Install event - cache assets
self.addEventListener('install', event => {
  console.log('[Service Worker] Installing Service Worker...');
  
  // Skip waiting to ensure the new service worker activates immediately
  self.skipWaiting();
  
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('[Service Worker] Caching app shell and content');
        return cache.addAll(ASSETS_TO_CACHE);
      })
      .catch(error => {
        console.error('[Service Worker] Error during cache.addAll():', error);
      })
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', event => {
  console.log('[Service Worker] Activating Service Worker...');
  
  event.waitUntil(
    caches.keys()
      .then(keyList => {
        return Promise.all(keyList.map(key => {
          if (key !== CACHE_NAME) {
            console.log('[Service Worker] Removing old cache:', key);
            return caches.delete(key);
          }
        }));
      })
  );
  
  // Ensure the service worker takes control immediately
  return self.clients.claim();
});

// Fetch event - serve from cache, fall back to network
self.addEventListener('fetch', event => {
  // Skip cross-origin requests
  if (!event.request.url.startsWith(self.location.origin) && 
      !event.request.url.includes('unpkg.com/leaflet')) {
    return;
  }
  
  // For API requests, use network first, then cache
  if (event.request.url.includes('/api/') || 
      event.request.url.includes('/map/') || 
      event.request.url.includes('/safety/') || 
      event.request.url.includes('/emergency/') || 
      event.request.url.includes('/location/')) {
    event.respondWith(
      fetch(event.request)
        .then(response => {
          // Clone the response before using it
          const responseToCache = response.clone();
          
          caches.open(CACHE_NAME)
            .then(cache => {
              // Only cache successful responses
              if (response.status === 200) {
                cache.put(event.request, responseToCache);
              }
            });
          
          return response;
        })
        .catch(() => {
          // If network fails, try to serve from cache
          return caches.match(event.request);
        })
    );
  } else {
    // For non-API requests, use cache first, then network
    event.respondWith(
      caches.match(event.request)
        .then(response => {
          // Return cached response if found
          if (response) {
            return response;
          }
          
          // Clone the request before using it
          const fetchRequest = event.request.clone();
          
          // If not in cache, fetch from network
          return fetch(fetchRequest)
            .then(response => {
              // Check if valid response
              if (!response || response.status !== 200 || response.type !== 'basic') {
                return response;
              }
              
              // Clone the response before using it
              const responseToCache = response.clone();
              
              // Cache the fetched response
              caches.open(CACHE_NAME)
                .then(cache => {
                  cache.put(event.request, responseToCache);
                });
              
              return response;
            });
        })
    );
  }
});

// Handle push notifications
self.addEventListener('push', event => {
  console.log('[Service Worker] Push received:', event);
  
  const title = 'Swiss Knife for Women';
  const options = {
    body: event.data ? event.data.text() : 'Safety alert notification',
    icon: '/static/images/icons/icon-192x192.png',
    badge: '/static/images/icons/icon-72x72.png',
    vibrate: [100, 50, 100, 50, 100],
    data: {
      dateOfArrival: Date.now(),
      primaryKey: '1'
    },
    actions: [
      {
        action: 'view',
        title: 'View Map'
      },
      {
        action: 'emergency',
        title: 'Emergency'
      }
    ]
  };
  
  event.waitUntil(
    self.registration.showNotification(title, options)
  );
});

// Handle notification clicks
self.addEventListener('notificationclick', event => {
  console.log('[Service Worker] Notification click:', event);
  
  event.notification.close();
  
  // Handle different actions
  if (event.action === 'view') {
    clients.openWindow('/safety-map');
  } else if (event.action === 'emergency') {
    clients.openWindow('/emergency');
  } else {
    // Default action when notification itself is clicked
    clients.openWindow('/');
  }
});