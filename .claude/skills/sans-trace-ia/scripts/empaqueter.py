#!/usr/bin/env python3
"""Empaquette le skill en fichier .skill à réinstaller par l'utilisateur.

Usage : python3 empaqueter.py [dossier-de-sortie]
Le dossier installé du skill est en lecture seule : on travaille sur une copie
(voir "Apprendre d'une correction" dans SKILL.md), puis on lance ce script depuis la copie.
"""
import re, sys, zipfile
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
SKIP_DIRS = {"__pycache__", "node_modules", "evals"}


def main():
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    head = (SKILL / "SKILL.md").read_text(encoding="utf-8").split("---")[1]
    name = re.search(r'^name:\s*"?([\w-]+)"?', head, flags=re.M).group(1)
    if not re.search(r"^description:", head, flags=re.M):
        sys.exit("SKILL.md sans description : paquet annulé")
    out.mkdir(parents=True, exist_ok=True)
    dest = out / f"{name}.skill"
    n = 0
    with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(SKILL.rglob("*")):
            rel = f.relative_to(SKILL)
            if not f.is_file() or set(rel.parts) & SKIP_DIRS or f.suffix == ".pyc" or f.name == ".DS_Store":
                continue
            z.write(f, Path(name) / rel)
            n += 1
    print(f"{dest} ({n} fichiers)")


if __name__ == "__main__":
    main()
