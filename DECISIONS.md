#Decisions
| Choix | Options envisagées | Choix retenu et justification |
|---|---|---|
| Domaine | Sport, santé, finance | Course à pied : problème concret, intérêt personnel et résultats mesurables. |
| Objectif | Prédire un temps, proposer une distance à courir | Prédire le temps final au marathon pour fournir une estimation individuelle lors d'une course. |
| Type de problème | Régression, classification | Régression supervisée : la cible est un temps connu dans les données. |
| Jeu de données | Résultats de différentes courses, données simulées | Données du marathon de Boston : présence des temps intermédiaires et finaux. |
| Fichier de travail | Données brutes, fichier préparé | boston-nettoye.csv : centraliser les données prêtes à utiliser. Les données sont anonymisées dans le github. |
| Taille des données | Toutes les observations, échantillon | 49 000 observations : volume fixé et entrées sélectionnées aléatoirement par le programme. |
| Échantillonnage | Premières lignes, sélection aléatoire | Échantillon aléatoire avec graine 42 : sélection reproductible pour tests. |
| Cible | Temps brut, temps net, allure | Finish Net : prédire le temps net final du coureur: facile à vérifier pour la précision. |
| Unité des calculs | Heures, minutes, secondes | Secondes : calculs et comparaisons dans une unité commune. |
| Structure des données | Listes, dictionnaires, tableaux | DataFrame pandas : manipuler les colonnes nommées du CSV. |
| Colonnes manquantes | Ignorer, compléter, refuser | Refuser : les variables requises sont nécessaires au fonctionnement. |
| Vérification du fichier final | Contrôle visuel, contrôles programmés | Vérifier automatiquement les colonnes, valeurs manquantes, temps, catégories et effectif. |
| Export des données | CSV avec index, CSV sans index | CSV sans index : éviter une colonne technique supplémentaire. |
| Modèle prédictif | Règle fixe, régression linéaire, modèle complexe | Régression linéaire : solution lisible et adaptée à une cible numérique. La vitesse du coureur n'est pas constante durant le marathon, alors nous pensons qu'une régression linéaire sera plus précise d'une simple proportion. |
| Encodage de M/F | Texte brut, codage numérique | OneHotEncoder : convertir la catégorie pour la régression. |
| Métrique principale | MAE, MSE, RMSE | MAE en secondes : erreur moyenne facile à interpréter. |
| Métrique complémentaire | Aucune, R² | R² : compléter la MAE par une mesure de la variance facilement interprétable. |
| Mesure des performances techniques | Aucune, chronométrage | Décorateur chronometrer : afficher la durée de l’entraînement. |
| Données transmises à la prédiction | Liste positionnelle, dictionnaire | Dictionnaire nommé : identifier clairement chaque caractéristique. |
| Résultats d’évaluation | Accès direct, copie | Retourner une copie du dictionnaire : protéger l’état interne. |
| Technologie d’interface | Tkinter, PyQt ou PySide, Streamlit, Gradio | Tkinter et ttk : interface de bureau intégrée à Python. Standard parce qu'on n'a pas besoin d'une interface précise ou particulièrement belle, générique suffit. |
| Adaptation à l’écran | Dimensions fixes, dimensions ajustées | Échelle selon la résolution, bornée de 0,80 à 1,35 : améliorer la lisibilité. |
| Saisie de l’âge | Texte libre, menu déroulant | Menu en lecture seule : limiter les saisies aux âges autorisés. |
| Bornes de l’âge | Bornes arbitraires, bornes des données | Intervalles des métadonnées : rester dans les âges observés. |
| Saisie de M/F | Texte libre, sélection | Menu en lecture seule : éviter les catégories non reconnues. |
| Saisie des temps | Secondes brutes, texte libre, champs séparés | Heures/minutes/secondes : saisie plus naturelle pour l’utilisateur. |
| Affichage du temps final | Nombre brut, durée formatée | convertir_temps() : présenter une durée lisible. |
| Information complémentaire | Temps seul, temps et allure | Afficher aussi l’allure moyenne : faciliter l’interprétation sportive. |
| Organisation des graphiques | Tout dans interface.py, module spécialisé | graphiques.py : isoler la construction et l’affichage du graphique. |
| Activation du graphique | Affichage automatique, bouton | Bouton dédié : laisser l’utilisateur choisir le moment de consultation. |
| Architecture générale | Script unique, modules spécialisés | Séparer données, chronos, modèle, entraînement, interface, historique et graphiques. |
