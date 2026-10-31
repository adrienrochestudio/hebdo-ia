# Fonctionnement des détecteurs (pour répondre à l'utilisateur)

Trois familles :
1. Statistiques (GPTZero, ZeroGPT) : un petit modèle de langue lit le texte et mesure la perplexité (mots prévisibles = suspect) et la burstiness (variation de la perplexité et de la longueur des phrases ; uniforme = suspect). Faux positifs fréquents sur les textes juridiques, scientifiques, ou d'auteurs non natifs.
2. Classifieurs entraînés (Pangram, Turnitin) : réseau entraîné sur des paires texte humain / texte IA, sort des classes (humain, assisté, généré). Plus robustes. Une étude de l'Université de Chicago (2025) place Pangram en tête, y compris face aux outils de réécriture ; une étude de 2026 (arXiv 2608.11256) mesure à l'inverse plus de 96 % de passage des textes "humanisés".
3. Filigranes : marque statistique insérée à la génération (SynthID chez Google). Ne concerne que les modèles qui l'appliquent.

Ce que ce skill change : rythme varié, mots moins prévisibles, faits précis. Ce qu'il ne promet pas : un passage garanti face à un classifieur entraîné.
Wikipédia note que les humains distinguent mal les deux, sauf les gros utilisateurs d'IA, qui repèrent environ 90 % des textes générés.
