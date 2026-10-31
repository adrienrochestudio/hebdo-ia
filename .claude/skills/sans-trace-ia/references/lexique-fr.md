# Lexique FR des marqueurs IA

Format lu par `scripts/audit.py` : `- terme | remplacement` (barre entourée d’espaces). Préfixe `re:` = expression régulière. Les titres `[rouge]` ou `[orange]` donnent la gravité.
Un mot seul ne prouve rien : c'est la densité qui trahit. Les sens propres restent permis (une clé USB, souligner au crayon).

## Ouvertures et clôtures pompeuses [rouge]
- il est important de noter | supprimer, donner le fait
- il est important de souligner | supprimer
- il convient de noter | supprimer
- il convient de souligner | supprimer
- il est crucial de | il faut
- il est essentiel de | il faut
- il est à noter que | supprimer
- force est de constater | supprimer
- en conclusion | supprimer ou "Bref"
- en résumé | supprimer
- en somme | supprimer
- pour conclure | supprimer
- comme nous l'avons vu | supprimer
- dans un monde où | supprimer
- à l'heure où | aujourd'hui, ou une date
- à l'ère de | supprimer
- sans plus attendre | supprimer
- n'hésitez pas à | dire l'action directement
- j'espère que ce message vous trouve | Bonjour
- re:\bcela a de l'importance\b | dire la conséquence concrète
- re:\bpourquoi (?:c|ce|cela|ça) (?:compte|importe)\b | supprimer

## Vocabulaire surutilisé [rouge]
- crucial | décisif, ou rien
- cruciale | décisive, ou rien
- essentiel | nécessaire, ou rien
- essentielle | nécessaire, ou rien
- primordial | rien
- incontournable | rien, ou "obligatoire" si vrai
- méticuleux | soigneux, ou décrire le soin
- méticuleusement | avec soin
- re:\b(?:point|élément|enjeu|facteur|rôle|acteur|chiffre|moment)s? clés?\b | principal, ou rien
- re:\bclés? de voûte\b | rien
- tournant majeur | décrire ce qui change
- re:\btémoign(?:e|ent|age) de\b | montre, preuve de
- tapisserie | rien
- vibrant | vivant, ou décrire
- re:\bpaysage (?:audiovisuel|numérique|actuel|médiatique|économique|culturel)\b | secteur, situation
- re:\bécosystème\b | secteur, réseau
- re:\bfaçonn(?:er|e|ent|é|ée|és|ant)\b | former, modeler, ou décrire
- re:\benrichi(?:r|t|ssant|ssent)\b | compléter, ajouter
- re:\bfavoris(?:er|e|ant|ent)\b | aider, permettre, ou supprimer
- re:\bmet(?:tre|tent)? en (?:lumière|avant|exergue|évidence)\b | montrer
- re:\bsoulign(?:e|ent|ant|er)\b | dire, montrer, rappeler
- re:\bplong(?:er|eons|e) (?:dans|au cœur)\b | aborder, ou rien
- au cœur de | dans
- re:\bfiab(?:le|les|ilité)\b | sûr, solide, ou le chiffre qui le prouve
- re:\brobustes?\b | solide
- holistique | global, ou rien
- synergie | rien
- re:\blevier\b | moyen
- re:\bstructur(?:er|ant|ante)\b | organiser
- verdoyant | vert, ou nommer la végétation
- re:\bréinvent(?:er|e|é)\b | refaire, changer
- re:\bvéritable (?:levier|atout|outil|pilier|vitrine)\b | supprimer l'adjectif
- re:\bpilier\b | base, ou rien

## Transitions mécaniques [orange]
- en outre | supprimer, ou "et"
- de plus | supprimer
- par ailleurs | supprimer
- néanmoins | mais
- toutefois | mais
- en effet | supprimer
- dès lors | donc
- de surcroît | supprimer

## Verbes et tournures de bureau [orange]
- mettre en œuvre | faire, appliquer
- re:\boptimis(?:er|e|ant)\b | améliorer, réduire (dire quoi)
- re:\bperme(?:t|ttent) de\b | réécrire avec le verbe direct
- jouer un rôle | dire ce qu'il fait
- re:\bser(?:t|vent) de\b | est
- re:\bconstitue(?:nt)?\b | est
- re:\bse positionne(?:nt)? comme\b | est
- re:\bs'inscri(?:t|vent) dans\b | fait partie de, ou supprimer
- re:\bdivers(?:es)?\b | nommer les éléments
- re:\bnombreu(?:x|ses)\b | donner le nombre
- re:\bparticulièrement\b | rien
- re:\bsignificati(?:f|ve|fs|ves|vement)\b | net, marqué, ou le chiffre
- re:\bvaleur ajoutée\b | dire le gain
- re:\bcontinue(?:nt)? d'évoluer\b | supprimer

## Formules spécifiques à Claude [rouge]
- honnêtement | supprimer
- franchement | supprimer
- re:\bla vraie question\b | supprimer
- re:\ble vrai sujet\b | supprimer
- re:\bvoici (?:le|la|ce) (?:problème|truc|point)\b | supprimer

## Mise en scène et résidus de chatbot [rouge]
- ce qui compte vraiment | dire la chose précise
- à bien y regarder | supprimer
- contrairement à ce qu'on pourrait croire | supprimer
- re:\bil ne s'agit pas (?:tant|seulement|uniquement) de\b | affirmer directement
- re:\bla réponse est simple\b | supprimer
- re:\bles informations disponibles sont limitées\b | dire ce que la source montre
- re:\bà ma connaissance\b | supprimer, ou citer la source
- re:\bj'espère que (?:cela|ça|ceci) (?:vous|t')aide\b | supprimer
- re:\bdans cette (?:section|partie),? nous (?:allons voir|verrons)\b | parler du sujet
- re:\ble tableau ci-dessous (?:compare|présente|résume)\b | parler du sujet

## Précautions et mises en scène [orange]
- au fond | supprimer
- re:\bpourrai(?:t|ent) potentiellement\b | pourrait
- re:\bil semblerait que\b | affirmer, ou citer la source
- re:\bce guide a pour (?:but|objectif) de\b | dire ce qu'il contient
