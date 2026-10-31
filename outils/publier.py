#!/usr/bin/env python3
"""Contrôle et publie une édition de Hebdo IA (branche main, servie par GitHub Pages).

Usage :
  python3 outils/publier.py edition.json              contrôle : erreurs, MANQUES, statistiques
  python3 outils/publier.py edition.json --texte      idem, et écrit edition.txt (pour l'audit sans-trace-ia)
  python3 outils/publier.py edition.json --pousser    contrôle, dessine schémas et cartes, publie
  --forcer : publie malgré des MANQUES (jamais malgré une ERREUR).

Publier écrit editions/AAAA-MM-JJ/ (edition.json + img/), met à jour editions/index.json,
puis commit et pousse ces seuls fichiers sur main. Le code de l'app n'est jamais touché.

Schéma de edition.json (textes en texte brut, jamais de HTML ni de markdown) :
{
  "date_texte": "Samedi 31 octobre 2026",
  "semaine_texte": "Semaine du 25 au 31 octobre 2026",
  "rubriques": [                                  trois, dans cet ordre : actualite, environnement, technique
    {"id": "actualite",
     "une": {"texte": "3 ou 4 lignes", "image": {facultative, comme un bloc image}, "sources": [{"titre": "...", "url": "..."}]},
     "articles": [
       {"format": "article" | "chiffre" | "dossier",
        "etiquette": "Fait de la semaine · Chine",   (voir consignes/hebdo.md)
        "titre": "...", "chapo": "facultatif, obligatoire pour un dossier",
        "couverture": {bloc image ou carte, obligatoire pour un dossier},
        "blocs": [
          {"type": "p", "texte": "..."},
          {"type": "sous_titre", "texte": "..."},
          {"type": "liste", "items": ["...", "..."]},
          {"type": "definitions", "items": [{"terme": "...", "definition": "..."}]},
          {"type": "image", "nature": "portrait|logo|donnees|photo|carte_lieu", "url": "https://...", "largeur": 1100,
           "legende": "...", "lien": "https://... (version interactive)", "credit": {"titre": "...", "url": "..."}},
          {"type": "duo", "elements": [{bloc image}, {bloc carte}]},
          {"type": "carte", "ville": "Abilene", "lat": 32.45, "lon": -99.73, "pays": "United States of America", "legende": "..."},
          {"type": "schema", "titre": "...", "noeuds": [...], "liens": [...], "legende": "..."}   (voir outils/schema.py)
          {"type": "barres", "titre": "...", "unite": "TWh", "items": [{"texte": "...", "valeur": 4.1, "accent": true}],
           "legende": "...", "credit": {...}}
        ],
        "a_retenir": "deux phrases",
        "sources": [{"titre": "nom court du média", "url": "https://..."}],
        "note_sources": "facultatif : calcul de la rédaction"}
     ],
     "breves": [{"rubrique": "Chine", "items": ["..."], "sources": [...]}],
     "quiz": [{"question": "...", "choix": ["...", "...", "..."], "reponse": 0, "explication": "..."}]
    }
  ]
}
Ajoutés par ce script : "date" (AAAA-MM-JJ), "numero", "publie", "nom" de chaque rubrique,
"src" des schémas, barres et cartes (dessinés ici dans img/). Les images "url" restent distantes :
l'app les télécharge sur l'appareil pour la lecture hors ligne.
"""
import argparse
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time

from PIL import Image

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RACINE, "outils"))
import locator  # noqa: E402
import schema as dessin  # noqa: E402

EDITIONS = os.path.join(RACINE, "editions")
RUBRIQUES = {"actualite": "Actualité", "environnement": "Environnement", "technique": "Technique"}
TYPES = {"p", "sous_titre", "liste", "definitions", "image", "duo", "carte", "schema", "barres"}
FORMATS = {"article", "chiffre", "dossier"}
MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août",
        "septembre", "octobre", "novembre", "décembre"]
MOTS_DOSSIER = 1200
QUESTIONS = 6
ILLUSTRES = 0.7
LIMITE_EDITION = 6 * 1024 * 1024
PARIS = dt.timezone(dt.timedelta(hours=1))

# Ce que chaque rubrique doit contenir (vérifié comme MANQUES). Étiquettes : début du champ "etiquette".
ATTENDU = {
    "actualite": {"une": True, "articles": 7, "etiquettes": ["Fait de la semaine", "Portrait", "Le chiffre", "Dossier"]},
    "environnement": {"une": True, "articles": 6, "etiquettes": ["Fait de la semaine", "Angle mort", "Le chiffre", "Dossier"]},
    "technique": {"une": False, "articles": 6, "etiquettes": ["Mécanisme", "Infrastructure", "Métier", "Outil", "Glossaire"]},
}


def erreur(msg):
    sys.exit(f"ERREUR : {msg}")


def date_iso(date_texte):
    m = re.fullmatch(r"\s*\w+\s+(\d{1,2})(?:er)?\s+(\w+)\s+(\d{4})\s*", date_texte.lower())
    if not m or m.group(2) not in MOIS:
        erreur(f"date_texte illisible : {date_texte!r} (attendu : 'Samedi 31 octobre 2026')")
    return dt.date(int(m.group(3)), MOIS.index(m.group(2)) + 1, int(m.group(1))).isoformat()


def slug(t):
    t = t.lower()
    for a, b in (("àâä", "a"), ("éèêë", "e"), ("îï", "i"), ("ôö", "o"), ("ùûü", "u"), ("ç", "c")):
        for c in a:
            t = t.replace(c, b)
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")


# Espaces insécables : un nombre ne se sépare jamais de son unité, ni un signe de ponctuation de son mot.
NBSP, NNBSP = " ", " "
UNITES = (r"h|min|s|%|‰|€|\$|£|¥|°C|°|km|km²|m|m²|m³|cm|mm|nm|kg|g|t|Mt|Gt|kt|Md|Mds|Md\$|Md€|M\$|M€|GW|MW|kW|GWh|"
          r"MWh|kWh|TWh|W|Wh|L|ha|Go|Mo|To|Po|ko|Gbit/s|To/s|Go/s|Tflops|Pflops|ans?|mois|jours?|heures?|minutes?|"
          r"secondes?|semaines?|milliards?|millions?|milliers|tonnes|litres|personnes|euros?|dollars?|paramètres|"
          r"jetons|tokens|puces|GPU|serveurs|salariés|employés")
TYPO = [
    (re.compile(r"(?<=\d) (?=\d{3}(?!\d))"), NBSP),
    (re.compile(r"(?<=\d) (?=(?:" + UNITES + r")(?![\w]))"), NBSP),
    (re.compile(r"(?<=\b[hH]) (?=\d)"), NBSP),
    (re.compile(r"(?<=\b\d) (?=(?:" + "|".join(MOIS) + r")\b)|(?<=\b\d\d) (?=(?:" + "|".join(MOIS) + r")\b)|(?<=1er) (?=(?:" + "|".join(MOIS) + r")\b)"), NBSP),
    (re.compile(r"\b(n°|p\.|M\.|Mme|Dr) (?=\S)"), r"\1" + NBSP),
    (re.compile(r" (?=[;!?])"), NNBSP),
    (re.compile(r" (?=:)"), NBSP),
    (re.compile(r"« "), "«" + NBSP),
    (re.compile(r" »"), NBSP + "»"),
]
CHAMPS_TEXTE = {"texte", "titre", "legende", "a_retenir", "chapo", "detail", "valeur", "note_sources", "items",
                "date_texte", "semaine_texte", "question", "choix", "explication", "terme", "definition"}


def typographie(ed):
    def corriger(t):
        # Jamais de tiret cadratin ni de demi-cadratin d'incise.
        t = t.replace(" — ", ", ").replace("—", ", ").replace(" – ", ", ")
        for motif, rempl in TYPO:
            t = motif.sub(rempl, t)
        return t

    def visiter(o, cle=None):
        if isinstance(o, dict):
            for k, v in o.items():
                if k in ("sources", "credit", "url", "lien", "src"):
                    continue
                if isinstance(v, str) and k in CHAMPS_TEXTE:
                    o[k] = corriger(v)
                else:
                    visiter(v, k)
        elif isinstance(o, list):
            for i, v in enumerate(o):
                if isinstance(v, str) and cle in CHAMPS_TEXTE:
                    o[i] = corriger(v)
                else:
                    visiter(v, cle)
    visiter(ed)


def blocs_images(a):
    """Blocs, éléments de duo et couverture d'un article qui portent une image ou une carte."""
    if a.get("couverture"):
        yield a["couverture"]
    for b in a.get("blocs", []):
        if b.get("type") in ("image", "carte"):
            yield b
        elif b.get("type") == "duo":
            yield from b.get("elements", [])


def visuels(a):
    return sum(1 for b in a.get("blocs", []) if b.get("type") in ("image", "carte", "duo", "schema", "barres")) \
        + (1 if a.get("couverture") else 0)


def mots_corps(a):
    textes = []
    for b in a.get("blocs", []):
        textes.append(b.get("texte", ""))
        for i in b.get("items", []) if b.get("type") in ("liste", "definitions") else []:
            textes.append(i if isinstance(i, str) else f"{i.get('terme', '')} {i.get('definition', '')}")
    return len(" ".join(textes).split())


def verifier(ed):
    """Erreurs bloquantes : structure illisible pour l'app."""
    for cle in ("date_texte", "semaine_texte", "rubriques"):
        if not ed.get(cle):
            erreur(f"champ manquant : {cle}")
    ids = [r.get("id") for r in ed["rubriques"]]
    if ids != list(RUBRIQUES):
        erreur(f"rubriques attendues dans cet ordre : {', '.join(RUBRIQUES)} (reçu : {ids})")
    for r in ed["rubriques"]:
        for a in r.get("articles", []):
            for cle in ("etiquette", "titre", "blocs"):
                if not a.get(cle):
                    erreur(f"article sans {cle} ({r['id']}) : {a.get('titre', a.get('etiquette'))}")
            if a.setdefault("format", "article") not in FORMATS:
                erreur(f"format inconnu : {a['format']} ({a['titre']})")
            for b in a["blocs"]:
                if b.get("type") not in TYPES:
                    erreur(f"type de bloc inconnu : {b.get('type')} ({a['titre']})")
                if b["type"] == "definitions" and not all(isinstance(i, dict) and i.get("terme") and i.get("definition")
                                                          for i in b.get("items", [])):
                    erreur(f"definitions : chaque item porte terme et definition ({a['titre']})")
        for q in r.get("quiz", []):
            if not q.get("question") or not isinstance(q.get("choix"), list) or not 2 <= len(q["choix"]) <= 4:
                erreur(f"question de quiz mal formée ({r['id']}) : {q.get('question', '')[:60]}")
            if not isinstance(q.get("reponse"), int) or not 0 <= q["reponse"] < len(q["choix"]):
                erreur(f"réponse hors des choix ({r['id']}) : {q['question'][:60]}")
    for url in re.findall(r'"(?:url|lien)":\s*"([^"]+)"', json.dumps(ed)):
        if not url.startswith("https://"):
            erreur(f"URL non https : {url}")


def controler(ed):
    """Ce qui manque au regard des consignes. Renvoie la liste des MANQUES et affiche les statistiques."""
    manques = []
    total_mots = 0
    for r in ed["rubriques"]:
        att = ATTENDU[r["id"]]
        nom = RUBRIQUES[r["id"]]
        arts = r.get("articles", [])
        if att["une"] and not (r.get("une") or {}).get("texte"):
            manques.append(f"{nom} : pas d'« une » (l'essentiel de la semaine)")
        if len(arts) < att["articles"]:
            manques.append(f"{nom} : {len(arts)} articles, {att['articles']} attendus")
        etiquettes = [a["etiquette"].lower() for a in arts]
        for e in att["etiquettes"]:
            if not any(x.startswith(e.lower()) for x in etiquettes):
                manques.append(f"{nom} : pas d'article « {e} »")
        if r["id"] == "actualite":
            grands = re.compile(r"\b(openai|anthropic|google|alphabet|meta|microsoft|chatgpt|claude|gemini)\b", re.I)
            faits = [a for a in arts if a["etiquette"].lower().startswith("fait de la semaine")]
            if sum(bool(grands.search(a["titre"])) for a in faits) > 1:
                manques.append("Actualité : plus d'un Fait de la semaine sur OpenAI, Anthropic, Google, Meta ou Microsoft")
            if not any(re.search(r"inde|golfe|afrique|amérique latine|asie|japon|corée|monde", a["etiquette"], re.I)
                       for a in faits):
                manques.append("Actualité : aucun Fait de la semaine hors États-Unis, Europe et Chine")
        if r["id"] == "technique" and sum(x.startswith("métier") for x in etiquettes) < 2:
            manques.append("Technique : deux articles « Métier » attendus")
        if r["id"] == "technique" and not any(b.get("type") == "schema" for a in arts for b in a["blocs"]):
            manques.append("Technique : aucun schéma (le Mécanisme en demande un)")
        illustrables = [a for a in arts if a["format"] != "chiffre" and not a["etiquette"].lower().startswith("glossaire")]
        illustres = [a for a in illustrables if visuels(a)]
        if illustrables and len(illustres) / len(illustrables) < ILLUSTRES:
            sans = ", ".join(a["etiquette"] for a in illustrables if not visuels(a))
            manques.append(f"{nom} : {len(illustres)}/{len(illustrables)} articles illustrés, 70 % attendus (sans : {sans})")
        externes = [el for a in arts for el in blocs_images(a) if el.get("url")] + ([r["une"]["image"]] if (r.get("une") or {}).get("image") else [])
        if len(externes) < 2:
            manques.append(f"{nom} : {len(externes)} image(s) Wikimedia ou Our World in Data, 2 au moins (les schémas, barres et mini-cartes ne comptent pas)")
        for a in arts:
            if a["etiquette"].lower().startswith("portrait") and not any(el.get("nature") in ("portrait", "logo") for el in blocs_images(a)):
                manques.append(f"{nom} : le Portrait n'a ni portrait ni logo")
            if a["format"] == "dossier" and a.get("couverture") and not a["couverture"].get("url"):
                manques.append(f"{nom} : couverture de dossier en mini-carte ; une photo ou un graphique attendu : {a['titre']}")
        for a in arts:
            m = mots_corps(a)
            total_mots += m
            if not a.get("sources"):
                manques.append(f"{nom} : article sans sources : {a['titre']}")
            if a["format"] == "dossier":
                if m < MOTS_DOSSIER:
                    manques.append(f"{nom} : dossier trop court ({m} mots, {MOTS_DOSSIER} au moins) : {a['titre']}")
                if not a.get("couverture"):
                    manques.append(f"{nom} : dossier sans couverture : {a['titre']}")
                if not a.get("chapo"):
                    manques.append(f"{nom} : dossier sans chapo : {a['titre']}")
            elif a["format"] == "article" and not a["etiquette"].lower().startswith("glossaire") and m < 200:
                manques.append(f"{nom} : article trop court ({m} mots, 200 au moins) : {a['titre']}")
        q = r.get("quiz", [])
        if len(q) != QUESTIONS:
            manques.append(f"{nom} : quiz de {len(q)} questions, {QUESTIONS} attendues")
        if any(not x.get("explication") for x in q):
            manques.append(f"{nom} : question de quiz sans explication")
        reps = [x["reponse"] for x in q]
        if len(q) >= 4 and len(set(reps)) == 1:
            manques.append(f"{nom} : toutes les bonnes réponses sont à la même position")
        print(f"  {nom} : {len(arts)} articles, {sum(mots_corps(a) for a in arts)} mots, "
              f"{len(illustres)}/{len(illustrables)} illustrés, {len(r.get('breves', []))} groupes de brèves, {len(q)} questions")
    print(f"  Total : {total_mots} mots hors brèves")
    for m in manques:
        print(f"MANQUE : {m}")
    return manques


def texte(ed, chemin):
    """Texte brut de l'édition, pour l'audit sans-trace-ia."""
    out = []
    for r in ed["rubriques"]:
        if (r.get("une") or {}).get("texte"):
            out.append(r["une"]["texte"])
        for a in r.get("articles", []):
            out += [a["titre"], a.get("chapo", "")]
            for b in a["blocs"]:
                out.append(b.get("texte", ""))
                for i in b.get("items", []) if b.get("type") in ("liste", "definitions") else []:
                    out.append(i if isinstance(i, str) else f"{i['terme']} : {i['definition']}")
                out.append(b.get("legende", ""))
            out.append(a.get("a_retenir", ""))
        for br in r.get("breves", []):
            out += br.get("items", [])
        for q in r.get("quiz", []):
            out += [q["question"], q.get("explication", "")]
    open(chemin, "w", encoding="utf-8").write("\n\n".join(t for t in out if t))
    print(f"Texte écrit : {chemin}")


def compresser(png):
    im = Image.open(png).convert("RGB").quantize(colors=48, method=Image.Quantize.MEDIANCUT)
    im.save(png, optimize=True)


def dessiner(ed, dossier):
    """Schémas, barres et mini-cartes dessinés dans dossier/img ; "src" relatif à la racine du site."""
    rel = f"editions/{ed['date']}/img"
    img = os.path.join(dossier, "img")
    os.makedirs(img, exist_ok=True)
    for r in ed["rubriques"]:
        for a in r.get("articles", []):
            for b in a["blocs"]:
                if b["type"] in ("schema", "barres"):
                    b.pop("src", None)
                    cle = hashlib.sha1(json.dumps(b, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:10]
                    nom = f"sch-{cle}.png"
                    try:
                        dessin.dessiner({**b, "_langue": "fr"}, os.path.join(img, nom))
                    except Exception as exc:
                        erreur(f"{b['type']} illisible ({exc}) dans « {a['titre']} »")
                    compresser(os.path.join(img, nom))
                    b["src"] = f"{rel}/{nom}"
            for el in blocs_images(a):
                if el.get("type") == "carte" or ("ville" in el and "lat" in el):
                    nom = f"loc-{slug(el['ville'])}.png"
                    cible = os.path.join(img, nom)
                    if not os.path.exists(cible):
                        locator.carte(el["ville"], float(el["lat"]), float(el["lon"]), cible, nom_pays=el.get("pays"))
                        compresser(cible)
                    el["type"] = el.get("type") or "carte"
                    el["src"] = f"{rel}/{nom}"
                elif not el.get("url"):
                    erreur(f"image sans url : {el.get('legende', '')[:60]} (« {a['titre']} »)")
        u = (r.get("une") or {}).get("image")
        if u and not u.get("url"):
            erreur(f"image de l'une sans url ({r['id']})")


def git(*args, verifier_code=True):
    r = subprocess.run(["git", *args], cwd=RACINE, capture_output=True, text=True)
    if verifier_code and r.returncode != 0:
        erreur(f"git {' '.join(args)} : {r.stderr.strip() or r.stdout.strip()}")
    return r


def index_editions():
    f = os.path.join(EDITIONS, "index.json")
    return json.load(open(f, encoding="utf-8")) if os.path.isfile(f) else []


def publier(ed):
    git("pull", "-q", "--rebase", "origin", "main")
    liste = [e for e in index_editions() if e["date"] != ed["date"]]
    anterieures = [e for e in liste if e["date"] < ed["date"]]
    ed["numero"] = max([e["numero"] for e in anterieures], default=0) + 1
    ed["publie"] = dt.datetime.now(PARIS).isoformat(timespec="minutes")
    for r in ed["rubriques"]:
        r["nom"] = RUBRIQUES[r["id"]]
    dossier = os.path.join(EDITIONS, ed["date"])
    shutil.rmtree(dossier, ignore_errors=True)  # relance du jour : l'édition est remplacée entière
    os.makedirs(dossier)
    dessiner(ed, dossier)
    brut = json.dumps(ed, ensure_ascii=False, separators=(",", ":"))
    open(os.path.join(dossier, "edition.json"), "w", encoding="utf-8").write(brut)
    taille = sum(os.path.getsize(os.path.join(d, f)) for d, _, fs in os.walk(dossier) for f in fs)
    if taille > LIMITE_EDITION:
        erreur(f"édition trop lourde : {taille // 1024} Ko (limite {LIMITE_EDITION // 1024} Ko)")
    liste.append({"date": ed["date"], "numero": ed["numero"], "semaine_texte": ed["semaine_texte"],
                  "titres": {r["id"]: (r.get("articles") or [{}])[0].get("titre", "") for r in ed["rubriques"]}})
    liste.sort(key=lambda e: e["date"], reverse=True)
    json.dump(liste, open(os.path.join(EDITIONS, "index.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    git("add", "--", "editions")
    git("-c", "user.name=Hebdo IA", "-c", "user.email=adrien.etks@gmail.com",
        "commit", "-q", "-m", f"Édition n° {ed['numero']} du {ed['date']}", "--", "editions")
    for essai in range(3):
        r = git("push", "-q", "origin", "HEAD:main", verifier_code=False)
        if r.returncode == 0:
            print(f"Publié : n° {ed['numero']} du {ed['date']} ({taille // 1024} Ko). "
                  f"En ligne sur https://adrienrochestudio.github.io/hebdo-ia/ d'ici deux minutes.")
            return
        print(f"  envoi refusé ({r.stderr.strip()[:120]}), nouvel essai")
        git("pull", "-q", "--rebase", "origin", "main")
        time.sleep(3)
    erreur("envoi sur main impossible après trois essais")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("json")
    p.add_argument("--texte", action="store_true")
    p.add_argument("--pousser", action="store_true")
    p.add_argument("--forcer", action="store_true")
    x = p.parse_args()
    ed = json.load(open(x.json, encoding="utf-8"))
    verifier(ed)
    ed["date"] = date_iso(ed["date_texte"])
    typographie(ed)
    print(f"Édition du {ed['date']} ({ed['semaine_texte']})")
    manques = controler(ed)
    if x.texte:
        texte(ed, os.path.splitext(x.json)[0] + ".txt")
    if x.pousser:
        if manques and not x.forcer:
            erreur(f"{len(manques)} MANQUE(S) : compléter, ou --forcer en dernier recours")
        publier(ed)
    elif not manques:
        print("Aucun manque.")


if __name__ == "__main__":
    main()
