# Écriture : règles de Hebdo IA

Condensé du skill `.claude/skills/sans-trace-ia`, à appliquer en écrivant. L'audit (`python3 .claude/skills/sans-trace-ia/scripts/audit.py edition.txt --lang fr`) contrôle le lexique et le rythme : ne pas charger le skill ni ses lexiques.

## Fond

- Chaque phrase porte un fait : nom, chiffre, date, lieu. Jamais "un rôle majeur", "les experts", "de nombreux observateurs".
- Ne pas dire pourquoi un sujet est important : les faits le montrent. Pas de phrase finale "défis et perspectives", pas de conclusion morale.
- Toute affirmation vient d'une source lue pendant l'exécution, listée dans `sources`. Un calcul de la rédaction est signalé dans `note_sources`. Jamais un chiffre, une citation ou une source inventés.
- Pas de ton alarmiste ni promotionnel, pas de superlatif non chiffré. Titres non interrogatifs.

## Phrases

- Chaque phrase a un sujet et un verbe conjugué. Pas de groupe nominal posé comme une phrase ("Trois jours, dix-neuf pays.").
- Longueurs variées : des phrases de 5 mots à côté de phrases de 30. Pas trois phrases de suite qui commencent par le sujet.
- Pas de groupes de trois par réflexe. "Est", "a" plutôt que "constitue", "se positionne comme", "offre".
- Nommer le référent plutôt que l'anaphore vague ("ici", "dans ce cadre"). Répéter un mot plutôt que chercher un synonyme.
- Une énumération se présente en `liste`.

## Typographie

- Jamais de tiret cadratin. Pas de gras dans le texte, pas de majuscules forcées.
- Français : espace avant : ; ? !, guillemets « », 12 500, 3,5 %, 1,5 milliard.
- Mots bannis : plonger, souligner, significatif, crucial, de plus (sauf comparaison chiffrée), clé (figuré), essentiel, méticuleux, paysage (figuré), structurer (figuré), façonner, enrichir, et les autres alertes rouges de l'audit.

## Technique

- Chaque notion technique est définie à sa première apparition, en une phrase concrète ("le cache KV garde en mémoire les calculs déjà faits sur le début du texte, pour ne pas les refaire à chaque mot").
- Un sigle est développé à sa première apparition (HBM, mémoire à haute bande passante).
- Un ordre de grandeur se compare à quelque chose de connu, seulement si la comparaison est juste et sourcée (consommation d'une ville, d'un pays).
- Les termes anglais d'usage restent en anglais quand le français n'est pas employé par le métier (prompt, fine-tuning, benchmark), en italique de sens : pas de guillemets, pas de majuscule.
- Ne pas prêter d'intentions ni de pensée aux modèles ("le modèle comprend", "veut") : dire ce qu'il calcule ou produit.
