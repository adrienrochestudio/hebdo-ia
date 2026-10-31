import { index, charger, enregistrer } from "./edition.js";
import { rendre, message, activerZoom, ancres } from "./rendu.js";
import { RUBRIQUES, T } from "./textes.js";
import * as suivi from "./suivi.js";

const journal = document.getElementById("journal");
const ligneDate = document.getElementById("date");
const bandeauArchive = document.getElementById("archive");
const boutonsVue = [...document.querySelectorAll(".onglets [data-vue]")];
const RELECTURE_MIN_MS = 30 * 60 * 1000;
const IDS = RUBRIQUES.map((r) => r.id);

let liste = [];          // index des éditions
let edition = null;      // édition affichée
let choisie = null;      // date d'une édition passée choisie dans le menu ; null = la dernière
let derniereVerif = 0;
let vue = "actualite";
try {
  const v = localStorage.getItem("vue");
  if (IDS.includes(v) || v === "gardes") vue = v;
} catch {}

const installee = matchMedia("(display-mode: standalone)").matches || navigator.standalone === true;
const rubrique = () => edition?.rubriques?.find((r) => r.id === vue) ?? null;
const derniere = () => liste[0]?.date ?? null;

// Un article est lu quand sa fin (sources, dernière brève, score du quiz) est passée à l'écran.
let lecture = null;
const observateur = "IntersectionObserver" in window ? new IntersectionObserver((entrees) => {
  for (const e of entrees) {
    if ((e.isIntersecting || e.boundingClientRect.bottom < 0) && lecture?.marquer(e.target.dataset.fin)) {
      observateur.unobserve(e.target);
      marquerOnglets();
    }
  }
}, { rootMargin: "0px 0px -10% 0px" }) : null;

function suivreLecture() {
  observateur?.disconnect();
  const r = rubrique();
  if (!r || !edition?.date || !observateur) return;
  lecture = suivi.lus(edition.date, r.id);
  for (const { id } of ancres(r)) {
    const bloc = document.getElementById(id);
    const fin = bloc?.querySelector(".dossier-corps")?.lastElementChild ?? bloc?.lastElementChild;
    if (!fin || lecture.ids.has(id)) continue;
    fin.dataset.fin = id;
    observateur.observe(fin);
  }
}

// Onglet d'une rubrique entièrement lue : texte gris.
function marquerOnglets() {
  const lues = edition?.date
    ? suivi.rubriquesLues(edition.date, Object.fromEntries((edition.rubriques ?? []).map((r) => [r.id, ancres(r).map((a) => a.id)])))
    : new Set();
  for (const b of boutonsVue) b.classList.toggle("lu", lues.has(b.dataset.vue));
}

const etiqueterGarde = (b) => {
  b.textContent = suivi.estGarde(b.dataset.garder) ? `${T.garde} · ${T.retirer}` : T.garder;
};

function dessiner() {
  for (const b of boutonsVue) b.setAttribute("aria-pressed", String(b.dataset.vue === vue));
  if (vue === "gardes") {
    ligneDate.textContent = T.articlesGardes;
    bandeauArchive.hidden = true;
    rendre(journal, null, { garder: { etiqueter: etiqueterGarde }, gardes: suivi.gardes() });
    observateur?.disconnect();
    return;
  }
  ligneDate.textContent = edition ? `${edition.semaine_texte} · ${T.numero(edition.numero)}` : "";
  const ancienne = edition && edition.date !== derniere();
  bandeauArchive.hidden = !ancienne;
  if (ancienne) {
    const retour = Object.assign(document.createElement("button"), { type: "button", textContent: T.derniere });
    retour.addEventListener("click", () => ouvrirEdition(null));
    bandeauArchive.replaceChildren(`${T.archive} `, retour);
  }
  const r = rubrique();
  rendre(journal, r, {
    garder: { etiqueter: etiqueterGarde },
    cle: (i) => (edition?.date ? `${edition.date}|${vue}|a${i + 1}` : null),
    quiz: r?.quiz?.length && edition?.date ? suivi.reponsesQuiz(edition, r.id, r.quiz) : null,
  });
  suivreLecture();
  marquerOnglets();
  document.title = "Hebdo IA";
}

// Garder ou retirer un article (lien en fin d'article).
journal.addEventListener("click", async (e) => {
  const b = e.target.closest?.("button[data-garder]");
  if (!b) return;
  const cle = b.dataset.garder;
  if (suivi.estGarde(cle)) {
    await suivi.retirer(cle);
    if (vue === "gardes") return dessiner();
  } else {
    const [date, rub, id] = cle.split("|");
    if (date !== edition?.date) return;
    const article = edition.rubriques.find((r) => r.id === rub)?.articles?.[Number(id.slice(1)) - 1];
    if (!article) return;
    await suivi.garder(cle, edition, article);
  }
  etiqueterGarde(b);
});

function changerVue(v) {
  if (v === vue) return;
  vue = v;
  try { localStorage.setItem("vue", vue); } catch {}
  dessiner();
  scrollTo(0, 0);
}

for (const b of boutonsVue) b.addEventListener("click", () => changerVue(b.dataset.vue));

// Charge l'index puis l'édition voulue. silencieux : ne redessine que si l'édition a changé.
// Renvoie true si l'affichage a changé.
async function afficher({ silencieux = false } = {}) {
  derniereVerif = Date.now();
  const idx = await index();
  if (idx?.liste.length) liste = idx.liste;
  const date = choisie ?? derniere();
  if (!date) {
    if (!edition) message(journal, T.rien);
    return false;
  }
  if (silencieux && edition?.date === date) return false;
  const ed = await charger(date);
  if (!ed) {
    if (!edition) message(journal, choisie ? T.horsLigne : T.rien);
    return false;
  }
  const nouvelle = edition && edition.date !== ed.donnees.date;
  edition = ed.donnees;
  dessiner();
  if (nouvelle) scrollTo(0, 0);
  if (ed.source === "reseau") {
    const manquees = await enregistrer(edition, [derniere(), edition.date].filter(Boolean));
    if (manquees) console.info(`${manquees} image(s) non enregistrée(s) pour la lecture hors ligne`);
  }
  return true;
}

async function ouvrirEdition(date) {
  choisie = date && date !== derniere() ? date : null;
  if (vue === "gardes") vue = IDS[0];
  message(journal, T.chargement);
  const change = await afficher();
  if (!change) dessiner();
  scrollTo(0, 0);
}

// Menu latéral : articles de la rubrique, éditions, articles gardés, scores des quiz.
const menu = document.getElementById("menu");
const listeRubriques = document.getElementById("menu-rubriques");
const titreRubriques = document.getElementById("menu-rubriques-titre");
const listeEditions = document.getElementById("menu-editions");
const listeGardes = document.getElementById("menu-gardes");
const titreGardes = document.getElementById("menu-gardes-titre");
const listeScores = document.getElementById("menu-scores");
const titreScores = document.getElementById("menu-scores-titre");

function bouton(texte, actif, action, lu = false) {
  const li = document.createElement("li");
  const b = Object.assign(document.createElement("button"), { type: "button", textContent: texte });
  if (actif) b.setAttribute("aria-current", "true");
  if (lu) b.classList.add("lu");
  b.addEventListener("click", action);
  li.append(b);
  return li;
}

// Article en cours de lecture : le dernier dont le haut est passé sous le premier quart de l'écran.
function courant(entrees) {
  let id = entrees[0]?.id;
  for (const e of entrees) {
    const n = document.getElementById(e.id);
    if (n && n.getBoundingClientRect().top < innerHeight / 4) id = e.id;
  }
  return id;
}

const nomRubrique = (id) => RUBRIQUES.find((r) => r.id === id)?.nom ?? id;

function remplirMenu() {
  const entrees = vue === "gardes" ? [] : ancres(rubrique());
  const ici = courant(entrees);
  const lues = lecture && vue !== "gardes" ? lecture.ids : new Set();
  titreRubriques.hidden = !entrees.length;
  titreRubriques.textContent = vue === "gardes" ? "" : nomRubrique(vue);
  listeRubriques.replaceChildren(...entrees.map(({ id, nom }) => bouton(nom, id === ici, () => {
    menu.close();
    document.getElementById(id)?.scrollIntoView({ block: "start" });
  }, lues.has(id))));

  listeEditions.replaceChildren(...liste.map((e) => bouton(`${T.numero(e.numero)} · ${e.semaine_texte}`,
    vue !== "gardes" && e.date === edition?.date, () => {
      menu.close();
      ouvrirEdition(e.date);
    })));

  const gardes = suivi.gardes();
  titreGardes.hidden = !gardes.length;
  listeGardes.replaceChildren(...gardes.map((g, i) => bouton(g.article.titre, false, () => {
    menu.close();
    changerVue("gardes");
    document.getElementById(`g${i + 1}`)?.scrollIntoView({ block: "start" });
  })));

  const sc = suivi.scores().slice(0, 12);
  titreScores.hidden = !sc.length;
  listeScores.replaceChildren(...sc.map((s) => {
    const li = document.createElement("li");
    li.className = "note";
    li.textContent = `${s.semaine_texte} · ${nomRubrique(s.rubrique)} · ${T.sur(s.justes, s.total)}`;
    return li;
  }));
}

document.getElementById("ouvrir-menu").addEventListener("click", () => {
  remplirMenu();
  menu.showModal();
});
menu.querySelector(".fermer-menu").addEventListener("click", () => menu.close());
menu.addEventListener("click", (e) => { if (e.target === menu) menu.close(); });

// Tirer vers le bas en haut de page pour actualiser (téléphone).
const tirer = document.getElementById("tirer");
const tirerTexte = tirer.querySelector("p");
const SEUIL = 72;
let depart = null;
let distance = 0;
let actualisation = false;

function poserTirage(d) {
  document.documentElement.style.setProperty("--decalage", `${d}px`);
  tirer.classList.toggle("visible", d > 24 || actualisation);
}

addEventListener("touchstart", (e) => {
  if (actualisation || scrollY > 0 || menu.open || e.touches.length !== 1) return;
  depart = e.touches[0].clientY;
  distance = 0;
}, { passive: true });

addEventListener("touchmove", (e) => {
  if (depart == null) return;
  const brut = e.touches[0].clientY - depart;
  if (brut <= 0 || scrollY > 0) { distance = 0; poserTirage(0); return; }
  distance = Math.min(120, brut * 0.5);
  document.documentElement.classList.add("glisse");
  tirerTexte.textContent = distance >= SEUIL ? T.relacher : T.tirer;
  poserTirage(distance);
}, { passive: true });

addEventListener("touchend", async () => {
  if (depart == null) return;
  depart = null;
  document.documentElement.classList.remove("glisse");
  if (distance < SEUIL) { poserTirage(0); return; }
  actualisation = true;
  tirer.classList.add("tourne");
  tirerTexte.textContent = T.actualisation;
  poserTirage(SEUIL);
  const debut = Date.now();
  const change = await afficher({ silencieux: true });
  if (!change) tirerTexte.textContent = T.aJour;
  await new Promise((r) => setTimeout(r, Math.max(0, 700 - (Date.now() - debut))));
  actualisation = false;
  tirer.classList.remove("tourne");
  poserTirage(0);
});

// Bouton du menu : caché quand on descend dans la lecture, visible dès qu'on remonte.
const boutonMenu = document.getElementById("ouvrir-menu");
let dernierY = scrollY;
addEventListener("scroll", () => {
  const y = scrollY;
  if (Math.abs(y - dernierY) < 6) return;
  boutonMenu.classList.toggle("cache", y > 80 && y > dernierY);
  dernierY = y;
}, { passive: true });

// Retour au premier plan : chercher une nouvelle édition.
document.addEventListener("visibilitychange", () => {
  if (document.visibilityState === "visible" && !choisie && Date.now() - derniereVerif > RELECTURE_MIN_MS) {
    afficher({ silencieux: true });
  }
});

activerZoom(journal, document.getElementById("zoom"));

// Mise à jour de l'app elle-même (nouveau service worker).
if ("serviceWorker" in navigator) {
  navigator.serviceWorker.register("./sw.js").then((reg) => {
    const proposer = (sw) => {
      document.getElementById("maj").hidden = false;
      document.getElementById("maj-bouton").onclick = () => sw.postMessage("activer");
    };
    if (reg.waiting && navigator.serviceWorker.controller) proposer(reg.waiting);
    reg.addEventListener("updatefound", () => {
      const nouveau = reg.installing;
      nouveau?.addEventListener("statechange", () => {
        if (nouveau.state === "installed" && navigator.serviceWorker.controller) proposer(nouveau);
      });
    });
  }).catch(() => {});
  let recharge = false;
  navigator.serviceWorker.addEventListener("controllerchange", () => {
    if (!recharge) { recharge = true; location.reload(); }
  });
}

if (installee) navigator.storage?.persist?.();

afficher();
