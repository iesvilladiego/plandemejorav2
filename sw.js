/* Service Worker del Plan de Mejora V2026 - IES Virgen de Villadiego.
 * Alcance: /plandemejorav2/ - nunca controla páginas fuera de su subcarpeta,
 * así que no interfiere con el service worker del portal si lo tuviera.
 * Caches con prefijo propio "plandemejora-v2-": al activar solo se borran las
 * versiones anteriores de esta app, nunca las de otro SW del origen.
 * Generado por scripts/make_pwa.py; sube SW_VERSION para publicar cambios. */
var VERSION = 'v1.8.5';
var CACHE_NAME = 'plandemejora-v2-' + VERSION;
var APP_SHELL = [
    './',
    './index.html',
    './manifest.json',
    './icons/favicon.ico',
    './icons/favicon-16x16.png',
    './icons/favicon-32x32.png',
    './icons/apple-touch-icon.png',
    './icons/icon-192.png',
    './icons/icon-512.png',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js',
    'https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js',
    'https://cdnjs.cloudflare.com/ajax/libs/jspdf-autotable/3.5.28/jspdf.plugin.autotable.min.js',
    'https://www.gstatic.com/firebasejs/10.14.1/firebase-app-compat.js',
    'https://www.gstatic.com/firebasejs/10.14.1/firebase-firestore-compat.js'
];

self.addEventListener('install', function(event) {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(function(cache) { return cache.addAll(APP_SHELL); })
            .then(function() { return self.skipWaiting(); })
    );
});

self.addEventListener('activate', function(event) {
    event.waitUntil(
        caches.keys().then(function(nombres) {
            return Promise.all(nombres.map(function(nombre) {
                if (nombre.indexOf('plandemejora-v2-') === 0 && nombre !== CACHE_NAME) {
                    return caches.delete(nombre);
                }
            })).then(function() { return self.clients.claim(); })
        })
    );
});

self.addEventListener('fetch', function(event) {
    var req = event.request;
    if (req.method !== 'GET') return;

    /* Fuera del alcance de la app (p.ej. canales RPC de Firestore) no se
       toca nada: pasan directos a la red y nunca se cachean. */
    function cacheable(url) {
        return url.indexOf(self.registration.scope) === 0 || APP_SHELL.indexOf(url) !== -1;
    }
    if (!cacheable(req.url)) {
        event.respondWith(fetch(req));
        return;
    }

    /* Navegación (abrir la app): red primero para tener el HTML fresco;
       sin conexión se sirve la copia en caché. */
    if (req.mode === 'navigate') {
        event.respondWith(
            fetch(req).then(function(res) {
                var copia = res.clone();
                caches.open(CACHE_NAME).then(function(c) { c.put('./index.html', copia); });
                return res;
            }).catch(function() {
                return caches.match(req).then(function(hit) {
                    return hit || caches.match('./index.html');
                });
            })
        );
        return;
    }

    /* Resto de GET (shell local y CDN con versión fijada): caché primero
       y actualización en segundo plano. */
    event.respondWith(
        caches.match(req).then(function(hit) {
            var desdeRed = fetch(req).then(function(res) {
                if (res && res.ok) {
                    var copia = res.clone();
                    caches.open(CACHE_NAME).then(function(c) { c.put(req, copia); });
                }
                return res;
            }).catch(function() {
                return hit || Response.error();
            });
            return hit || desdeRed;
        })
    );
});
