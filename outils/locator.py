"""Mini-cartes de localisation pour la newsletter Actualités.

Usage : python3 locator.py "Nom affiché" LAT LON sortie.png [--pays "United States of America"] [--zoom 1.0]

Fond : frontières Natural Earth 1:50m (geo/pays.geojson).
Style : terres gris clair, pays de la ville un peu plus foncé, point noir, nom en serif.
"""
import argparse
import json
import math
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon

ICI = os.path.dirname(os.path.abspath(__file__))
GEO = os.path.join(os.path.dirname(ICI), "geo", "pays.geojson")

TERRE = "#e4e4e4"
PAYS_CIBLE = "#c4c4c4"
FRONTIERE = "#ffffff"
MER = "#ffffff"
ENCRE = "#121212"


def anneaux(geometrie):
    if geometrie["type"] == "Polygon":
        yield geometrie["coordinates"][0]
    elif geometrie["type"] == "MultiPolygon":
        for poly in geometrie["coordinates"]:
            yield poly[0]


def contient(anneau, lon, lat):
    dedans = False
    n = len(anneau)
    for i in range(n):
        x1, y1 = anneau[i]
        x2, y2 = anneau[(i + 1) % n]
        if (y1 > lat) != (y2 > lat):
            x = x1 + (lat - y1) * (x2 - x1) / (y2 - y1)
            if x > lon:
                dedans = not dedans
    return dedans


def carte(nom, lat, lon, sortie, zoom=1.0, nom_pays=None):
    with open(GEO, encoding="utf-8") as f:
        pays = json.load(f)["features"]

    demi_lat = 10 / zoom
    demi_lon = demi_lat * (2.6 / 1.6) / math.cos(math.radians(lat))
    fig, ax = plt.subplots(figsize=(2.6, 1.6), dpi=320)
    fig.patch.set_facecolor(MER)
    ax.set_facecolor(MER)

    for p in pays:
        geom = p["geometry"]
        if not geom:
            continue
        if nom_pays:
            cible = nom_pays in (p["properties"].get("ADMIN"), p["properties"].get("NAME"))
        else:
            cible = any(contient(a, lon, lat) for a in anneaux(geom))
        for a in anneaux(geom):
            ax.add_patch(Polygon(a, closed=True, facecolor=PAYS_CIBLE if cible else TERRE,
                                 edgecolor=FRONTIERE, linewidth=0.5))

    ax.plot(lon, lat, "o", color=ENCRE, markersize=4.5, zorder=5)
    ax.annotate(nom, (lon, lat), xytext=(6, 4), textcoords="offset points",
                fontsize=8, family="DejaVu Serif", color=ENCRE, zorder=6)
    ax.set_xlim(lon - demi_lon, lon + demi_lon)
    ax.set_ylim(lat - demi_lat, lat + demi_lat)
    ax.set_aspect("auto")
    ax.axis("off")
    plt.subplots_adjust(0, 0, 1, 1)
    fig.savefig(sortie, facecolor=MER)
    plt.close(fig)


if __name__ == "__main__":
    a = argparse.ArgumentParser()
    a.add_argument("nom")
    a.add_argument("lat", type=float)
    a.add_argument("lon", type=float)
    a.add_argument("sortie")
    a.add_argument("--zoom", type=float, default=1.0)
    a.add_argument("--pays", help="nom ADMIN Natural Earth, pour une ville frontalière")
    x = a.parse_args()
    carte(x.nom, x.lat, x.lon, x.sortie, x.zoom, x.pays)
