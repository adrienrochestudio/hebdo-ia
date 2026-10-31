---
name: "sans-trace-ia"
description: "Rédaction et relecture de tout texte en français, en anglais ou en portugais du Brésil pour qu'il ne porte aucune trace d'écriture IA - vocabulaire, tournures, typographie, fautes typiques des modèles, traductions conformes au lexique de l'utilisateur, dont la traduction FR vers pt-BR de la newsletter. Utiliser ce skill dès que Claude rédige, réécrit, traduit ou relit un texte destiné à être lu par d'autres - post LinkedIn, e-mail, article, rapport, guide, document Word, page web, communiqué, sous-titre, présentation - même si l'utilisateur ne parle pas d'IA. Utiliser aussi quand l'utilisateur demande si un texte \"fait IA\", veut le rendre plus naturel, passer un détecteur (GPTZero, Pangram, Turnitin, ZeroGPT) ou traduire avec son lexique. Utiliser aussi quand l'utilisateur dit avoir repris, corrigé ou réécrit un texte produit par Claude, colle sa propre version ou demande d'entraîner le skill : comparer les deux versions et intégrer les leçons au skill."
---

# sans-trace-ia

Objectif : un texte qu'un lecteur attentif ou un détecteur ne rattache pas à une IA, sans tricher sur la qualité. On corrige le fond (précision, faits) autant que la surface (mots, typographie).

Langues couvertes : français, anglais, portugais du Brésil (pt-BR). Les règles de ce fichier valent pour les trois.

## Pourquoi le fond d'abord

Un modèle de langue tend vers la formulation la plus probable. Il remplace les faits rares et précis par des généralités positives qui s'appliqueraient à n'importe quel sujet. Retirer seulement les mots marqueurs donne un texte creux mais plus difficile à repérer : ce n'est pas le but. Chaque phrase doit porter une information vérifiable ou une position assumée.

## Procédure

1. **Lexique de traduction** : si le texte est une traduction ou touche à un terme métier, lire `references/traduction.md` avant d'écrire. Pour une traduction FR vers pt-BR, lire sa section « Français vers portugais du Brésil » et `references/lexique-pt.md` avant d'écrire, pas seulement en relecture. Les équivalences qu'il impose priment sur tout le reste du skill.
2. **Rédiger** en appliquant les règles ci-dessous. Pour un texte fourni à réécrire, ne pas garder sa structure comme acquise : repérer d'abord les signaux, du plus fort au plus faible, puis réécrire.
3. **Relire** avec `references/structures.md` (tournures) et le lexique de la langue : `references/lexique-fr.md`, `references/lexique-en.md` ou `references/lexique-pt.md` (pt-BR, avec les gallicismes de traduction). Vérifier ensuite que chaque phrase a un verbe conjugué (voir "Phrases complètes") : l'audit ne le contrôle pas. Puis se poser une seule question sur le brouillon : "qu'est-ce qui fait encore IA ici ?" Corriger ce qui en ressort avant de livrer la version finale.
4. **Auditer** quand le texte dépasse environ 80 mots ou qu'il sort en fichier :
   `python3 scripts/audit.py fichier.txt --lang fr` (ou `--lang en`, `--lang pt`, ou texte sur l'entrée standard).
   Corriger chaque alerte rouge. Les alertes orange se jugent en contexte.
5. **Ne pas annoncer** la relecture à l'utilisateur sauf demande : livrer le texte propre.

L'audit couvre le lexique et le rythme. Il ne couvre pas ce que repère un classifieur entraîné (Pangram, Turnitin), qui juge la forme d'ensemble. Un score de 100/100 à l'audit n'est donc pas un passage garanti : les sections "Contre-optimisation" et "Signature de structure" ci-dessous visent précisément ce que l'audit ne voit pas.

Faits et fichiers
- Ne jamais inventer un nom, un chiffre, une date, une citation ou une source pour remplacer une généralité. Si le détail manque, le demander.
- Sur un fichier (Markdown, HTML, code), ne réécrire que la prose : le code, les données, l'en-tête et les cibles de liens restent intacts.

Calibrer sur la voix de l'utilisateur
- Si l'utilisateur fournit deux ou trois paragraphes écrits par lui, reprendre son rythme, son vocabulaire, sa ponctuation et ses tics, sauf ceux que ce skill interdit (tiret cadratin). Un texte personnel garde ses opinions ; un texte technique reste neutre.

## Apprendre d'une correction de l'utilisateur

Quand l'utilisateur dit qu'il a repris un texte produit par Claude ("j'ai repris ton texte", "voici ma version", "entraîne le skill"), chaque écart entre les deux versions est une donnée d'entraînement. Le but est de comprendre pourquoi Claude a écrit ce que l'utilisateur a changé, et d'en tirer une règle qui évitera le même écart sur d'autres textes. Le skill écrit pour cet utilisateur : ses préférences de style comptent comme des règles.

1. **Récupérer les deux versions.** La version de Claude est en général plus haut dans la conversation ; sinon la chercher dans les conversations passées ; sinon la demander. La version de l'utilisateur peut être collée, jointe ou dans un document partagé. Enregistrer les deux en texte brut (`ia.txt`, `humain.txt`).
2. **Comparer** : `python3 scripts/compare.py ia.txt humain.txt` (ajouter `--json` pour un traitement automatique). Le rapport donne les métriques avant/après (longueur et rythme des phrases, ponctuation, première personne, score d'audit), chaque écart phrase par phrase avec des indices (connecteur ajouté, tiret retiré, phrase réécrite, fusionnée ou scindée, déjà au lexique) et des candidats pour le lexique.
3. **Classer chaque écart** selon les catégories de `references/lecons.md` : lexique, traduction, tournure, typographie, règle de rédaction, fond propre au texte. Un fait corrigé ou une information que seul l'utilisateur connaissait ne s'apprend pas, sauf quand il remplace une généralité : c'est alors le réflexe "généralité au lieu du fait" qui s'apprend.
4. **Remonter à la cause.** Pour chaque écart retenu, chercher l'habitude de modèle qui l'a produit et formuler la règle à ce niveau : "le modèle compresse une relative en idiome" plutôt que "ne pas écrire along the way". Le lexique est la seule catégorie où l'on note le mot exact.
5. **Intégrer dans une copie du skill.** Le dossier installé est en lecture seule : copier le dossier qui contient ce SKILL.md dans le répertoire de travail et modifier la copie, en reprenant l'avant/après réel comme exemple. Un candidat lexique du script n'entre au lexique que si le remplacement vaut hors de ce texte : en orange à la première occurrence, en rouge quand il revient ou que l'utilisateur le demande. Une règle du SKILL.md ne s'ajoute qu'à la deuxième occurrence d'une même leçon dans le journal, ou dès la première si l'utilisateur la formule comme règle. Quand une correction contredit une règle existante, la correction gagne et la règle est réécrite.
6. **Journaliser** chaque leçon dans `references/lecons.md`. Si la leçon y figure déjà, augmenter son compteur d'occurrences au lieu d'ajouter une entrée.
7. **Contrôler.** Relancer `scripts/audit.py` sur la version de l'utilisateur : elle ne doit déclencher aucune alerte rouge, sinon la règle en cause est trop stricte et doit être corrigée. Relancer l'audit sur la version de Claude : les mots ajoutés au lexique doivent maintenant y être signalés.
8. **Livrer** : depuis la copie, `python3 scripts/empaqueter.py <dossier-de-sortie>`, puis envoyer le fichier `.skill` à l'utilisateur, qui le réinstalle depuis la carte du fichier. Plusieurs corrections dans la même conversation se cumulent sur la même copie et partent dans un seul paquet.
9. **Rendre compte** en quelques lignes : les leçons retenues, le fichier où chacune est entrée, les écarts écartés et pourquoi. Poser une question fermée seulement quand un écart se lit de deux façons (préférence personnelle ou erreur de modèle) et que la réponse change la règle.

## Règles de rédaction

Fond
- Préférer le fait précis au commentaire : un nom, un chiffre, une date, un lieu plutôt que "un rôle majeur".
- Ne pas expliquer pourquoi le sujet est important. Si c'est important, les faits le montrent.
- Attribuer une opinion à une source nommée, ou l'assumer. Jamais "les experts", "de nombreux observateurs".
- Pas de section ou de phrase finale "défis et perspectives", "en conclusion", "en résumé", sauf si le format l'exige.
- Pas de ton promotionnel ni de superlatifs non chiffrés.

Phrases complètes
- Chaque phrase a un sujet et un verbe conjugué. Le fragment nominal posé comme une phrase entière est une signature de modèle : il imite un effet de copywriting, mais personne n'écrit comme ça en continu.
  - Avant : Ninety minutes with four people who do this work daily.
  - Après : For ninety minutes, four people who do this work daily shared what they had learned.
  - Avant : Trois jours, dix-neuf participants, neuf pays.
  - Après : Dix-neuf participants de neuf pays ont suivi les trois jours d'atelier.
- Le symptôme à repérer : une phrase qui s'arrête net sur un groupe nominal, sans que rien n'y agisse. Reformuler avec le verbe qui dit ce qui s'est passé.
- Un fragment isolé reste possible pour un effet voulu, une fois dans un texte long. Deux ou plus, c'est la signature.
- Même règle pour l'empilement : plusieurs phrases courtes autonomes à la suite, toutes construites pareil, trahissent autant qu'un fragment. Les lier par une conjonction, une relative ou une virgule.
- Cas fréquents dans un cours ou un document structuré, à chercher un par un en relecture car l'audit ne les repère pas :
  - le chiffre posé en tête de volet ou de carte, souvent en gras. Avant : **Dix fois plus d'émissions par gigaoctet** sur un réseau mobile que sur un réseau fixe. Après : Un gigaoctet envoyé sur un réseau mobile émet **dix fois plus** que sur un réseau fixe.
  - la consigne d'exercice. Avant : Deux questions pour vérifier les notions de la leçon. Après : Ces deux questions vérifient les notions de la leçon.
  - la définition hors glossaire. Avant : Apports de nutriments vers les milieux aquatiques, qui asphyxient les écosystèmes. Après : L'eutrophisation désigne les apports de nutriments vers les milieux aquatiques, qui asphyxient les écosystèmes.
  - l'énumération posée comme une phrase. Avant : Analyse et tri des rushes, génération de métadonnées, restauration. Après : Les usages y couvrent l'analyse et le tri des rushes, la génération de métadonnées et la restauration.
- Un glossaire (lexique, liste de définitions) garde ses définitions nominales : c'est la convention du genre.

Contre-optimisation : écrire moins bien que le modèle ne le voudrait

Un modèle optimise vers la phrase courte, dense, variée, sans répétition. Un humain est plus explicite, plus redondant, moins économe. C'est cet écart que repère un classifieur entraîné, et il ne se corrige pas en changeant des mots. Six réflexes à inverser :

- **La relative plutôt que l'idiome compressé.** Dire la chose au lieu de la suggérer par une tournure élégante.
  - Avant : Plenty of films and tools to draw from were mentioned along the way.
  - Après : Many films and tools that could inspire you were mentioned during this webinar.
- **Nommer le référent, même si c'est redondant.** "During this webinar" dans un post qui parle déjà du webinaire, "dans ce rapport" dans un rapport. Le modèle fuit la redite par une anaphore ou un repère vague ("along the way", "ici", "dans ce cadre") : c'est un marqueur.
- **Garder les connecteurs de conversation.** "Of course", "bien sûr", "aussi", "d'ailleurs", "et" en tête de phrase. Le modèle les élague pour resserrer ; leur absence donne un texte poli à la machine.
- **Répéter un mot plutôt que varier.** La variation élégante ("so did", "cette dernière", un synonyme à chaque occurrence) est une habitude de modèle. Reprendre le même mot est normal à l'écrit.
- **Ne pas sacrifier un détail identifiant au rythme.** Le titre complet d'une personne, le nom entier d'une structure, une date : on les garde même si la phrase s'alourdit.
- **Une liste se présente en liste.** Quand le contenu est une énumération (des personnes, des mesures, des critères), mettre des puces ou des tirets. Le modèle tisse la liste en prose fluide pour "faire naturel" : c'est l'inverse qui l'est.

Signature de structure

Au-delà de la phrase, c'est l'architecture du texte qui trahit. À vérifier sur tout texte destiné à être publié :

- **Un paragraphe, une fonction, dans l'ordre attendu.** Annonce, contexte, contenu, clôture, appel à l'action. Aucune digression, aucun aparte, aucune redite. Un texte humain a un centre de gravité déséquilibré : il s'étend sur ce qui intéresse l'auteur et expédie le reste.
- **Traitement égal de tous les éléments.** Quatre personnes présentées en quatre phrases de même structure, un titre chacune. Préférer trois lignes sur l'une et une mention rapide pour les autres.
- **Absence d'auteur.** Pas de "je", pas d'avis, aucun détail que seul quelqu'un de présent pourrait donner. Si le texte raconte un événement, il lui faut au moins un élément de témoin : une phrase prononcée, un désaccord, une question restée sans réponse.
- **Registre uniforme.** Tout au même niveau de langue déclaratif et calme du début à la fin.
- **Double appel à l'action.** Une phrase d'incitation suivie du lien qui dit la même chose. En garder un seul.

Quand le texte raconte quelque chose que Claude n'a pas vécu et qu'aucun détail de témoin n'est disponible, le dire à l'utilisateur et lui demander deux ou trois éléments vécus plutôt que de combler avec des généralités.

Rythme (c'est ce que mesurent les détecteurs statistiques)
- Varier vraiment la longueur des phrases : des phrases de 4 mots à côté de phrases de 30.
- Varier l'ouverture des phrases. Éviter trois phrases de suite qui commencent par le sujet.
- Ne pas grouper par trois par réflexe (adjectifs, exemples, bénéfices). Deux ou quatre, ou un seul bien choisi.
- Écrire "est", "a" quand c'est le sens. Pas "sert de", "constitue", "se positionne comme", "offre".
- Choisir parfois le mot exact mais moins attendu, sans tomber dans le rare gratuit.

Typographie
- Jamais de tiret cadratin (—). Le tiret demi-cadratin (–) seulement dans les intervalles (2024-2026 s'écrit aussi avec un trait d'union).
- Pas de gras pour souligner dans un texte courant. Pas de titres en forme de question.
- Détails par langue dans `references/typographie.md`.

Ce qu'on ne fait pas
- Pas de fautes volontaires, de caractères invisibles, de synonymes forcés pour tromper un détecteur. Ces techniques dégradent le texte et les classifieurs récents (Pangram) les repèrent. Si l'utilisateur demande un passage garanti aux détecteurs, dire qu'aucune garantie n'existe et appliquer le skill.

## Fichiers

- `references/lexique-fr.md` : mots et expressions marqués en français, avec remplacements
- `references/lexique-en.md` : idem en anglais, classés par génération de modèle
- `references/lexique-pt.md` : idem en portugais du Brésil, avec les calques du français et les marques du pt-BR
- `references/structures.md` : tournures IA avec exemples avant/après (les deux langues)
- `references/typographie.md` : règles FR, EN et pt-BR, fautes typiques des modèles
- `references/traduction.md` : lexique de traduction de l'utilisateur, calques à éviter, méthode FR vers pt-BR
- `references/detecteurs.md` : fonctionnement des détecteurs, à lire si l'utilisateur pose la question
- `scripts/audit.py` : contrôle chiffré, lit les lexiques ci-dessus
- `references/lecons.md` : journal des corrections de l'utilisateur et des leçons tirées
- `scripts/compare.py` : comparaison entre la version de Claude et la version reprise par l'utilisateur
- `scripts/empaqueter.py` : produit le fichier .skill à réinstaller après une mise à jour