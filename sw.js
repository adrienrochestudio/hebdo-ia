// Changer VERSION à chaque modification de l'app, sinon l'iPhone garde l'ancienne version.
// Les éditions ne passent pas par VERSION : edition.js les gère (caches "index" et "edition-AAAA-MM-JJ").
const VERSION = "2026-10-31.3";
const CACHE_APP = `app-${VERSION}`;
const FICHIERS = [
  "./",
  "./index.html",
  "./styles.css",
  "./app.js",
  "./edition.js",
  "./rendu.js",
  "./textes.js",
  "./suivi.js",
  "./manifest.webmanifest",
  "./fonts/source-serif-4-var.woff2",
  "./fonts/source-serif-4-var-italic.woff2",
  "./icons/logo.svg",
  "./icons/icon-180.png",
  "./icons/icon-192.png",
  "./icons/icon-512.png",
];

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(CACHE_APP).then((c) => c.addAll(FICHIERS)));
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys()
      .then((cles) => Promise.all(cles.filter((k) => k.startsWith("app-") && k !== CACHE_APP).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("message", (e) => {
  if (e.data === "activer") self.skipWaiting();
});

self.addEventListener("fetch", (e) => {
  const req = e.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);

  // Index et éditions : edition.js gère réseau puis cache lui-même.
  if (url.origin === location.origin && url.pathname.includes("/editions/") && url.pathname.endsWith(".json")) return;

  // Images (schémas, cartes, images libres externes) : copie locale d'abord.
  if (req.destination === "image") {
    e.respondWith(caches.match(req).then((c) => c || fetch(req)));
    return;
  }

  if (url.origin !== location.origin) return;

  // Fichiers de l'app : cache d'abord, page d'accueil en dernier recours.
  e.respondWith(
    caches.match(req, { ignoreSearch: true }).then((c) =>
      c || fetch(req).catch(() => (req.mode === "navigate" ? caches.match("./index.html") : Response.error()))
    )
  );
});
