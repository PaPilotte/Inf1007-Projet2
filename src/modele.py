
"""Entraînement, évaluation, prédiction et sauvegarde du modèle."""

import json
import os
import time
from functools import wraps
from typing import Callable

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from src.exceptions import DonneeInvalideError, ModeleNonEntraineError

# Chemins et constantes
DOSSIER_PROJET = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOSSIER_MODELES = os.path.join(DOSSIER_PROJET, "modeles")
CHEMIN_MODELE = os.path.join(DOSSIER_MODELES, "modele.joblib")
CHEMIN_METADONNEES = os.path.join(DOSSIER_MODELES, "metadonnees.json")

COLONNES_NUMERIQUES = ["Age", "5K", "10K", "15K", "HALF"]
COLONNE_CATEGORIELLE = "M/F"
CATEGORIES_GENRE = ["M", "F"]
COLONNES_ENTREE = ["Age", "M/F", "5K", "10K", "15K", "HALF"]
COLONNE_CIBLE = "Finish Net"


# ---------- Outil du chapitre 7 : décorateur ----------

def chronometrer(fonction: Callable) -> Callable:
    """Décorateur qui affiche le temps d'exécution de la fonction décorée.

    Args:
        fonction: fonction à chronométrer.

    Returns:
        Une nouvelle fonction qui fait le même travail et affiche sa durée.
    """
    @wraps(fonction)  # conserve le nom et la docstring d'origine
    def enveloppe(*args, **kwargs):
        debut = time.perf_counter()
        resultat = fonction(*args, **kwargs)
        duree = time.perf_counter() - debut
        print(f"[{fonction.__name__}] terminé en {duree:.2f} s")
        return resultat
    return enveloppe


# ---------- Chapitre 12 : métriques vectorisées avec NumPy ----------

def _valider_tableaux(y_reel, y_predit) -> tuple[np.ndarray, np.ndarray]:
    """Convertit en tableaux NumPy et vérifie qu'ils sont compatibles.

    Raises:
        DonneeInvalideError: si les tailles diffèrent ou si les tableaux sont vides.
    """
    y_reel = np.asarray(y_reel, dtype=float)
    y_predit = np.asarray(y_predit, dtype=float)
    if y_reel.shape != y_predit.shape or y_reel.size == 0:
        raise DonneeInvalideError(
            "Les tableaux doivent avoir la même taille et ne pas être vides."
        )
    return y_reel, y_predit


def calculer_mae(y_reel, y_predit) -> float:
    """Erreur absolue moyenne (même unité que la cible : secondes).

    Args:
        y_reel: valeurs réelles.
        y_predit: valeurs prédites, de même longueur.

    Returns:
        La MAE (float >= 0).

    Raises:
        DonneeInvalideError: si les tableaux sont vides ou de tailles différentes.
    """
    y_reel, y_predit = _valider_tableaux(y_reel, y_predit)
    return float(np.mean(np.abs(y_reel - y_predit)))


def calculer_r2(y_reel, y_predit) -> float:
    """Coefficient de détermination R² (1 = parfait, 0 = pas mieux que la moyenne).

    Raises:
        DonneeInvalideError: tableaux invalides ou cible constante (R² indéfini).
    """
    y_reel, y_predit = _valider_tableaux(y_reel, y_predit)
    somme_residus = np.sum((y_reel - y_predit) ** 2)
    somme_totale = np.sum((y_reel - np.mean(y_reel)) ** 2)
    if somme_totale == 0:
        raise DonneeInvalideError("R² indéfini : la cible est constante.")
    return float(1 - somme_residus / somme_totale)


# ---------- Chapitres 9 à 11 : la classe Modele ----------

class Modele:
    """Régression linéaire qui prédit le temps final d'un marathon (secondes)."""

    def __init__(self, graine: int = 42, taille_test: float = 0.2) -> None:
        """Crée un modèle non entraîné.

        Args:
            graine: graine aléatoire (résultats reproductibles).
            taille_test: proportion des données réservée au test.
        """
        self._graine = graine
        self._taille_test = taille_test
        self._pipeline = self._construire_pipeline()
        self._est_entraine = False
        self._resultats: dict = {}
        self._y_test: np.ndarray | None = None
        self._predictions: np.ndarray | None = None

    @staticmethod
    def _construire_pipeline() -> Pipeline:
        """Encode M/F en 0/1, laisse passer les colonnes numériques, puis régresse."""
        preparation = ColumnTransformer(
            [("genre", OneHotEncoder(drop="if_binary"), [COLONNE_CATEGORIELLE])],
            remainder="passthrough",
        )
        return Pipeline([
            ("preparation", preparation),
            ("regression", LinearRegression()),
        ])

    @chronometrer
    def entrainer(self, df: pd.DataFrame) -> dict:
        """Sépare les données, calcule les références, entraîne et évalue.

        Args:
            df: données nettoyées contenant les colonnes d'entrée et la cible.

        Returns:
            Dictionnaire des métriques du modèle et des références.

        Raises:
            DonneeInvalideError: si une colonne requise est absente.
        """
        requises = COLONNES_ENTREE + [COLONNE_CIBLE]
        manquantes = [c for c in requises if c not in df.columns]
        if manquantes:
            raise DonneeInvalideError(f"Colonnes manquantes : {manquantes}")

        X, y = df[COLONNES_ENTREE], df[COLONNE_CIBLE]
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=self._taille_test, random_state=self._graine
        )

        # Référence 1 : toujours prédire la moyenne d'entraînement
        reference = DummyRegressor(strategy="mean").fit(X_train, y_train)
        mae_moyenne = calculer_mae(y_test, reference.predict(X_test))
        # Référence 2 : règle naïve « temps final = 2 x HALF »
        mae_naive = calculer_mae(y_test, 2 * X_test["HALF"].to_numpy())

        # Entraînement sur train, évaluation sur test uniquement
        self._pipeline.fit(X_train, y_train)
        self._est_entraine = True
        predictions = self._pipeline.predict(X_test)

        self._y_test = y_test.to_numpy()
        self._predictions = predictions
        self._resultats = {
            "mae_modele": calculer_mae(y_test, predictions),
            "r2_modele": calculer_r2(y_test, predictions),
            "mae_reference_moyenne": mae_moyenne,
            "mae_reference_naive": mae_naive,
            "taille_entrainement": int(len(X_train)),
            "taille_test": int(len(X_test)),
        }
        return self.resultats

    def predire(self, caracteristiques: dict) -> float:
        """Prédit le temps final (secondes) d'un coureur.

        Args:
            caracteristiques: ex. {"Age": 30, "M/F": "F", "5K": 1500, ...}

        Returns:
            Temps final prédit, en secondes.

        Raises:
            ModeleNonEntraineError: si le modèle n'est ni entraîné ni chargé.
            DonneeInvalideError: caractéristique manquante, non numérique ou genre invalide.
        """
        if not self._est_entraine:
            raise ModeleNonEntraineError("Entraînez ou chargez le modèle d'abord.")

        manquantes = [c for c in COLONNES_ENTREE if c not in caracteristiques]
        if manquantes:
            raise DonneeInvalideError(f"Caractéristiques manquantes : {manquantes}")

        if caracteristiques[COLONNE_CATEGORIELLE] not in CATEGORIES_GENRE:
            raise DonneeInvalideError(f"Genre invalide : choisir parmi {CATEGORIES_GENRE}.")

        ligne = {COLONNE_CATEGORIELLE: caracteristiques[COLONNE_CATEGORIELLE]}
        for colonne in COLONNES_NUMERIQUES:
            try:
                ligne[colonne] = float(caracteristiques[colonne])
            except (TypeError, ValueError) as erreur:
                raise DonneeInvalideError(
                    f"La valeur de « {colonne} » doit être un nombre."
                ) from erreur

        df_ligne = pd.DataFrame([ligne])[COLONNES_ENTREE]
        return float(self._pipeline.predict(df_ligne)[0])

    def donnees_test(self) -> tuple[np.ndarray, np.ndarray]:
        """Renvoie (valeurs réelles, prédictions) du jeu de test.

        Raises:
            ModeleNonEntraineError: si entrainer() n'a pas été appelé.
        """
        if self._y_test is None or self._predictions is None:
            raise ModeleNonEntraineError("Aucun jeu de test : appelez entrainer().")
        return self._y_test, self._predictions

    def sauvegarder(self, chemin_modele: str, chemin_meta: str, df: pd.DataFrame) -> None:
        """Enregistre le pipeline (joblib) et les métadonnées (JSON).

        Args:
            chemin_modele: destination du fichier .joblib.
            chemin_meta: destination du fichier .json.
            df: données ayant servi à calculer les intervalles des variables.

        Raises:
            ModeleNonEntraineError: si le modèle n'est pas entraîné.
        """
        if not self._est_entraine:
            raise ModeleNonEntraineError("Rien à sauvegarder : modèle non entraîné.")

        for chemin in (chemin_modele, chemin_meta):
            dossier = os.path.dirname(chemin)
            if dossier:
                os.makedirs(dossier, exist_ok=True)

        joblib.dump(self._pipeline, chemin_modele)

        metadonnees = {
            "colonnes": COLONNES_ENTREE,
            "cible": COLONNE_CIBLE,
            "categories": {COLONNE_CATEGORIELLE: CATEGORIES_GENRE},
            "intervalles": {
                col: [float(df[col].min()), float(df[col].max())]
                for col in COLONNES_NUMERIQUES
            },
            "metriques": self._resultats,
        }
        with open(chemin_meta, "w", encoding="utf-8") as fichier:
            json.dump(metadonnees, fichier, indent=2, ensure_ascii=False)

    @classmethod
    def charger(cls, chemin_modele: str) -> "Modele":
        """Recharge un modèle sauvegardé, sans ré-entraînement.

        Raises:
            FileNotFoundError: si le fichier n'existe pas.
        """
        if not os.path.exists(chemin_modele):
            raise FileNotFoundError(f"Modèle introuvable : {chemin_modele}")
        modele = cls()
        modele._pipeline = joblib.load(chemin_modele)
        modele._est_entraine = True
        return modele

    @property
    def resultats(self) -> dict:
        """Copie des métriques (la copie protège l'état interne)."""
        return dict(self._resultats)

    @property
    def est_entraine(self) -> bool:
        """Indique si le modèle peut prédire."""
        return self._est_entraine

    def __repr__(self) -> str:
        etat = "entraîné" if self._est_entraine else "non entraîné"
        return f"Modele(regression_lineaire, {etat})"