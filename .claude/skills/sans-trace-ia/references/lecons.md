# Journal des leçons

Une entrée par correction de l'utilisateur sur un texte produit par Claude. Ce journal sert à repérer les écarts qui reviennent avant d'en faire une règle du SKILL.md. Les entrées les plus récentes vont en haut.

Format d'une entrée :

## AAAA-MM-JJ | type de texte | langue
- Écart : « avant » -> « après » (le plus court possible)
- Leçon : la règle générale, formulée pour d'autres textes
- Intégrée dans : fichier modifié, ou "journal seulement"
- Occurrences : 1 (augmenter quand la même leçon revient)

Catégories d'intégration :
- lexique : mot ou expression retiré ou remplacé -> `lexique-fr.md`, `lexique-en.md` ou `lexique-pt.md`
- traduction : terme rendu autrement -> `traduction.md`, section lexique de l'utilisateur
- tournure : construction de phrase -> `structures.md`, avec l'avant/après réel
- typographie : ponctuation, tirets, guillemets, majuscules -> `typographie.md`, et `audit.py` si un motif suffit à la repérer
- règle de rédaction : fond, rythme, architecture du texte -> SKILL.md à partir de 2 occurrences, ou dès la première si l'utilisateur la formule comme règle
- fond propre au texte : fait corrigé, information ajoutée par l'utilisateur -> journal seulement, sauf si l'écart révèle un réflexe (une généralité remplacée par un fait, par exemple)

## Entrées

## 2026-10-22 | post LinkedIn StepUP (EmpCo) | en
- Écart : « What still holds up is a claim backed by proof. » signalé par Adrien comme « fait IA » ; même famille : « That is the date from which... », « That is what a green production strategy is for »
- Leçon : la phrase pseudo-clivée (sujet vide puis contenu) et le renvoi « That is what / That is the date » mettent en scène l'information au lieu de la dire. Écrire sujet réel + verbe.
- Intégrée dans : structures.md (n° 22), audit.py (motifs en et fr)
- Occurrences : 1 (formulée comme règle par l'utilisateur)

## 2026-10-22 | post LinkedIn StepUP (EmpCo) | en
- Écart : « eco-friendly » employé, alors qu'il figure dans le lexique Ecoprod d'Adrien comme traduction interdite de « éco-responsable »
- Leçon : le lexique de traduction d'Adrien n'était pas dans le skill. Il est intégré en entier dans traduction.md, et ses faux sens les plus nets sont repérés par l'audit.
- Intégrée dans : traduction.md, lexique-en.md (sections rouge et orange)
- Occurrences : 1
