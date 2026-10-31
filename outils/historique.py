#!/usr/bin/env python3
"""Mémoire de la rédaction, lue dans les éditions publiées (editions/*/edition.json) : rien d'autre à tenir à jour.

Usage :
  python3 outils/historique.py etat            dernière édition et décision pour l'exécution du jour
                                               (code 0 : produire ; code 3 : édition de la semaine déjà en ligne)
  python3 outils/historique.py notions         sujets, métiers, mécanismes et outils des 12 dernières éditions
  python3 outils/historique.py verifier e.json sujets de e.json trop proches d'un sujet déjà traité
"""
import datetime as dt
import glob
import json
import os
import re
import sys
import unicodedata

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EDITIONS = os.path.join(RACINE, "editions")
PARIS = dt.timezone(dt.timedelta(hours=1))
JOURS_ENTRE_EDITIONS = 6  # une édition plus récente que ça : la semaine est déjà couverte

VIDES = set("""avec dans pour sans sous entre leur leurs mais plus moins comme apres avant depuis contre
vers chez dont elle elles ils sont etre avoir fait faire cette celle ceux tout tous toute toutes
the and for with from that this into over under after their about quand quoi comment pourquoi""".split())


def aujourdhui():
    return dt.datetime.now(PARIS).date().isoformat()


def mots(texte):
    """Mots significatifs d'un texte, sans accents ni majuscules."""
    t = unicodedata.normalize("NFD", (texte or "").lower())
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return {m for m in re.findall(r"[a-z0-9]{4,}", t) if m not in VIDES}


def editions(nombre=None, sauf_aujourdhui=True):
    """Éditions publiées, de la plus récente à la plus ancienne. Une relance du jour ignore l'édition du jour."""
    out = []
    for f in sorted(glob.glob(os.path.join(EDITIONS, "*", "edition.json")), reverse=True):
        date = os.path.basename(os.path.dirname(f))
        if sauf_aujourdhui and date == aujourdhui():
            continue
        try:
            out.append(json.load(open(f, encoding="utf-8")))
        except (OSError, ValueError):
            continue
    return out[:nombre] if nombre else out


def sujets_recents(nombre=12):
    """(rubrique, titre, mots) pour les articles des dernières éditions."""
    out = []
    for ed in editions(nombre):
        for r in ed.get("rubriques", []):
            for a in r.get("articles", []):
                out.append((f"{r['id']} · {a.get('etiquette', '')}", a.get("titre", ""),
                            mots(a.get("titre", "") + " " + (a.get("chapo") or ""))))
    return out


def deja_traite(texte, sujets=None, seuil=0.5):
    """Sujet récent le plus proche si le recouvrement de mots dépasse le seuil, sinon None."""
    m = mots(texte)
    if len(m) < 2:
        return None
    meilleur = None
    for rub, sujet, ms in sujets if sujets is not None else sujets_recents():
        if not ms:
            continue
        r = len(m & ms) / min(len(m), len(ms))
        if r >= seuil and (meilleur is None or r > meilleur[0]):
            meilleur = (r, rub, sujet)
    return meilleur


def etat():
    tout = editions(sauf_aujourdhui=False)
    if not tout:
        print("Aucune édition publiée : produire le n° 1.")
        return 0
    der = tout[0]
    jours = (dt.date.fromisoformat(aujourdhui()) - dt.date.fromisoformat(der["date"])).days
    print(f"Dernière édition : n° {der.get('numero')} du {der['date']} ({der.get('semaine_texte')}), il y a {jours} jour(s).")
    if jours == 0:
        print("Relance du jour : refaire l'édition et la remplacer (même numéro).")
        return 0
    if jours < JOURS_ENTRE_EDITIONS:
        print("La semaine est déjà couverte : ne rien produire.")
        return 3
    print(f"Produire le n° {der.get('numero', 0) + 1}.")
    return 0


def notions():
    eds = editions(12)
    if not eds:
        print("Aucune édition précédente.")
        return
    print("Sujets des 12 dernières éditions (ne pas refaire ; un suivi est possible s'il y a un fait nouveau) :")
    metiers, mecanismes, voix = [], [], []
    for ed in eds:
        print(f"\n## n° {ed.get('numero')} · {ed.get('date')}")
        for r in ed.get("rubriques", []):
            for a in r.get("articles", []):
                et = a.get("etiquette", "")
                print(f"- {r['id']} · {et} · {a.get('titre', '')}")
                if et.lower().startswith("métier"):
                    metiers.append(f"{et.split('·', 1)[-1].strip()} ({ed.get('date')})")
                if et.lower().startswith("la voix"):
                    voix.append(f"{et.split('·', 1)[-1].strip()} ({ed.get('date')})")
                if et.lower().startswith(("mécanisme", "outil")):
                    mecanismes.append(f"{et} : {a.get('titre', '')}")
    if metiers:
        print("\nMétiers déjà traités, du plus récent au plus ancien : " + " ; ".join(metiers))
    if voix:
        print("Voix de la semaine déjà publiées (pas deux fois en 10 éditions) : " + " ; ".join(voix))
    if mecanismes:
        print("Mécanismes et outils déjà expliqués : " + " ; ".join(mecanismes))


def verifier(chemin):
    ed = json.load(open(chemin, encoding="utf-8"))
    sujets = sujets_recents()
    alertes = 0
    for r in ed.get("rubriques", []):
        for a in r.get("articles", []):
            if a.get("format") == "chiffre" or a.get("etiquette", "").lower().startswith("glossaire"):
                continue
            proche = deja_traite(a.get("titre", "") + " " + (a.get("chapo") or ""), sujets, seuil=0.6)
            if proche:
                alertes += 1
                print(f"PROCHE : « {a['titre']} » ({r['id']}) ressemble à « {proche[2]} » ({proche[1]}) : "
                      "changer de sujet, ou apporter un fait nouveau et le dire dans le titre.")
    print(f"{alertes} sujet(s) trop proche(s)." if alertes else "Aucun sujet déjà traité.")


if __name__ == "__main__":
    cmd = sys.argv[1:2]
    if cmd == ["etat"]:
        sys.exit(etat())
    elif cmd == ["notions"]:
        notions()
    elif cmd == ["verifier"] and len(sys.argv) == 3:
        verifier(sys.argv[2])
    else:
        sys.exit(__doc__)
