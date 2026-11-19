# Marathon Predictor

Projet réalisé par **Olivier Valenciano et Paul-Antoine Pilotte** dans le cadre du cours INF1007 – Programmation à Polytechnique Montréal, automne 2026.

## 1. Description du projet

Marathon Predictor est une application Python permettant de prédire le temps final d'un coureur au marathon à partir de son âge, de son sexe et de ses temps de passage au 5 km, 10 km, 15 km et demi-marathon.

L'application utilise un modèle de régression linéaire entraîné sur des résultats du marathon de Boston de 2021 à 2024.

Une interface graphique développée avec Tkinter permet de saisir les informations du coureur, d'obtenir une prédiction et de consulter un graphique ainsi que l'historique des prédictions.

## 2. Fonctionnalités

L'application permet de :

- Saisir les caractéristiques du coureur et ses temps de passage.
- Valider les données entrées et afficher des messages d'erreur.
- Prédire le temps final au marathon et calculer l'allure moyenne.
- Visualiser les temps de passage et la prédiction avec Matplotlib.
- Enregistrer les prédictions dans un fichier CSV.
- Consulter l'historique des prédictions précédentes.

Les résultats sont des estimations statistiques et ne garantissent pas la performance réelle d'un coureur.

## 3. Jeu de données

Les données proviennent du **CMU Statistics & Data Science Data Repository** de Carnegie Mellon University.

Source : [Boston Marathon times, 2021–2024](https://cmustatistics.github.io/data-repository/sports/boston-marathon.html)

Le fichier utilisé contient **49 000 observations et 7 colonnes** :

| Colonne | Description |
|---|---|
| Age | Âge du coureur |
| M/F | Sexe du coureur |
| 5K, 10K, 15K, HALF | Temps cumulés aux différentes distances |
| Finish Net | Temps final au marathon (variable cible) |

Les temps sont exprimés en secondes.

Les données ont été nettoyées afin de retirer les colonnes inutiles, les informations identifiantes et les observations présentant des valeurs manquantes ou incohérentes.

Le fichier nettoyé est disponible dans `donnees/boston-nettoye.csv` (environ 1,49 Mo).

Le dépôt de Carnegie Mellon rend ces données accessibles, mais aucune licence spécifique autorisant explicitement leur redistribution n'a été identifiée sur la page du jeu de données.

## 4. Modèle de prédiction

Nous utilisons une **régression linéaire** avec scikit-learn. La variable catégorielle M/F est encodée avec `OneHotEncoder`.

Les données sont séparées en deux ensembles : 80 % pour l'entraînement et 20 % pour les tests, avec une graine aléatoire fixe (`random_state=42`).

Nous utilisons principalement l'erreur absolue moyenne (MAE), puisqu'elle permet de mesurer directement l'écart moyen entre le temps prédit et le temps réel, en minutes. Nous calculons également le coefficient de détermination R².

**Résultats obtenus :**

| Métrique | Résultat approximatif |
|---|---:|
| MAE du modèle | 7,31 minutes |
| R² | 0,945 |

Pour évaluer ces résultats, le modèle est comparé à deux références : une prédiction constante basée sur la moyenne des temps d'entraînement et une estimation correspondant à deux fois le temps au demi-marathon.

Le modèle comporte certaines limites : les données proviennent principalement de coureurs qualifiés pour Boston et ne tiennent pas compte de facteurs comme la météo, les blessures ou la fatigue.

## 5. Installation et utilisation

### Installation

Cloner le dépôt GitHub :

```bash
git clone https://github.com/PaPilotte/Inf1007-Projet2.git
cd Inf1007-Projet2
```

Installer les dépendances avec Python :

```bash
python -m pip install -r requirements.txt
```

Tkinter doit également être disponible dans l'installation Python.

### Entraînement

Pour entraîner le modèle à partir du fichier CSV fourni :

```bash
python -m src.entrainement
```

Cette commande entraîne le modèle, calcule les métriques d'évaluation et génère les fichiers nécessaires dans `modeles/`, ainsi que les graphiques d'exploration et d'évaluation dans `graphiques/`.

### Lancement

Pour ouvrir l'interface graphique :

```bash
python -m src.main
```

Il suffit ensuite de saisir les informations du coureur et de cliquer sur le bouton de prédiction. Le modèle sauvegardé est chargé sans nouvel entraînement.

## 6. Organisation du projet

| Module | Rôle |
|---|---|
| `main.py` | Lancement de l'application |
| `donnees.py` | Chargement, nettoyage et validation des données |
| `modele.py` | Évaluation et prédiction |
| `entrainement.py` | Exécution du processus d'entraînement |
| `interface.py` | Interface graphique Tkinter |
| `chronos.py` | Conversion et validation des temps |
| `graphiques.py` | Graphiques Matplotlib |
| `historique.py` | Enregistrement des prédictions |
| `fenetre_historique.py` | Affichage de l'historique |
| `exceptions.py` | Exceptions personnalisées |

Le dossier `tests/` contient les tests automatisés.

Le projet utilise la programmation orientée objet avec les classes `Modele`, `Application`, `Variable`, `VariableNumerique` et `VariableCategorielle`. Il comprend notamment l'héritage, le polymorphisme, la composition et l'encapsulation.

Le module `modele.py` utilise également un **décorateur `@chronometrer`** (chapitre 7) pour mesurer le temps d'exécution de l'entraînement, ainsi que des calculs vectorisés avec NumPy pour les métriques MAE et R².

## 7. Graphiques

Deux types de graphiques sont produits pendant l'entraînement :

- Un graphique d'exploration montrant la relation entre le temps au demi-marathon et le temps final, sauvegardé avec `savefig()`.
- Un graphique comparant les temps prédits et les temps réels.

L'interface permet également d'afficher un graphique Matplotlib présentant les temps de passage et la prédiction finale.

## 8. Tests automatisés

Les tests ont été réalisés avec pytest. Ils couvrent notamment le traitement des données, les calculs, le modèle, les validations, les graphiques et l'interface.

Pour exécuter les tests :

```bash
python -m pytest -q
```

Pour mesurer la couverture :

```bash
python -m pytest --cov=src --cov-report=term-missing
```

**Résultats obtenus le 19 novembre 2026 :**

| Indicateur | Résultat |
|---|---:|
| Tests réussis | 164 / 164 |
| Couverture du code | 98 % |

Les tests sont également exécutés automatiquement avec GitHub Actions à chaque modification envoyée au dépôt.

## 9. Documentation consultée

- [pandas – Documentation officielle](https://pandas.pydata.org/docs/)
- [scikit-learn – Régression linéaire](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LinearRegression.html)
- [Python – Tkinter](https://docs.python.org/3/library/tkinter.html)
- [NumPy – Documentation](https://numpy.org/doc/stable/)
- [Matplotlib – Documentation](https://matplotlib.org/stable/)

## 10. Documents complémentaires

Les fichiers `DECISIONS.md` et `JOURNAL_IA.md` présentent respectivement les choix effectués durant le projet et l'utilisation des outils d'intelligence artificielle.