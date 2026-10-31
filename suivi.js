// État de lecture propre à cet appareil : articles lus, réponses aux quiz, articles gardés.
// Rangé dans le stockage local ; chaque accès est protégé (stockage parfois indisponible).

import { imagesDe } from "./edition.js";

const CACHE_GARDES = "gardes";
const SEMAINES_GARDEES = 26; // état de lecture et quiz : six mois

function lire(cle, defaut) {
  try {
    const v = localStorage.getItem(cle);
    return v ? JSON.parse(v) : defaut;
  } catch {
    return defaut;
  }
}

function ecrire(cle, valeur) {
  try {
    localStorage.setItem(cle, JSON.stringify(valeur));
  } catch {}
}

// Supprime les entrées "prefixe.AAAA-MM-JJ..." plus vieilles que six mois.
function purger(prefixe) {
  const limite = new Date(Date.now() - SEMAINES_GARDEES * 7 * 864e5).toISOString().slice(0, 10);
  try {
    for (let i = localStorage.length - 1; i >= 0; i--) {
      const k = localStorage.key(i);
      if (k?.startsWith(prefixe) && k.slice(prefixe.length, prefixe.length + 10) < limite) localStorage.removeItem(k);
    }
  } catch {}
}

// Articles lus d'une rubrique d'une édition : { ids: Set, marquer(id) }.
export function lus(date, rubrique) {
  purger("lus.");
  const cle = `lus.${date}.${rubrique}`;
  const ids = new Set(lire(cle, []));
  return {
    ids,
    marquer(id) {
      if (ids.has(id)) return false;
      ids.add(id);
      ecrire(cle, [...ids]);
      return true;
    },
  };
}

// Rubriques entièrement lues d'une édition (pour marquer les onglets).
export function rubriquesLues(date, ancresParRubrique) {
  const faites = new Set();
  for (const [id, ancres] of Object.entries(ancresParRubrique)) {
    const vus = new Set(lire(`lus.${date}.${id}`, []));
    if (ancres.length && ancres.every((a) => vus.has(a))) faites.add(id);
  }
  return faites;
}

// Quiz d'une rubrique : { reponses: [index ou -1], enregistrer(liste), recommencer() }.
export function reponsesQuiz(edition, rubrique, questions) {
  purger("quiz.");
  const cle = `quiz.${edition.date}.${rubrique}`;
  const r = lire(cle, {}).reponses ?? [];
  return {
    reponses: questions.map((_, i) => (Number.isInteger(r[i]) ? r[i] : -1)),
    enregistrer: (liste) => ecrire(cle, {
      reponses: liste,
      semaine_texte: edition.semaine_texte,
      rubrique,
      total: questions.length,
      justes: questions.filter((q, i) => liste[i] === q.reponse).length,
    }),
    recommencer: () => {
      try { localStorage.removeItem(cle); } catch {}
    },
  };
}

// Quiz terminés : [{ date, rubrique, justes, total, semaine_texte }], du plus récent au plus ancien.
export function scores() {
  const liste = [];
  try {
    for (let i = 0; i < localStorage.length; i++) {
      const k = localStorage.key(i);
      if (!k?.startsWith("quiz.")) continue;
      const v = lire(k, null);
      if (v?.reponses?.length && v.reponses.every((x) => x >= 0)) liste.push({ date: k.slice(5, 15), ...v });
    }
  } catch {}
  return liste.sort((a, b) => b.date.localeCompare(a.date));
}

// Articles gardés : [{ cle, date, semaine_texte, article }], du plus récent au plus ancien.
export function gardes() {
  return lire("gardes", []);
}

export function estGarde(cle) {
  return gardes().some((g) => g.cle === cle);
}

export async function garder(cle, edition, article) {
  const liste = gardes().filter((g) => g.cle !== cle);
  liste.unshift({ cle, date: edition.date, semaine_texte: edition.semaine_texte, article });
  ecrire("gardes", liste);
  // Images de l'article : copie dans un cache à part, qui survit au remplacement de l'édition.
  if (!("caches" in self)) return;
  try {
    const cache = await caches.open(CACHE_GARDES);
    await Promise.all(imagesDe({ rubriques: [{ articles: [article] }] }).map(async (url) => {
      if (await cache.match(url)) return;
      const rep = (await caches.match(url)) || (await fetch(url, { mode: "no-cors" }));
      await cache.put(url, rep.clone());
    }));
  } catch {}
}

export async function retirer(cle) {
  const liste = gardes();
  const g = liste.find((x) => x.cle === cle);
  const reste = liste.filter((x) => x.cle !== cle);
  ecrire("gardes", reste);
  if (!g || !("caches" in self)) return;
  // Retirer les images qui ne servent plus à aucun article gardé.
  try {
    const utiles = new Set(imagesDe({ rubriques: [{ articles: reste.map((x) => x.article) }] }));
    const cache = await caches.open(CACHE_GARDES);
    await Promise.all(imagesDe({ rubriques: [{ articles: [g.article] }] }).filter((u) => !utiles.has(u)).map((u) => cache.delete(u)));
  } catch {}
}
