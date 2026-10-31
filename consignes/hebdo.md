# Hebdo IA : consignes de l'édition de la semaine

Une exécution = une édition en trois rubriques (Actualité, Environnement, Technique), chacune finie par un quiz, publiée dans l'app (https://adrienrochestudio.github.io/hebdo-ia/). Lecteur : Adrien, francophone, à l'aise avec le numérique, qui veut comprendre l'IA en profondeur : son industrie dans le monde entier, son coût environnemental, sa technique et ce qu'elle change dans les métiers.

Fichiers : schéma du JSON en tête de `outils/publier.py` ; règles d'écriture dans `consignes/ecriture.md` ; format des schémas dans `outils/schema.py`. Ne charger aucun skill.

## Ligne éditoriale

- Scope mondial. Pas seulement OpenAI, Anthropic et Google : Chine (DeepSeek, Alibaba Qwen, Moonshot, Zhipu, MiniMax, ByteDance, Huawei), Europe (Mistral, Aleph Alpha, Black Forest Labs, Helsing, Poolside, H Company), Inde, Golfe, Japon, Corée, Afrique, Amérique latine, open source, startups, États, régulateurs, fonds, fabricants de puces et d'équipements (TSMC, ASML, SK hynix, Samsung), hébergeurs, syndicats, chercheurs.
- Ni promotion ni catastrophisme. Pas de reprise de communiqué : chaque annonce est remise en contexte (chiffres, concurrents, ce qui est vérifiable et ce qui ne l'est pas). Les critiques sérieuses ont leur place, chiffrées.
- Priorité à ce qui a un effet réel (argent engagé, électricité consommée, emplois, lois votées, usages mesurés) sur ce qui fait du bruit. Une rumeur ou une démo sans chiffres ne fait pas un article.
- Aucune mention d'Ecoprod ni de ses publications.

## Rubrique Actualité (id `actualite`)

L'industrie de l'IA dans le monde : entreprises, modèles, argent, puces, États, régulation, usages.

- `une` : l'information la plus importante de la semaine, en 3 ou 4 lignes factuelles.
- 4 articles `Fait de la semaine · <zone>` (zones : États-Unis, Chine, Europe, France, Inde, Golfe, Asie, Afrique, Amérique latine, Monde), 250 à 450 mots chacun. Au plus deux sur les États-Unis et au plus un sur OpenAI, Anthropic, Google, Meta ou Microsoft (les autres acteurs américains d'abord : puces, nuages, startups, États, syndicats) ; au moins un sur la Chine, un sur l'Europe ou la France, et un sur une autre zone (Inde, Golfe, Asie hors Chine, Afrique, Amérique latine). Au plus un sur une annonce de modèle.
- 1 `Portrait` : une entreprise, un laboratoire ou une personne importante mais peu médiatisée (pas Altman, Musk, Huang, Amodei, Zuckerberg), 400 à 600 mots, avec portrait ou logo.
- 1 `Le chiffre` (format `chiffre`) : le titre est le chiffre lui-même ; 120 à 250 mots qui expliquent l'ordre de grandeur et la comparaison qui le rend lisible.
- 1 `Dossier` (format `dossier`) : 1 200 à 1 800 mots, en 4 à 6 parties, sur une question de fond liée à un fait de la semaine (un modèle économique, un rapport de force, une chaîne d'approvisionnement, une loi).
- Brèves, 2 à 4 items par groupe, groupe omis s'il est vide : États-Unis, Chine, Europe et France, Reste du monde, Argent et marchés.

## Rubrique Environnement (id `environnement`)

Tous les enjeux environnementaux de l'IA : électricité et mix énergétique, eau, data centers et territoires, matériel et minerais (cuivre, gallium, germanium, terres rares, cobalt), fabrication des puces, déchets électroniques, émissions publiées par les entreprises, méthodes de mesure, réglementation, usages sobres, et aussi ce que l'IA apporte à la recherche environnementale quand c'est chiffré.

- `une` : 3 ou 4 lignes.
- 3 articles `Fait de la semaine · <thème>` (thèmes : Énergie, Eau, Data centers, Minerais, Puces, Émissions, Réglementation, Usages, Recherche), 250 à 450 mots.
- 1 `Angle mort` : une donnée qui manque. Ce que les entreprises ou les États ne publient pas (consommation par requête, eau, scope 3, localisation), pourquoi, ce qu'on peut estimer et avec quelle marge, qui réclame la donnée. 400 à 600 mots.
- 1 `Le chiffre` (format `chiffre`).
- 1 `Dossier` (format `dossier`), 1 200 à 1 800 mots.
- Brèves : Énergie, Eau et territoires, Matériel et minerais, Transparence et règles, Usages.
- Repères de lecture : distinguer entraînement et inférence ; puissance (MW, GW) et énergie (MWh, TWh) ; émissions selon la méthode (location-based ou market-based) ; prélèvement et consommation d'eau. Toujours dire de quelle méthode vient un chiffre et qui l'a calculé.

## Rubrique Technique (id `technique`)

Comprendre comment l'IA fonctionne et comment elle entre dans les logiciels et les métiers. Le lecteur n'est pas ingénieur mais veut le vrai mécanisme, sans simplification fausse.

- 1 `Mécanisme` (format `dossier`) : 1 200 à 1 800 mots sur un mécanisme technique, expliqué pas à pas avec un `schema` obligatoire (attention et transformeurs, tokenisation, mélange d'experts, cache KV, quantification, distillation, RAG, agents et protocole MCP, modèles de diffusion, génération vidéo, apprentissage par renforcement, évaluation et benchmarks, fenêtres de contexte, inférence spéculative...). De préférence lié à une actualité de la semaine. Une notion déjà expliquée dans les 12 dernières éditions n'est pas refaite.
- 1 `Infrastructure` : 400 à 700 mots sur le matériel ou l'exploitation (GPU, TPU, ASIC, mémoire HBM, réseaux, refroidissement, alimentation, service d'inférence, coûts par million de jetons).
- 2 `Métier · <métier>` : 450 à 800 mots chacun. L'IA dans un métier précis : quels logiciels (nom, éditeur, fonction), quelle étape du travail change, ce qui est mesuré (temps, coût, qualité), ce qui coince (droits, qualité, emploi, formation). Rotation, sans reprendre un métier traité dans les 8 dernières éditions (`historique.py notions`). Chaque semaine, au moins un métier de l'image : cinéma (production, écriture, casting), effets visuels, post-production (montage, étalonnage, son, doublage, sous-titrage), animation 2D et 3D, jeu vidéo, photographie, publicité. L'autre parmi : finance, management, ressources humaines, droit, santé, architecture, journalisme, éducation, recherche, industrie, logistique, agriculture, administration publique, design, musique, traduction.
- 1 `Outil` : 300 à 500 mots sur un outil, un modèle ouvert ou une méthode que l'on peut essayer, avec ce qu'il faut pour le faire tourner (matériel, coût, licence) et ses limites.
- 1 `Glossaire` : 4 à 6 termes de l'édition, en bloc `definitions`, une ou deux phrases chacun. Pas de sources obligatoires.
- Pas d'`une` ni de brèves obligatoires ; des brèves « Logiciels et outils » sont possibles.

## Quiz (les trois rubriques)

6 questions par rubrique, sur le contenu de la rubrique : chiffres, acteurs, mécanismes, définitions. Trois choix plausibles (quatre au plus), une seule bonne réponse, position de la bonne réponse variée. `explication` : une ou deux phrases qui redonnent le fait et sa source. Pas de question piège sur un détail sans intérêt.

## Visuels

Viser au moins 70 % d'articles illustrés (contrôlé), avec des images qui apprennent quelque chose. Licences libres uniquement, chargées par `"url"` : jamais d'image de presse, de capture d'un produit commercial ni de photo de célébrité. Chaque image porte `"nature"` : `portrait`, `logo`, `donnees`, `photo` ou `carte_lieu`.

- Données : graphiques et cartes Our World in Data (`https://ourworldindata.org/grapher/<graphique>.png?tab=chart` ou `tab=map`, `"lien"` vers la version interactive sans `.png`, crédit "Our World in Data, CC BY", `"largeur": 1100`). Chercher avec WebFetch sur `https://ourworldindata.org/search?q=<sujet>` (ex. "artificial intelligence", "electricity", "data centers", "copper").
- Barres (`barres`) pour comparer 2 à 8 quantités sourcées (investissements, consommations, parts de marché, prix par million de jetons) ; `accent` sur celle dont parle l'article.
- Schémas (`schema`) pour un mécanisme ou un circuit : vrais nœuds avec `valeur` et `detail`, liens libellés (données, énergie, argent, décisions), 3 nœuds au plus par étage, 4 à 6 mots par nœud.
- Portraits et logos des personnes et organisations peu connues : Wikimedia Commons, `"largeur": 360` (portrait) ou `240` (logo), souvent dans un `duo`.
- Photos Wikimedia Commons d'un data center, d'une puce, d'une mine, d'un site, en pleine largeur.
- Mini-cartes (`carte`) pour chaque lieu peu connu (site de data center, mine, usine, ville) ; `"pays"` en nom Natural Earth si la ville est près d'une frontière.
- Couverture des dossiers : une photo Wikimedia Commons ou un graphique Our World in Data qui représente le sujet, jamais décorative et jamais une mini-carte (elle serait recadrée).
- Au moins 2 images Wikimedia ou Our World in Data par rubrique (contrôlé) : schémas, barres et mini-cartes ne suffisent pas à illustrer une édition. Le Portrait porte un portrait ou un logo (contrôlé).
- Wikimedia Commons : le réseau de la tâche n'atteint pas Commons. Ne pas chercher d'adresse d'image : donner le fichier, GitHub Actions (`outils/images.py`) remplit `url` et `credit` juste après la publication et retire ce qui n'existe pas. Deux formes, à la place de `url` :
  - `"commons": "File:Nom exact.jpg"` quand WebSearch (requête `site:commons.wikimedia.org <sujet>`) ou une page lue donne le nom exact du fichier ; c'est la forme à préférer, surtout pour un portrait ou un logo ;
  - `"commons_recherche": "<3 à 5 mots anglais précis>"` sinon (ex. "Microsoft data center Quincy", "Huawei Ascend 910 chip", "copper mine Chuquicamata") ; le premier fichier sous licence libre est retenu, donc la requête doit nommer le sujet exact, jamais un thème vague.
  Ne pas écrire de `credit` pour ces images. Our World in Data garde son `url` directe.
- Légendes : dire ce qu'il faut regarder (la courbe, l'écart, la zone), pas seulement ce que c'est.

## Réseau et sources

- Le shell de la tâche n'atteint ni les sites de presse ni Wikimedia (proxy 403) : c'est normal. Seuls git, GitHub et les dépôts de paquets passent. Toute lecture du web passe par WebSearch et WebFetch.
- La veille (flux de `consignes/veille.txt`, sept derniers jours) est préparée par GitHub Actions avant la tâche sur la branche `veille`. Les flux généralistes y sont déjà filtrés sur l'IA.
- WebSearch : `mode: "extended"` pour l'actualité datée, requêtes précises, lancées en parallèle dans un seul tour. WebFetch sur l'adresse directe de l'article, jamais une redirection Google. Une page qui refuse la lecture : passer à une autre source.
- Sources primaires d'abord : communiqués et rapports d'entreprise (rapports environnementaux annuels, dépôts SEC), AIE, Epoch AI, Stanford AI Index, OCDE.AI, LBNL, Uptime Institute, Commission européenne, CNIL, Arcep, ADEME, Ember, Our World in Data, articles de recherche (arXiv, avec date et laboratoire). Presse de référence ensuite (Reuters, FT, Bloomberg, Les Échos, Le Monde, The Information, SCMP, Caixin, Nikkei, Rest of World, Data Center Dynamics, IEEE Spectrum). Métiers de l'image : befores & afters, fxguide, Cartoon Brew, Animation Magazine, CNC, Film français. Éviter les agrégateurs et les blogs de référencement.
- `sources` : `titre` est le nom court du média ou de l'institution ("Reuters", "AIE"), un média une fois par article.

## Déroulé

Dépendances : `pip install pillow matplotlib` si l'import échoue. Au plus 24 recherches web et 40 lectures de page au total.

1. État : `python3 outils/historique.py etat`. Code 3 (semaine déjà couverte) : arrêter là, sans rien publier, et finir par la phrase qu'il affiche. Code 0 : continuer. Une relance le jour même d'une édition publiée est voulue par Adrien : refaire et remplacer l'édition, sans exception.
2. Mémoire : `python3 outils/historique.py notions` (sujets, métiers, mécanismes des 12 dernières éditions).
3. Veille : `git fetch origin veille && git worktree add veille FETCH_HEAD`, lire `veille/veille.txt` (sa première ligne donne l'heure). Si la branche manque ou date de plus de 30 heures : `python3 outils/veille.py > veille.txt` (peut échouer faute de réseau), sinon WebSearch, une requête par rubrique. Choisir les sujets, `python3 outils/veille.py lien <numéros>` pour leurs adresses.
4. Recherche, en vagues parallèles : lectures des articles retenus, compléments par WebSearch (Chine, Golfe, Inde et Afrique sont mal couverts par les flux : chercher exprès), données et chiffres, images.
5. Rédaction de `edition.json` (dossier de travail, pas dans `editions/`) selon le schéma de `outils/publier.py`. `date_texte` : la date du jour, "Dimanche 8 novembre 2026". `semaine_texte` : les sept jours couverts, "Semaine du 2 au 8 novembre 2026".
6. `python3 outils/historique.py verifier edition.json` : changer tout sujet signalé PROCHE, sauf fait nouveau dit dans le titre.
7. Contrôle : `python3 outils/publier.py edition.json --texte`. Compléter tout ce qu'il liste en MANQUE et relancer jusqu'à ce qu'il n'en reste aucun. Puis l'audit : `python3 .claude/skills/sans-trace-ia/scripts/audit.py edition.txt --lang fr`. Corriger dans le JSON toute alerte rouge (les alertes "de plus" dans une comparaison chiffrée sont acceptées).
8. Relecture des faits : pour chaque chiffre, date et nom, vérifier qu'il figure dans une source lue cette semaine. Retirer ce qui n'est pas vérifiable. Vérifier que chaque bonne réponse de quiz est juste.
9. Publication : `python3 outils/publier.py edition.json --pousser`. `--forcer` seulement pour un MANQUE de matière (une rubrique sans assez de faits fiables cette semaine), après deux recherches supplémentaires. Jamais pour les images, la diversité des zones, le quiz ou la longueur : ceux-là se corrigent toujours. Une relance ne republie jamais l'édition en ligne telle quelle.
10. Fin : une phrase qui donne le numéro publié, les titres des trois dossiers et ce qui manque éventuellement.

## En cas d'échec

Aucun mail, aucune notification envoyée par la tâche : tout passe par l'app et par le message de fin de tâche.
- Accès git refusé : ne rien publier ; finir par le message d'erreur git exact.
- Une rubrique sans matière fiable : publier avec `--forcer`, la rubrique la plus courte plutôt qu'une rubrique inventée.
- Échec complet : finir par une phrase qui donne la cause. L'édition précédente reste en ligne.
