#!/usr/bin/env python3
"""Schémas et graphiques en barres de l'édition, dessinés en PNG au moment de la publication.

Une seule mise en forme pour l'iPhone, le Mac et le navigateur : l'app affiche une image, que l'on peut agrandir.
Typographie de l'app (Source Serif 4, coupes dans outils/polices), encre, gris de note, bordeaux.

Schéma (circuit, mécanisme, montage) :
{"type": "schema", "titre": "facultatif",
 "noeuds": [{"id": "a", "texte": "Banques chinoises", "detail": "facultatif, une ligne courte",
             "valeur": "facultatif, ex. 4,1 Md$", "accent": true}],
 "liens": [{"de": "a", "vers": "b", "texte": "prêt de 4,1 Md$"}],
 "legende": "..."}
Les nœuds sont placés par étages, du haut vers le bas, selon les liens (3 nœuds au plus par étage).
Un lien qui remonte (boucle) est dessiné en arc sur le côté.
Ancien format accepté : {"type": "schema", "etapes": [{"boite": "..."}, {"fleche": "..."}]}, converti en chaîne.

Graphique en barres (comparer 2 à 8 quantités) :
{"type": "barres", "titre": "...", "unite": "Md$", "items": [{"texte": "Chine", "valeur": 4.1, "accent": true}],
 "legende": "...", "credit": {...}}
"""
import os
import textwrap

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.font_manager import FontProperties  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch  # noqa: E402

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POLICES = os.path.join(RACINE, "outils", "polices")
ENCRE, NOTE, MARQUE, FILET, FOND_ACCENT = "#121212", "#666666", "#1d4257", "#c8c8c8", "#eaf1f5"
LARGEUR = 1100  # px ; affiché à la largeur de la colonne, agrandissable
MARGE = 40
ECART_H = 36
PAR_ETAGE = 3


def police(coupe, taille):
    return FontProperties(fname=os.path.join(POLICES, f"Hebdo{coupe}.ttf"), size=taille)


# Tailles en pixels de l'image (pt = px à 72 dpi). Sur un téléphone l'image est réduite d'environ 2,7 fois :
# 40 px de titre de nœud donnent environ 15 points à l'écran.
T_TITRE, T_NOEUD, T_DETAIL, T_VALEUR, T_LIEN = 44, 40, 33, 40, 33


def lignes(texte, taille, largeur_px):
    """Coupe un texte pour tenir dans largeur_px (approximation : 0,5 em par caractère)."""
    if not texte:
        return []
    par_ligne = max(8, int(largeur_px / (taille * 0.5)))
    return textwrap.wrap(texte, par_ligne, break_long_words=False, break_on_hyphens=False)


def depuis_etapes(b):
    noeuds, liens, precedent, fleche = [], [], None, None
    for i, e in enumerate(b.get("etapes", [])):
        if "boite" in e:
            parties = e["boite"].split("\n")
            n = {"id": f"n{i}", "texte": parties[0], "detail": " ".join(parties[1:])}
            noeuds.append(n)
            if precedent:
                liens.append({"de": precedent, "vers": n["id"], "texte": fleche or ""})
            precedent, fleche = n["id"], None
        else:
            fleche = e.get("fleche")
    return noeuds, liens


def etages(noeuds, liens):
    """Étage de chaque nœud : plus long chemin depuis une source, sans suivre les liens qui remontent."""
    ids = [n["id"] for n in noeuds]
    suivants = {i: [l["vers"] for l in liens if l["de"] == i and l["vers"] in ids] for i in ids}
    ordre, etat, retour = [], {}, set()

    def visiter(i):
        etat[i] = 1
        for j in suivants[i]:
            if etat.get(j) == 1:
                retour.add((i, j))
            elif j not in etat:
                visiter(j)
        etat[i] = 2
        ordre.append(i)

    for i in ids:
        if i not in etat:
            visiter(i)
    niveau = {i: 0 for i in ids}
    for i in reversed(ordre):
        for j in suivants[i]:
            if (i, j) not in retour:
                niveau[j] = max(niveau[j], niveau[i] + 1)
    # Plus de PAR_ETAGE nœuds sur un étage : on décale les suivants d'un étage.
    par = {}
    for i in ids:
        par.setdefault(niveau[i], []).append(i)
    final, decalage = {}, 0
    for n in sorted(par):
        groupe = par[n]
        for k in range(0, len(groupe), PAR_ETAGE):
            for i in groupe[k:k + PAR_ETAGE]:
                final[i] = n + decalage
            decalage += 1 if k + PAR_ETAGE < len(groupe) else 0
    return final, retour


def x_fleche(a, c):
    """Abscisses de départ et d'arrivée : verticale dès que les deux boîtes se recouvrent en largeur."""
    ca, cc = a["x"] + a["l"] / 2, c["x"] + c["l"] / 2
    if c["x"] + 30 <= ca <= c["x"] + c["l"] - 30:
        return ca, ca
    if a["x"] + 30 <= cc <= a["x"] + a["l"] - 30:
        return cc, cc
    return ca, cc


def schema(b, sortie):
    noeuds, liens = (b["noeuds"], b.get("liens", [])) if b.get("noeuds") else depuis_etapes(b)
    if not noeuds:
        raise ValueError("schéma sans nœud")
    niveau, retour = etages(noeuds, liens)
    rangs = {}
    for n in noeuds:
        rangs.setdefault(niveau[n["id"]], []).append(n)
    utile = LARGEUR - 2 * MARGE - (110 if retour else 0)
    titre = lignes(b.get("titre"), T_TITRE, LARGEUR - 2 * MARGE)

    # 1. Largeur et hauteur des boîtes, étage par étage.
    boites = {}
    for rang in sorted(rangs):
        groupe = rangs[rang]
        largeur = (utile - ECART_H * (len(groupe) - 1)) / len(groupe)
        x = MARGE
        mesures = []
        for n in groupe:
            interieur = largeur - 2 * 22
            t = lignes(n["texte"], T_NOEUD, interieur)
            v = lignes(n.get("valeur"), T_VALEUR, interieur)
            d = lignes(n.get("detail"), T_DETAIL, interieur)
            h = 28 + len(t) * T_NOEUD * 1.22 + len(v) * T_VALEUR * 1.22 + len(d) * T_DETAIL * 1.3 + 26
            mesures.append(dict(id=n["id"], x=x, l=largeur, h=h, t=t, v=v, d=d, accent=n.get("accent"), rang=rang))
            x += largeur + ECART_H
        haut = max(m["h"] for m in mesures)
        for m in mesures:
            m["h"] = haut
            boites[m["id"]] = m

    # 2. Flèches descendantes et libellés de chaque intervalle entre deux étages.
    fleches = []
    for l in liens:
        a, c = boites.get(l["de"]), boites.get(l["vers"])
        if a and c and (l["de"], l["vers"]) not in retour and c["rang"] > a["rang"]:
            x0, x1 = x_fleche(a, c)
            fleches.append(dict(l=l, a=a, c=c, x0=x0, x1=x1))
    hauteur_intervalle = {}
    for rang in sorted(rangs):
        dans = sorted([f for f in fleches if f["a"]["rang"] == rang], key=lambda f: max(f["x0"], f["x1"]))
        nb = 0
        for i, f in enumerate(dans):
            xg = max(f["x0"], f["x1"]) + 16
            xd = min([min(g["x0"], g["x1"]) - 20 for g in dans[i + 1:]] + [LARGEUR - MARGE])
            f["place"] = max(140, xd - xg)
            f["lignes"] = lignes(f["l"].get("texte"), T_LIEN, f["place"])
            nb = max(nb, len(f["lignes"]))
        hauteur_intervalle[rang] = max(100, 50 + nb * T_LIEN * 1.25)

    # 3. Ordonnées.
    y = MARGE + len(titre) * T_TITRE * 1.3 + (28 if titre else 0)
    for rang in sorted(rangs):
        for n in rangs[rang]:
            boites[n["id"]]["y"] = y
        y += boites[rangs[rang][0]["id"]]["h"] + hauteur_intervalle[rang]
    hauteur = y - hauteur_intervalle[max(rangs)] + MARGE

    fig = plt.figure(figsize=(LARGEUR / 72, hauteur / 72), dpi=72)
    ax = fig.add_axes((0, 0, 1, 1))
    ax.set_xlim(0, LARGEUR)
    ax.set_ylim(hauteur, 0)
    ax.axis("off")
    fig.patch.set_facecolor("white")

    yt = MARGE
    for l in titre:
        ax.text(MARGE, yt, l, fontproperties=police("Titre-Medium", T_TITRE), color=ENCRE, va="top")
        yt += T_TITRE * 1.3

    for bx in boites.values():
        ax.add_patch(FancyBboxPatch((bx["x"], bx["y"]), bx["l"], bx["h"], boxstyle="round,pad=0,rounding_size=10",
                                    linewidth=2.4 if bx["accent"] else 1.6,
                                    edgecolor=MARQUE if bx["accent"] else ENCRE,
                                    facecolor=FOND_ACCENT if bx["accent"] else "white"))
        contenu = len(bx["t"]) * T_NOEUD * 1.22 + len(bx["v"]) * T_VALEUR * 1.22 + len(bx["d"]) * T_DETAIL * 1.3
        cx, ty = bx["x"] + bx["l"] / 2, bx["y"] + (bx["h"] - contenu) / 2
        for l in bx["t"]:
            ax.text(cx, ty, l, fontproperties=police("Texte-Semibold", T_NOEUD), color=ENCRE, ha="center", va="top")
            ty += T_NOEUD * 1.22
        for l in bx["v"]:
            ax.text(cx, ty, l, fontproperties=police("Texte-Semibold", T_VALEUR), color=MARQUE, ha="center", va="top")
            ty += T_VALEUR * 1.22
        for l in bx["d"]:
            ax.text(cx, ty + 4, l, fontproperties=police("Texte-Regular", T_DETAIL), color=NOTE, ha="center", va="top")
            ty += T_DETAIL * 1.3

    for f in fleches:
        a, c = f["a"], f["c"]
        p0, p1 = (f["x0"], a["y"] + a["h"] + 4), (f["x1"], c["y"] - 4)
        ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle="-|>,head_length=10,head_width=5", color=ENCRE,
                                     linewidth=2.2, shrinkA=0, shrinkB=0, mutation_scale=2))
        if f["lignes"]:
            ax.text(max(p0[0], p1[0]) + 16, (p0[1] + p1[1]) / 2, "\n".join(f["lignes"]),
                    fontproperties=police("Texte-Italic", T_LIEN), color=ENCRE, ha="left", va="center", linespacing=1.15)

    # Liens qui remontent (boucle) ou restent au même étage : arc pointillé sur la droite.
    for l in liens:
        a, c = boites.get(l["de"]), boites.get(l["vers"])
        if not a or not c or any(f["l"] is l for f in fleches):
            continue
        x0, x1 = a["x"] + a["l"], c["x"] + c["l"]
        ax.add_patch(FancyArrowPatch((x0 + 4, a["y"] + a["h"] / 2), (x1 + 4, c["y"] + c["h"] / 2),
                                     connectionstyle="arc3,rad=0.45", arrowstyle="-|>,head_length=10,head_width=5",
                                     mutation_scale=2, color=NOTE, linewidth=1.8, linestyle=(0, (6, 5))))
        if l.get("texte"):
            ax.text(LARGEUR - MARGE + 10, (a["y"] + c["y"] + c["h"]) / 2, "\n".join(lignes(l["texte"], T_LIEN - 4, 100)),
                    fontproperties=police("Texte-Italic", T_LIEN - 4), color=NOTE, ha="right", va="center")
    fig.savefig(sortie, dpi=72, facecolor="white")
    plt.close(fig)


def nombre_fr(v, langue="fr"):
    """fr : 12 500 et 4,1 (espace insécable). pt : 12.500 et 4,1."""
    milliers = "." if langue == "pt" else "\u00a0"
    entier = f"{int(abs(v)):,}".replace(",", milliers)
    signe = "-" if v < 0 else ""
    if v == int(v):
        return signe + entier
    return signe + entier + "," + f"{abs(v):.1f}".split(".")[1]


def barres(b, sortie):
    items = b.get("items", [])
    if not 2 <= len(items) <= 12:
        raise ValueError("un graphique en barres compare de 2 à 12 quantités")
    unite = b.get("unite", "")
    maxi = max(abs(float(i["valeur"])) for i in items) or 1
    titre = lignes(b.get("titre"), T_TITRE, LARGEUR - 2 * MARGE)
    ligne_h = T_NOEUD * 1.25 + 46 + 26
    hauteur = MARGE + len(titre) * T_TITRE * 1.3 + (24 if titre else 0) + len(items) * ligne_h + MARGE - 26
    fig = plt.figure(figsize=(LARGEUR / 72, hauteur / 72), dpi=72)
    ax = fig.add_axes((0, 0, 1, 1))
    ax.set_xlim(0, LARGEUR)
    ax.set_ylim(hauteur, 0)
    ax.axis("off")
    fig.patch.set_facecolor("white")
    y = MARGE
    for l in titre:
        ax.text(MARGE, y, l, fontproperties=police("Titre-Medium", T_TITRE), color=ENCRE, va="top")
        y += T_TITRE * 1.3
    y += 24 if titre else 0
    # Valeurs négatives : axe du zéro placé selon l'étendue, barres vers la gauche, signe explicite.
    valeurs = [float(i["valeur"]) for i in items]
    negatif = min(valeurs) < 0
    utile = LARGEUR - 2 * MARGE - (420 if negatif else 230)
    etendue = (max(0, max(valeurs)) - min(0, min(valeurs))) or 1
    zero = MARGE + (160 if negatif else 0) + utile * (-min(0, min(valeurs)) / etendue)
    y0 = y
    for i, v in zip(items, valeurs):
        ax.text(MARGE, y, i["texte"], fontproperties=police("Texte-Regular", T_NOEUD), color=ENCRE, va="top")
        y += T_NOEUD * 1.25
        long = max(4, utile * abs(v) / etendue)
        couleur = MARQUE if i.get("accent") else "#9a9a9a"
        x = zero - long if v < 0 else zero
        ax.add_patch(plt.Rectangle((x, y), long, 40, facecolor=couleur, edgecolor="none"))
        nombre = nombre_fr(v, b.get("_langue", "fr")).replace("-", "\u2212")
        if negatif and v > 0:
            nombre = "+" + nombre
        etiquette = f"{nombre}\u00a0{unite}".strip() if unite not in ("%",) else f"{nombre}\u00a0%"
        if v < 0:
            ax.text(x - 14, y + 20, etiquette, fontproperties=police("Texte-Semibold", T_VALEUR),
                    color=MARQUE if i.get("accent") else ENCRE, va="center", ha="right")
        else:
            ax.text(x + long + 14, y + 20, etiquette, fontproperties=police("Texte-Semibold", T_VALEUR),
                    color=MARQUE if i.get("accent") else ENCRE, va="center")
        y += 46 + 26
    if negatif:
        ax.plot([zero, zero], [y0 + T_NOEUD * 1.25 - 8, y - 26 + 8], color=ENCRE, linewidth=1.6)
    fig.savefig(sortie, dpi=72, facecolor="white")
    plt.close(fig)


def dessiner(b, sortie):
    (barres if b["type"] == "barres" else schema)(b, sortie)


if __name__ == "__main__":
    import json
    import sys
    b = json.load(open(sys.argv[1], encoding="utf-8"))
    dessiner(b, sys.argv[2])
    print(sys.argv[2])
