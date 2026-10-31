#!/usr/bin/env python3
"""Résout et vérifie les images libres d'une édition. Tourne dans GitHub Actions (.github/workflows/images.yml)
après chaque publication, parce que le réseau de la tâche planifiée n'atteint pas Wikimedia Commons.

Dans edition.json, une image Wikimedia peut être donnée sans adresse :
  "commons": "File:Nom exact du fichier.jpg"     fichier repéré par la rédaction (WebSearch sur commons.wikimedia.org)
  "commons_recherche": "Iluvatar CoreX logo"     à défaut, requête : premier fichier image sous licence libre
Ce script remplit "url" (vignette 1100 px, 500 px pour un portrait ou un logo) et "credit" (auteur, licence),
vérifie que chaque image "url" répond (Wikimedia, Our World in Data), et retire celles qui n'existent pas.

Usage : python3 outils/images.py editions/AAAA-MM-JJ/edition.json [...]   (réécrit le fichier s'il a changé)
"""
import html
import json
import re
import sys
import time
import urllib.parse
import urllib.request

API = "https://commons.wikimedia.org/w/api.php"
AGENT = "HebdoIA/1.0 (https://github.com/adrienrochestudio/hebdo-ia; adrien.etks@gmail.com)"
LIBRES = re.compile(r"cc[- ]by|cc0|public domain|domaine public|pd-|gfdl|attribution|no restrictions", re.I)
FORMATS = (".jpg", ".jpeg", ".png", ".svg", ".webp", ".tif", ".tiff", ".gif")


def appel(params):
    url = API + "?" + urllib.parse.urlencode({**params, "format": "json"})
    req = urllib.request.Request(url, headers={"User-Agent": AGENT})
    for essai in range(3):
        try:
            with urllib.request.urlopen(req, timeout=20) as rep:
                return json.load(rep)
        except Exception:
            time.sleep(2 + 3 * essai)
    return {}


def texte(v):
    return html.unescape(re.sub(r"<[^>]+>", "", v or "")).strip()


def info(titre, largeur):
    """(url, credit) d'un fichier Commons sous licence libre, ou None."""
    d = appel({"action": "query", "prop": "imageinfo", "iiprop": "url|extmetadata", "iiurlwidth": largeur,
               "titles": titre, "redirects": 1})
    for page in d.get("query", {}).get("pages", {}).values():
        ii = (page.get("imageinfo") or [None])[0]
        if not ii:
            return None
        meta = ii.get("extmetadata", {})
        licence = texte(meta.get("LicenseShortName", {}).get("value"))
        if not LIBRES.search(licence):
            return None
        auteur = texte(meta.get("Artist", {}).get("value"))[:80] or "auteur inconnu"
        return (ii.get("thumburl") or ii.get("url")).split("?utm_")[0], {
            "titre": f"{auteur}, {licence}, Wikimedia Commons", "url": ii.get("descriptionurl")}
    return None


def chercher(requete, largeur):
    d = appel({"action": "query", "list": "search", "srsearch": requete, "srnamespace": 6, "srlimit": 8})
    for r in d.get("query", {}).get("search", []):
        if r["title"].lower().endswith(FORMATS):
            trouve = info(r["title"], largeur)
            if trouve:
                return trouve
    return None


def repond(url):
    req = urllib.request.Request(url, headers={"User-Agent": AGENT}, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=20) as rep:
            return rep.status == 200 and rep.headers.get("Content-Type", "").startswith("image/")
    except Exception:
        return False


def elements(ed):
    """(conteneur, clé, élément) pour chaque image : couvertures, blocs, éléments de duo, image de l'une."""
    for r in ed.get("rubriques", []):
        if (r.get("une") or {}).get("image"):
            yield r["une"], "image", r["une"]["image"]
        for a in r.get("articles", []):
            if a.get("couverture"):
                yield a, "couverture", a["couverture"]
            for b in a.get("blocs", []):
                if b.get("type") == "image":
                    yield a["blocs"], None, b
                elif b.get("type") == "duo":
                    for e in b.get("elements", []):
                        yield b["elements"], None, e


def traiter(chemin):
    ed = json.load(open(chemin, encoding="utf-8"))
    change, retires = False, []
    for conteneur, cle, el in list(elements(ed)):
        if el.get("type") == "carte" or "ville" in el:
            continue
        largeur = 500 if el.get("nature") in ("portrait", "logo") else 1100
        if el.get("commons") or el.get("commons_recherche"):
            titre = el.get("commons", "")
            if titre and not titre.startswith("File:"):
                titre = "File:" + titre
            trouve = (info(titre, largeur) if titre else None) or (
                chercher(el["commons_recherche"], largeur) if el.get("commons_recherche") else None)
            el.pop("commons", None)
            el.pop("commons_recherche", None)
            change = True
            if trouve:
                el["url"], el["credit"] = trouve[0], el.get("credit") or trouve[1]
        if el.get("url") and not el.get("src") and not repond(el["url"]):
            el.pop("url")
        if not el.get("url") and not el.get("src"):
            retires.append(el.get("legende", "")[:60])
            change = True
            if cle:
                conteneur.pop(cle, None)
            else:
                conteneur.remove(el)
    # Un duo réduit à un élément devient un bloc simple ; un duo vide disparaît.
    for r in ed.get("rubriques", []):
        for a in r.get("articles", []):
            nouveaux = []
            for b in a.get("blocs", []):
                if b.get("type") == "duo" and len(b.get("elements", [])) < 2:
                    if b.get("elements"):
                        e = b["elements"][0]
                        nouveaux.append({"type": e.get("type", "image"), **e})
                    change = True
                    continue
                nouveaux.append(b)
            a["blocs"] = nouveaux
    if change:
        json.dump(ed, open(chemin, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    print(f"{chemin} : {'modifié' if change else 'inchangé'}" + (f", retirées : {retires}" if retires else ""))


if __name__ == "__main__":
    for c in sys.argv[1:]:
        traiter(c)
