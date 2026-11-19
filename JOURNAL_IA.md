#Journal IA

| Outil | Demande | Réponse et vérification |
|---|---|---|
| Claude Opus 5.5 | Construire des fonctions de test pour l'extraction et le nettoyage des gonnées | 8 fonctions de test, 2 modifiées pour inclure des cas qui devraient faire des erreurs pour s'assurer que le système lève bien des erreurs. |
| GPT-5 | Vérifier et valider le code du script modele.py | Détection de deux erreurs logiques, une pour la gestion des colonnes et l'autre qui laissait une erreur potentielle dans le R^2. Modifié la gestion des colonnes pour un Pipeline qui convertit M/F en binaire et laisse passer les autres colonnes numériques. |
| Claude | Construire le squelette de l'interface avec tkinter, laisser les fonctions de traitement et de communication vides pour qu'on puisse activer l'interface. | Interface impossible de changer de taille: modification manuelle pour s'adapter à différentes résolutions. |
| Claude Opus 5.5 | Générer des fonctions de test pour le processus d'entrainement et l'interface de base | 32 fonctions de test réparties dans test_entrainement, test_modele, test_interface |
| Claude Opus 5.5 | Évaluer la gestion de l'historique dans l'interface. | Changement: Script dédié historique.py pour gérer la logique derrière le csv et pour éviter d'alourdir le script d'interface. Cela a mené à faire un script dédié pour les graphiques aussi |
| Claude Opus 5.5 | Générer des fonctions de test pour la fonctionnalité du projet complet, vérifier la communication entre les modules et les edge cases | Fonctions de tests réparties dans des fichiers de test_*.py pour couvrir le plus de lignes de code et être safe à chaque push. |
