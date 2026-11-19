
"""Gestion, nettoyage et validation des données de Marathon Predictor."""

import os
import math
from abc import ABC, abstractmethod

import pandas as pd

from src.exceptions import DonneeInvalideError


# --------------------------------------------------
# Chemins et constantes du projet
# --------------------------------------------------

DOSSIER_PROJET = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

CHEMIN_NETTOYE = os.path.join(
    DOSSIER_PROJET,
    "donnees",
    "boston-nettoye.csv"
)

COLONNES_A_GARDER = [
    "Age",
    "M/F",
    "5K",
    "10K",
    "15K",
    "HALF",
    "Finish Net"
]


# --------------------------------------------------
# Classes des variables (POO)
# --------------------------------------------------

class Variable(ABC):
    """Classe parente abstraite représentant une variable du modèle."""

    def __init__(self, nom: str) -> None:
        """Initialise la variable.

        Args:
            nom: Nom de la variable.
        """
        self._nom = nom

    @property
    def nom(self) -> str:
        """Retourne le nom de la variable."""
        return self._nom

    @abstractmethod
    def valider(self, valeur: object) -> float | str:
        """Valide une valeur et retourne sa représentation convertie.

        Args:
            valeur: Valeur à valider.

        Returns:
            Valeur numérique ou catégorielle validée.

        Raises:
            DonneeInvalideError: Si la valeur est invalide.
        """

    def __repr__(self) -> str:
        """Retourne une représentation textuelle de la variable."""
        return f"{type(self).__name__}({self._nom!r})"


class VariableNumerique(Variable):
    """Variable numérique avec un intervalle autorisé."""

    def __init__(
        self, nom: str, minimum: float, maximum: float
    ) -> None:
        """Initialise une variable numérique.

        Args:
            nom: Nom de la variable.
            minimum: Valeur minimale autorisée.
            maximum: Valeur maximale autorisée.

        Raises:
            ValueError: Si le minimum dépasse le maximum.
        """
        super().__init__(nom)

        if minimum > maximum:
            raise ValueError("Intervalle invalide.")

        self._minimum = minimum
        self._maximum = maximum

    def valider(self, valeur: object) -> float:
        """Convertit la valeur en nombre et vérifie son intervalle.

        Args:
            valeur: Valeur à convertir et à valider.

        Returns:
            Valeur numérique convertie en float.

        Raises:
            DonneeInvalideError: Si la valeur n'est pas numérique,
                n'est pas finie ou est hors de l'intervalle.
        """
        try:
            nombre = float(valeur)
        except (TypeError, ValueError) as erreur:
            raise DonneeInvalideError(
                f"{self._nom} doit être un nombre."
            ) from erreur

        if not math.isfinite(nombre):
            raise DonneeInvalideError(
                f"{self._nom} doit être un nombre fini."
            )

        if not self._minimum <= nombre <= self._maximum:
            raise DonneeInvalideError(
                f"{self._nom} doit être entre "
                f"{self._minimum} et {self._maximum}."
            )

        return nombre


class VariableCategorielle(Variable):
    """Variable dont la valeur appartient à des catégories autorisées."""

    def __init__(self, nom: str, categories: list[str]) -> None:
        """Initialise une variable catégorielle.

        Args:
            nom: Nom de la variable.
            categories: Liste des catégories autorisées.

        Raises:
            ValueError: Si la liste des catégories est vide.
        """
        super().__init__(nom)

        if not categories:
            raise ValueError("La liste des catégories est vide.")

        self._categories = list(categories)

    def valider(self, valeur: object) -> str:
        """Vérifie que la valeur appartient aux catégories autorisées.

        Args:
            valeur: Catégorie à vérifier.

        Returns:
            Catégorie validée.

        Raises:
            DonneeInvalideError: Si la catégorie est invalide.
        """
        if valeur not in self._categories:
            raise DonneeInvalideError(
                f"{self._nom} doit être parmi : "
                f"{', '.join(self._categories)}."
            )

        return valeur


# --------------------------------------------------
# Chargement des données
# --------------------------------------------------

def charger_donnees(chemin: str) -> pd.DataFrame:
    """Charge un fichier CSV.

    Args:
        chemin: Chemin vers le fichier CSV.

    Returns:
        DataFrame contenant les données.

    Raises:
        FileNotFoundError: Si le fichier n'existe pas.
    """
    if not os.path.exists(chemin):
        raise FileNotFoundError(
            f"Fichier introuvable : {chemin}"
        )

    return pd.read_csv(chemin)


# --------------------------------------------------
# Nettoyage des données
# --------------------------------------------------

def nettoyer_donnees(df: pd.DataFrame) -> pd.DataFrame:
    """Sélectionne les colonnes utiles et conserve les catégories M et F.

    Args:
        df: Données originales.

    Returns:
        DataFrame contenant uniquement les colonnes sélectionnées
        et les observations des catégories M et F.

    Raises:
        ValueError: Si une colonne requise est manquante.
    """
    colonnes_manquantes = [
        colonne for colonne in COLONNES_A_GARDER
        if colonne not in df.columns
    ]

    if colonnes_manquantes:
        raise ValueError(
            f"Colonnes manquantes : {colonnes_manquantes}"
        )

    df_nettoye = df[COLONNES_A_GARDER].copy()

    df_nettoye = df_nettoye[
        df_nettoye["M/F"].isin(["M", "F"])
    ].copy()

    return df_nettoye


# --------------------------------------------------
# Vérification des temps
# --------------------------------------------------

def verifier_temps(df: pd.DataFrame) -> pd.DataFrame:
    """Repère les observations aux temps incohérents.

    Args:
        df: Données contenant les temps de passage des coureurs.

    Returns:
        DataFrame contenant les observations dont les temps sont
        non positifs ou non strictement croissants.
    """
    invalides = df[
        (df["5K"] <= 0) |
        (df["5K"] >= df["10K"]) |
        (df["10K"] >= df["15K"]) |
        (df["15K"] >= df["HALF"]) |
        (df["HALF"] >= df["Finish Net"])
    ]

    return invalides


# --------------------------------------------------
# Échantillonnage des données
# --------------------------------------------------

def echantillonner_donnees(
    df: pd.DataFrame,
    nombre: int = 49000,
    graine: int = 42
) -> pd.DataFrame:
    """Sélectionne un échantillon aléatoire reproductible.

    Args:
        df: Données à échantillonner.
        nombre: Nombre de lignes souhaité.
        graine: Graine aléatoire.

    Returns:
        DataFrame échantillonné avec un index réinitialisé.

    Raises:
        ValueError: Si le nombre demandé est invalide.
    """
    if nombre <= 0 or nombre > len(df):
        raise ValueError(
            "Nombre d'observations invalide."
        )

    return df.sample(
        n=nombre,
        random_state=graine
    ).reset_index(drop=True)


# --------------------------------------------------
# Sauvegarde des données
# --------------------------------------------------

def sauvegarder_donnees(
    df: pd.DataFrame,
    chemin: str
) -> None:
    """Sauvegarde un DataFrame au format CSV.

    Args:
        df: Données à sauvegarder.
        chemin: Destination du fichier CSV.

    Returns:
        None. Le résultat est écrit dans un fichier CSV.
    """
    df.to_csv(chemin, index=False)


# --------------------------------------------------
# Vérification du jeu de données nettoyé
# --------------------------------------------------

def main() -> None:
    """Charge et vérifie le fichier Boston nettoyé.

    Vérifie les colonnes, les valeurs manquantes, les temps,
    les catégories et le nombre d'observations.

    Returns:
        None. Les résultats sont affichés dans le terminal.

    Raises:
        FileNotFoundError: Si le fichier nettoyé est absent.
        ValueError: Si les données ne respectent pas les critères.
    """

    # 1. Charger les données nettoyées
    df = charger_donnees(CHEMIN_NETTOYE)

    print("=== DONNÉES NETTOYÉES ===")
    print("Dimensions :", df.shape)

    # 2. Vérifier les colonnes
    if list(df.columns) != COLONNES_A_GARDER:
        raise ValueError(
            "Les colonnes du CSV sont incorrectes."
        )

    # 3. Vérifier les valeurs manquantes
    valeurs_manquantes = df.isna().sum().sum()

    print("Valeurs manquantes :", valeurs_manquantes)

    if valeurs_manquantes > 0:
        raise ValueError(
            "Le fichier contient des valeurs manquantes."
        )

    # 4. Vérifier la cohérence des temps
    invalides = verifier_temps(df)

    print("Temps incohérents :", len(invalides))

    if not invalides.empty:
        raise ValueError(
            "Le fichier contient des temps incohérents."
        )

    # 5. Vérifier les catégories M/F
    if not df["M/F"].isin(["M", "F"]).all():
        raise ValueError(
            "Le fichier contient une catégorie M/F invalide."
        )

    # 6. Vérifier le nombre d'observations
    if len(df) != 49000:
        raise ValueError(
            "Le fichier doit contenir 49 000 observations."
        )

    # 7. Afficher les statistiques
    print("\n=== ÉCHANTILLON FINAL ===")
    print("Dimensions :", df.shape)

    print("\nRépartition H/F :")
    print(df["M/F"].value_counts())

    print("\nStatistiques des temps :")
    print(df["Finish Net"].describe())

    print("\n=== VÉRIFICATION TERMINÉE ===")
    print("Fichier vérifié avec succès!")


if __name__ == "__main__":
    main()
