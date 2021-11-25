
# HowLongToBeat Scraper

 Un web scraper qui parcourt HowLongToBeat pour extraire des données sur le temps de jeu et d'achèvement.

## But

HowLongToBeat (HLTB) est un excellent site Web qui permet de découvrir le temps que mettent les gens pour terminer un jeu. Bien qu'il regorge de données, il manque malheureusement une API. Ce projet extrait tous les jeux connus (au moment de l'écriture) sur le site Web, en extrayant les données du jeu ainsi que toutes les entrées d'achèvement existantes.




## Fonctionnement

Le `HLTB_Game_Spider` dans `hltb-game.py` récupère tous les jeux disponibles via la fonctionnalité de recherche du site web. Le `HLTB_Completions_Spider` dans `hltb-completions.py` récupère toutes les entrées d'achèvement soumises par les utilisateurs pour chaque jeu (certains n'ont pas d'entrées et seront donc manquants).

`HLTB_Game_Spider` extrait les colonnes (après le nettoyage) :

-`id` - ID du jeu du site

-`title` - Nom du jeu

-`main_story` - Temps moyen d'achèvement de la "Main Story" en heures.

-`main_plus_extras` - Temps de réalisation moyen de "Main + Extras" en heures.

-`completionist` - Temps moyen d'achèvement des travaux par les "complétistes", en heures.

-`all_styles` - Temps de réalisation moyen de "Tous les styles" en heures.

-`coop` - Temps moyen d'achèvement du "Co-Op" en heures.

-`versus` - Temps de réalisation moyen de "Vs." en heures.

-`type` - Tapez entrez pour différencier`DLC/Expansion`, `Mod`, `ROM` et `Hack` des jeux ordinaires.

-`developers` - Liste de tous les développeurs.

-`publishers` - Liste de tous les éditeurs.

-`platforms` - Liste de toutes les plateformes.

-`genres` - Liste de tous les genres.

-`release_na` - Date de sortie en Amérique (si disponible).

-`release_eu` - Date de sortie en Europe (si disponible).

-`release-jp` - Date de sortie au Japon (si disponible).

`HLTB_Completions_Spider` extrait les colones :

-`id` - ID du jeu qui peut être croisé avec l'ensemble de données ci-dessus.

-`type`- Type d'entrée d'achèvement(`Main Story`, `Main + Extras`, `Completionists`, `Co-Op Multiplayer`, `Speed Run - Any%`, `Speed Run - 100%`)

-`platforms` - Plate-forme sur laquelle l'entrée particulière a été effectuée.

`time` - Heure de la saisie en heures et minutes (par exemple, `2h50m`).