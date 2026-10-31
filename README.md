# Hebdo IA

App de lecture hebdomadaire sur l'intelligence artificielle, installable sur iPhone (app web, écran d'accueil), lisible hors ligne : https://adrienrochestudio.github.io/hebdo-ia/

Trois rubriques par édition, chacune finie par un quiz de 6 questions :
- Actualité : l'industrie de l'IA dans le monde (entreprises, modèles, argent, puces, États, régulation).
- Environnement : électricité, eau, data centers, minerais, émissions, données manquantes.
- Technique : mécanismes, infrastructure, outils, et l'IA dans les métiers (dont cinéma, VFX, post-production, animation).

## Organisation

- `index.html`, `app.js`, `rendu.js`, `edition.js`, `suivi.js`, `textes.js`, `styles.css`, `sw.js` : l'app (aucune dépendance, aucun build).
- `editions/index.json` et `editions/AAAA-MM-JJ/` : les éditions publiées (edition.json + schémas et cartes dans img/). Toutes restent consultables depuis le menu.
- `outils/publier.py` : contrôle et publication d'une édition (schéma du JSON en tête du fichier). Ne pousse que `editions/`.
- `outils/historique.py` : état de la semaine, sujets déjà traités (lus dans les éditions publiées), contrôle des doublons.
- `outils/veille.py` et `consignes/veille.txt` : veille RSS de la semaine, lancée par GitHub Actions (`.github/workflows/veille.yml`) le dimanche à 6h05 et publiée sur la branche `veille`.
- `outils/schema.py`, `outils/locator.py` : schémas, graphiques en barres et mini-cartes dessinés à la publication.
- `consignes/hebdo.md` (déroulé et ligne éditoriale), `consignes/ecriture.md` (règles d'écriture).
- `.claude/skills/sans-trace-ia` : audit du texte (appelé par chemin, sans charger le skill).

## Production

Une tâche planifiée Claude Code, « Hebdo IA », le dimanche à 8h52 (heure de Paris), avec ce dépôt attaché, suit `consignes/hebdo.md`. Une exécution moins de 6 jours après la dernière édition ne publie rien, sauf le jour même (relance voulue, l'édition est remplacée).

## Modifier l'app

Changer `VERSION` dans `sw.js` à chaque modification, sinon les appareils gardent l'ancienne version (ils proposent ensuite « Recharger »).

## Installer sur l'iPhone

Ouvrir l'adresse dans Safari, bouton Partager, « Sur l'écran d'accueil ».
