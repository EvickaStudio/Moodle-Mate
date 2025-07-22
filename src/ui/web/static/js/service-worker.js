// Simple service worker for Moodle-Mate Web Interface
// This prevents 404 errors when the browser tries to register a service worker

self.addEventListener('install', function(event) {
  // Skip waiting to activate immediately
  self.skipWaiting();
});

self.addEventListener('activate', function(event) {
  // Claim all clients immediately
  event.waitUntil(self.clients.claim());
});

// Handle fetch events (minimal implementation)
self.addEventListener('fetch', function(event) {
  // For now, just pass through all requests
  // This can be enhanced later for caching if needed
  event.respondWith(fetch(event.request));
}); 