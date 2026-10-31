// Rendu d'une rubrique de l'édition (schéma du JSON : en tête de outils/publier.py).
// Tout le texte passe par textContent : aucun HTML venu des données n'est interprété.

import { T } from "./textes.js";

function el(balise, classe, texte) {
  const n = document.createElement(balise);
  if (classe) n.className = classe;
  if (texte != null) n.textContent = texte;
  return n;
}

// Seuls les liens https sont rendus cliquables.
function lien(source, texte) {
  let url = null;
  try { url = new URL(source.url).protocol === "https:" ? source.url : null; } catch {}
  if (!url) return el("span", null, texte ?? source.titre);
  const a = el("a", null, texte ?? source.titre);
  a.href = url;
  a.target = "_blank";
  a.rel = "noopener noreferrer";
  return a;
}

// Un média ou une institution n'apparaît qu'une fois, sous son nom court.
function sourcesUniques(sources) {
  const vus = new Set();
  return (sources ?? []).filter((s) => {
    const nom = (s.titre || "").trim().toLowerCase();
    if (!nom || vus.has(nom)) return false;
    vus.add(nom);
    return true;
  });
}

function ligneSources(toutes, apres) {
  const p = el("p", "note");
  const sources = sourcesUniques(toutes);
  if (!sources.length) return p;
  p.append(sources.length === 1 ? T.source : T.sources);
  sources.forEach((s, i) => {
    if (i) p.append(", ");
    p.append(lien(s));
  });
  if (apres) p.append(`. ${apres}`);
  return p;
}

function legende(element) {
  if (!element.legende && !element.credit && !element.lien) return null;
  const c = el("figcaption", "note", element.legende || "");
  if (element.lien) {
    if (c.textContent) c.append(" ");
    c.append(lien({ url: element.lien }, T.versionInteractive), ".");
  }
  if (element.credit) {
    if (c.textContent) c.append(" ");
    c.append(lien(element.credit), ".");
  }
  return c;
}

// Graphique Our World in Data : la version interactive s'ouvre à l'agrandissement.
function interactif(url) {
  try {
    const h = new URL(url).hostname;
    return h === "ourworldindata.org" || h.endsWith(".ourworldindata.org");
  } catch {
    return false;
  }
}

function image(element, { zoom = true } = {}) {
  const img = el("img");
  if (zoom && element.lien && interactif(element.lien)) img.dataset.interactif = element.lien;
  img.src = element.src || element.url;
  img.alt = element.type === "carte" ? `${T.carte}${element.ville}` : (element.legende || "");
  img.loading = "lazy";
  img.decoding = "async";
  if (zoom) {
    img.tabIndex = 0;
    img.dataset.zoom = "";
  }
  return img;
}

// Portraits et logos petits ; cartes de lieu à la largeur de la colonne.
function genre(element) {
  if (element.type === "carte" || element.nature === "carte_lieu") return "carte";
  if (element.nature === "portrait" || element.nature === "logo") return "photo portrait";
  if (!element.nature && (element.largeur ?? 552) <= 400) return "photo portrait";
  return "photo";
}

function figure(element, classe) {
  const f = el("figure", [genre(element), classe].filter(Boolean).join(" "));
  const img = image(element);
  img.addEventListener("error", () => f.remove(), { once: true });
  f.append(img);
  const l = legende(element);
  if (l) f.append(l);
  return f;
}

function bloc(b) {
  switch (b.type) {
    case "p":
      return el("p", "texte", b.texte);
    case "sous_titre":
      return el("h3", "sous-titre", b.texte);
    case "liste": {
      const d = el("div");
      for (const item of b.items ?? []) d.append(el("p", "texte liste", `- ${item}`));
      return d;
    }
    case "definitions": {
      // Glossaire : terme puis définition.
      const d = el("dl", "definitions");
      for (const { terme, definition } of b.items ?? []) d.append(el("dt", null, terme), el("dd", "texte", definition));
      return d;
    }
    case "image":
    case "carte":
      return figure(b, b.type === "image" && (b.largeur ?? 552) >= 500 && genre(b) === "photo" ? "large" : null);
    case "duo": {
      const d = el("div", "duo");
      for (const e of b.elements ?? []) d.append(figure(e));
      return d;
    }
    case "schema":
    case "barres":
      // Dessinés à la publication (outils/schema.py).
      return b.src ? figure({ ...b, type: "image", largeur: 1100 }, "large schema-image") : null;
    default:
      return null;
  }
}

// Bouton "Garder" en fin d'article ; app.js en gère l'état (cle : "date|rubrique|aN").
function actions(cle, options) {
  const p = el("p", "note actions");
  if (!cle || !options.garder) return p;
  const b = el("button", "action-garder");
  b.type = "button";
  b.dataset.garder = cle;
  options.garder.etiqueter(b);
  p.append(b);
  return p;
}

function corps(a, cle, options = {}) {
  const frag = document.createDocumentFragment();
  for (const b of a.blocs ?? []) {
    const n = bloc(b);
    if (n) frag.append(n);
  }
  if (a.a_retenir) frag.append(el("h3", "sous-titre", T.aRetenir), el("p", "texte", a.a_retenir));
  const fin = ligneSources(a.sources, a.note_sources);
  fin.classList.add("sources");
  frag.append(fin, actions(cle, options));
  return frag;
}

function une(u) {
  const s = el("section", "une encart");
  s.id = "une";
  s.append(el("h2", "rubrique-nom", T.essentiel), el("p", "une-texte", u.texte));
  if (u.image) s.append(bloc({ type: "image", largeur: 360, ...u.image }));
  s.append(ligneSources(u.sources));
  return s;
}

// Article : "article" (dans le fil), "chiffre" (encart, le chiffre en grand), "dossier" (replié derrière son image).
function article(a, id, cle, options, nom = a.etiquette) {
  if (a.format === "dossier") return dossier(a, id, cle, options, nom);
  const s = el("article", a.format === "chiffre" ? "rubrique chiffre" : "rubrique");
  s.id = id;
  if (a.format === "chiffre") {
    const e = el("div", "encart");
    e.append(el("p", "rubrique-nom", nom), el("h2", "titre chiffre-titre", a.titre), corps(a, cle, options));
    s.append(e);
    return s;
  }
  s.append(el("p", "rubrique-nom", nom), el("h2", "titre", a.titre));
  if (a.chapo) s.append(el("p", "chapo", a.chapo));
  s.append(corps(a, cle, options));
  return s;
}

function dossier(a, id, cle, options, nom) {
  const s = el("article", "rubrique dossier-bloc");
  s.id = id;
  const d = el("details", "dossier");
  const resume = el("summary");
  if (a.couverture) {
    const c = image(a.couverture, { zoom: false });
    c.className = a.couverture.type === "carte" || a.couverture.ville ? "couverture couverture-carte" : "couverture";
    c.alt = "";
    c.addEventListener("error", () => c.remove(), { once: true });
    resume.append(c);
  }
  const textes = el("div", "dossier-entete");
  textes.append(el("p", "rubrique-nom", nom), el("h2", "titre", a.titre));
  if (a.chapo) textes.append(el("p", "chapo", a.chapo));
  textes.append(el("p", "note ouvrir", T.lireDossier));
  resume.append(textes);
  const contenu = el("div", "dossier-corps");
  const l = a.couverture ? legende(a.couverture) : null;
  if (l) contenu.append(l);
  contenu.append(corps(a, cle, options));
  d.append(resume, contenu);
  d.addEventListener("toggle", () => {
    d.querySelector(".ouvrir").textContent = d.open ? T.replier : T.lireDossier;
  });
  s.append(d);
  return s;
}

// Quiz de fin de rubrique : un choix par question, réponse et explication aussitôt.
function quiz(questions, etat) {
  const s = el("section", "quiz encart");
  s.id = "quiz";
  s.append(el("h2", "titre", T.quiz));
  let reponses = etat.reponses.slice();
  const score = el("p", "note quiz-score");
  const zone = el("div");
  const majScore = () => {
    const faites = reponses.filter((r) => r >= 0).length;
    const justes = questions.filter((q, i) => reponses[i] === q.reponse).length;
    score.textContent = faites === questions.length ? T.sur(justes, questions.length) : "";
    refaire.hidden = faites !== questions.length;
  };
  const dessiner = () => {
    zone.replaceChildren(...questions.map((q, i) => {
      const bloc = el("div", "question");
      bloc.append(el("p", "texte question-texte", `${i + 1}. ${q.question}`));
      const liste = el("div", "choix");
      const suite = el("div", "reponse");
      const montrer = () => {
        const r = reponses[i];
        if (r < 0) return;
        [...liste.children].forEach((b, j) => {
          b.disabled = true;
          b.classList.toggle("juste", j === q.reponse);
          b.classList.toggle("faux", j === r && r !== q.reponse);
        });
        const verdict = el("p", "texte");
        verdict.append(el("strong", null, r === q.reponse ? T.exact : T.non));
        if (q.explication) verdict.append(" ", q.explication);
        suite.replaceChildren(verdict);
      };
      q.choix.forEach((c, j) => {
        const b = el("button", "choix-bouton", `${"ABCD"[j] ?? j + 1}. ${c}`);
        b.type = "button";
        b.addEventListener("click", () => {
          if (reponses[i] >= 0) return;
          reponses[i] = j;
          etat.enregistrer(reponses);
          montrer();
          majScore();
        });
        liste.append(b);
      });
      bloc.append(liste, suite);
      montrer();
      return bloc;
    }));
  };
  const refaire = el("button", "action-garder", T.recommencer);
  refaire.type = "button";
  refaire.addEventListener("click", () => {
    reponses = questions.map(() => -1);
    etat.recommencer();
    dessiner();
    majScore();
    s.scrollIntoView({ block: "start" });
  });
  dessiner();
  s.append(zone, score, refaire);
  majScore();
  return s;
}

function breves(liste) {
  const s = el("section", "breves");
  s.id = "breves";
  s.append(el("h2", "titre", T.enBref));
  const l = el("div", "breves-liste");
  for (const br of liste) {
    const d = el("div", "breve");
    d.append(el("h3", "rubrique-nom", br.rubrique));
    for (const item of br.items ?? []) d.append(el("p", "texte", `- ${item}`));
    d.append(ligneSources(br.sources));
    l.append(d);
  }
  s.append(l);
  return s;
}

// Affiche une rubrique de l'édition, ou les articles gardés (r = null).
// options : { garder: { etiqueter(bouton) }, gardes: [...], quiz: { reponses, enregistrer, recommencer }, cle(i) }
export function rendre(conteneur, r, options = {}) {
  const frag = document.createDocumentFragment();
  if (r) {
    if (r.une?.texte) frag.append(une(r.une));
    (r.articles ?? []).forEach((a, i) => frag.append(article(a, `a${i + 1}`, options.cle?.(i), options)));
    if (r.breves?.length) frag.append(breves(r.breves));
    if (r.quiz?.length && options.quiz) frag.append(quiz(r.quiz, options.quiz));
    if (!r.articles?.length) frag.append(el("p", "note vide", T.videRubrique));
  } else {
    const liste = options.gardes ?? [];
    if (!liste.length) frag.append(el("p", "note vide", T.aucunGarde));
    liste.forEach((g, i) => frag.append(article({ ...g.article, format: g.article.format === "chiffre" ? "chiffre" : "article" },
      `g${i + 1}`, g.cle, options, `${g.article.etiquette} · ${g.semaine_texte}`)));
  }
  frag.append(el("footer", "pied"));
  conteneur.replaceChildren(frag);
}

// Entrées du menu pour la rubrique affichée : { id, nom } dans l'ordre de lecture.
export function ancres(r) {
  if (!r) return [];
  return [
    ...(r.une?.texte ? [{ id: "une", nom: T.essentiel }] : []),
    ...(r.articles ?? []).map((a, i) => ({ id: `a${i + 1}`, nom: a.etiquette })),
    ...(r.breves?.length ? [{ id: "breves", nom: T.enBref }] : []),
    ...(r.quiz?.length ? [{ id: "quiz", nom: T.quiz }] : []),
  ];
}

export function message(conteneur, texte) {
  conteneur.replaceChildren(el("p", "note vide", texte));
}

// Agrandissement d'une image au toucher ou au clic (cartes, graphiques, schémas).
// Graphique Our World in Data en ligne : sa version interactive remplace l'image.
export function activerZoom(racine, dialogue) {
  const vue = dialogue.querySelector("img");
  const texte = dialogue.querySelector("p");
  const cadre = dialogue.querySelector("iframe");
  const ouvrir = (img) => {
    const url = img.dataset.interactif;
    const enLigne = url && navigator.onLine;
    dialogue.classList.toggle("interactif", Boolean(enLigne));
    cadre.src = enLigne ? url : "about:blank";
    vue.src = img.currentSrc || img.src;
    vue.alt = img.alt;
    texte.textContent = img.closest("figure")?.querySelector("figcaption")?.textContent ?? "";
    dialogue.showModal();
  };
  dialogue.addEventListener("close", () => { cadre.src = "about:blank"; });
  dialogue.querySelector(".fermer-zoom").addEventListener("click", (e) => {
    e.stopPropagation();
    dialogue.close();
  });
  racine.addEventListener("click", (e) => {
    const img = e.target.closest?.("img[data-zoom]");
    if (img) ouvrir(img);
  });
  racine.addEventListener("keydown", (e) => {
    if ((e.key === "Enter" || e.key === " ") && e.target.matches?.("img[data-zoom]")) {
      e.preventDefault();
      ouvrir(e.target);
    }
  });
  dialogue.addEventListener("click", () => { if (!dialogue.classList.contains("interactif")) dialogue.close(); });
}
