#!/usr/bin/env python3
"""Veille de la semaine : lit les flux de consignes/veille.txt et sort une liste compacte des articles des
7 derniers jours, groupés par rubrique, sans les sujets déjà traités. Remplace la plupart des recherches web.

Le réseau de la tâche planifiée ne laisse pas passer les sites de presse : la veille tourne donc dans
GitHub Actions (.github/workflows/veille.yml) avant la tâche, et sa sortie est publiée sur la branche `veille`
(veille.txt, liens.json). La tâche lit ces fichiers avec git ; `lien` les retrouve dans le dossier veille/.

Usage :
  python3 outils/veille.py                  7 derniers jours, 8 articles au plus par flux
  python3 outils/veille.py --rubrique Environnement --max 12
  python3 outils/veille.py lien 12 31 40    adresses des articles retenus (numéros de la dernière veille)
Sortie : "[n] titre · source · JJ/MM HHhMM". Les adresses restent dans _veille.json, pour ne pas
alourdir la lecture. Les flux en échec sont listés à la fin.
"""
import argparse
import concurrent.futures as cf
import datetime as dt
import email.utils
import html
import json
import os
import re
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RACINE, "outils"))
from historique import deja_traite, mots, sujets_recents  # noqa: E402

LIENS = os.path.join(RACINE, "_veille.json")
LIENS_BRANCHE = os.path.join(RACINE, "veille", "liens.json")
AGENT = "Mozilla/5.0 (compatible; HebdoIAVeille/1.0; +https://github.com/adrienrochestudio/hebdo-ia)"
PARIS = dt.timezone(dt.timedelta(hours=1))  # heure d'hiver ; l'affichage n'a pas besoin de plus


def sources(rubrique=None):
    for l in open(os.path.join(RACINE, "consignes", "veille.txt"), encoding="utf-8"):
        if l.strip() and not l.startswith("#"):
            rub, nom, url, *opt = [c.strip() for c in l.split("|")]
            if rubrique is None or rub.lower() == rubrique.lower():
                yield rub, nom, url, "ia" in opt


def lire_date(texte):
    if not texte:
        return None
    texte = texte.strip()
    try:
        d = email.utils.parsedate_to_datetime(texte)
    except (TypeError, ValueError):
        try:
            d = dt.datetime.fromisoformat(texte.replace("Z", "+00:00"))
        except ValueError:
            return None
    return d if d.tzinfo else d.replace(tzinfo=dt.timezone.utc)


def nettoyer_url(url):
    p = urllib.parse.urlsplit(url.strip())
    garder = [(k, v) for k, v in urllib.parse.parse_qsl(p.query) if not k.startswith(("utm_", "xtor", "at_"))]
    return urllib.parse.urlunsplit((p.scheme, p.netloc, p.path, urllib.parse.urlencode(garder), ""))


def articles(xml):
    """(titre, lien, date) pour RSS 2.0, RSS 1.0 (RDF) et Atom, sans dépendre des espaces de noms."""
    racine = ET.fromstring(xml)
    for el in racine.iter():
        tag = el.tag.rsplit("}", 1)[-1]
        if tag not in ("item", "entry"):
            continue
        champs = {}
        for c in el:
            nom = c.tag.rsplit("}", 1)[-1]
            if nom == "link" and c.get("href") and c.get("rel", "alternate") == "alternate":
                champs.setdefault("link", c.get("href"))
            elif c.text and nom not in champs:
                champs[nom] = c.text
        titre = html.unescape(re.sub(r"<[^>]+>", "", champs.get("title", ""))).strip()
        date = lire_date(champs.get("pubDate") or champs.get("published") or champs.get("updated") or champs.get("date"))
        if titre and champs.get("link"):
            yield titre, champs["link"], date


# Flux généralistes (option "ia") : seuls ces titres sont gardés.
SUJET_IA = re.compile(r"\b(ia|ai|a\.i\.|intelligence artificielle|artificial intelligence|machine learning|llms?|gpt|chatgpt|"
                      r"openai|anthropic|claude|gemini|mistral|deepseek|qwen|llama|copilot|nvidia|gpus?|puces?|chips?|"
                      r"semiconduct\w*|data ?cent(?:er|re)s?|centres? de données|datacenters?|tsmc|hbm|neural|neuronal|"
                      r"genai|générati\w+|generative|agents? ia|ai agents?|robot\w*|automati\w+|algorithm\w*|machine)\b", re.I)


def lire_flux(source):
    rub, nom, url, filtre = source
    try:
        req = urllib.request.Request(url, headers={"User-Agent": AGENT})
        with urllib.request.urlopen(req, timeout=15) as rep:
            brut = rep.read()
        try:
            arts = list(articles(brut))
        except ET.ParseError:  # flux mal formé (esperluettes nues) : on les échappe et on relit
            arts = list(articles(re.sub(rb"&(?!#?\w+;)", b"&amp;", brut)))
        if filtre:
            arts = [a for a in arts if SUJET_IA.search(a[0])]
        return source, arts, None
    except Exception as exc:  # réseau, statut, XML invalide : le flux est signalé, la veille continue
        return source, [], f"{exc.__class__.__name__}"


def main():
    if sys.argv[1:2] == ["lien"]:
        args = sys.argv[2:]
        fichier = LIENS_BRANCHE if os.path.isfile(LIENS_BRANCHE) else LIENS
        liens = json.load(open(fichier, encoding="utf-8"))
        for n in args:
            print(f"[{n}] {liens.get(n, 'numéro inconnu')}")
        return
    a = argparse.ArgumentParser()
    a.add_argument("--heures", type=int, default=168)
    a.add_argument("--max", type=int, default=8, help="articles au plus par flux")
    a.add_argument("--rubrique")
    a.add_argument("--liens", default=LIENS, help="fichier où écrire les adresses")
    x = a.parse_args()

    depuis = dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=x.heures)
    sujets = sujets_recents()
    vus = []
    liens = {}
    par_rubrique, echecs, ecartes = {}, [], 0
    with cf.ThreadPoolExecutor(12) as pool:
        resultats = list(pool.map(lire_flux, list(sources(x.rubrique))))
    for (rub, nom, _, _), arts, err in resultats:
        if err:
            echecs.append(f"{nom} ({err})")
            continue
        n = 0
        for titre, lien, date in sorted(arts, key=lambda t: t[2] or depuis, reverse=True):
            if n >= x.max or (date and date < depuis):
                continue
            m = mots(titre)
            if any(len(m & v) >= max(3, len(m) * 0.7) for v in vus):  # même info dans un autre flux
                continue
            if deja_traite(titre, sujets, seuil=0.6):
                ecartes += 1
                continue
            vus.append(m)
            quand = date.astimezone(PARIS).strftime("%d/%m %Hh%M") if date else "?"
            num = str(len(liens) + 1)
            liens[num] = nettoyer_url(lien)
            par_rubrique.setdefault(rub, []).append(f"[{num}] {titre[:140]} · {nom} · {quand}")
            n += 1
    json.dump(liens, open(x.liens, "w", encoding="utf-8"), ensure_ascii=False)
    print(f"Veille du {dt.datetime.now(PARIS).strftime('%d/%m/%Y %Hh%M')} (heure de Paris), {x.heures} dernières heures")
    for rub, lignes in par_rubrique.items():
        print(f"\n## {rub}")
        print("\n".join(lignes))
    print(f"\n{sum(map(len, par_rubrique.values()))} articles, {ecartes} écarté(s) car déjà traités"
          + (f" ; flux en échec : {', '.join(echecs)}" if echecs else ""))


if __name__ == "__main__":
    main()
