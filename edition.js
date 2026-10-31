// Accès aux éditions publiées : réseau d'abord, copie locale ensuite.
// editions/index.json : liste des éditions, de la plus récente à la plus ancienne.
// editions/AAAA-MM-JJ/edition.json : une édition (trois rubriques), avec ses images dans img/.
// Hors ligne : l'index, la dernière édition et l'édition ouverte (caches "edition-AAAA-MM-JJ").

const INDEX = new URL("./editions/index.json", location.href).href;
const CACHE_INDEX = "index";
const DELAI_RESEAU_MS = 8000;
const DATE = /^\d{4}-\d{2}-\d{2}$/;

const adresse = (date) => new URL(`./editions/${date}/edition.json`, location.href).href;

async function depuisReseau(url) {
  const ctrl = new AbortController();
  const minuteur = setTimeout(() => ctrl.abort(), DELAI_RESEAU_MS);
  try {
    const rep = await fetch(url, { cache: "no-store", signal: ctrl.signal });
    if (!rep.ok) return null;
    return await rep.json();
  } catch {
    return null;
  } finally {
    clearTimeout(minuteur);
  }
}

async function depuisCache(url) {
  if (!("caches" in self)) return null;
  try {
    const rep = await caches.match(url);
    return rep ? await rep.json() : null;
  } catch {
    return null;
  }
}

const enJson = (donnees) => new Response(JSON.stringify(donnees), {
  headers: { "Content-Type": "application/json; charset=utf-8" },
});

// Liste des éditions : [{ date, numero, semaine_texte }]. { liste, source } ou null.
export async function index() {
  const enLigne = await depuisReseau(INDEX);
  if (Array.isArray(enLigne)) {
    try { await (await caches.open(CACHE_INDEX)).put(INDEX, enJson(enLigne)); } catch {}
    return { liste: enLigne.filter((e) => DATE.test(e.date)), source: "reseau" };
  }
  const locale = await depuisCache(INDEX);
  return Array.isArray(locale) ? { liste: locale.filter((e) => DATE.test(e.date)), source: "cache" } : null;
}

// Une édition : { donnees, source } ou null.
export async function charger(date) {
  if (!DATE.test(date)) return null;
  const url = adresse(date);
  const locale = await depuisCache(url);
  // Une édition publiée ne change plus, sauf republication le jour même : le réseau d'abord quand même.
  const enLigne = await depuisReseau(url);
  if (enLigne) return { donnees: enLigne, source: "reseau" };
  return locale ? { donnees: locale, source: "cache" } : null;
}

// Toutes les images citées par une édition (ou un article seul : { rubriques: [{ articles: [a] }] }).
// Les "src" sont relatifs à la racine du site (editions/AAAA-MM-JJ/img/...).
export function imagesDe(donnees) {
  const urls = new Set();
  const visiter = (b) => {
    if (!b || typeof b !== "object") return;
    if (Array.isArray(b.elements)) b.elements.forEach(visiter);
    const src = b.src || b.url;
    if (src) urls.add(src);
  };
  for (const r of donnees.rubriques ?? []) {
    visiter(r.une?.image);
    for (const a of r.articles ?? []) {
      visiter(a.couverture);
      (a.blocs ?? []).forEach(visiter);
    }
  }
  return [...urls].map((u) => new URL(u, location.href).href);
}

// Enregistre une édition et ses images pour la lecture hors ligne. Ne garde que `garder` (dates).
// Renvoie le nombre d'images non enregistrées.
export async function enregistrer(donnees, garder) {
  if (!("caches" in self) || !DATE.test(donnees?.date ?? "")) return 0;
  const url = adresse(donnees.date);
  const nom = `edition-${donnees.date}`;
  let manquees = 0;
  try {
    const cache = await caches.open(nom);
    await cache.put(url, enJson(donnees));
    await Promise.all(imagesDe(donnees).map(async (img) => {
      try {
        if (await cache.match(img)) return;
        // CORS d'abord (Wikimedia et Our World in Data l'acceptent) pour vérifier le statut ;
        // repli no-cors : réponse opaque, gardée faute de mieux.
        let rep;
        try {
          rep = await fetch(img, { mode: "cors" });
        } catch {
          rep = await fetch(img, { mode: "no-cors" });
        }
        if (rep.type !== "opaque" && !rep.ok) throw new Error(String(rep.status));
        await cache.put(img, rep);
      } catch {
        manquees += 1;
      }
    }));
    const utiles = new Set(garder.map((d) => `edition-${d}`));
    const noms = await caches.keys();
    await Promise.all(noms.filter((n) => n.startsWith("edition-") && !utiles.has(n)).map((n) => caches.delete(n)));
  } catch {}
  return manquees;
}
